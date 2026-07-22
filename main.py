import os
import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from reporter.config import ACCOUNTS, FREQ_GREEN, FREQ_YELLOW
from reporter.meta_api import fetch_campaigns
from reporter.formatters import fmt_money, fmt_int, fmt_pct, fmt_wow, freq_flag
from reporter.slack_sender import send_reports


# ── Fixed period presets ──────────────────────────────────────────────────────
# The dashboard is a static site, so it can only show ranges we pull ahead of
# time. Each preset is a REAL Meta query over its own date range — that keeps
# reach/frequency correct (reach is not additive across days, so we can never
# just sum daily files). Every preset also carries an equivalent "prev" range
# so the dashboard can show "vs kỳ trước" deltas.

PERIODS = [
    ("yesterday",  "Yesterday"),
    ("this_week",  "This week"),
    ("last_week",  "Last week"),
    ("last_7d",    "Last 7 days"),
    ("last_30d",   "Last 30 days"),
    ("this_month", "This month"),
    ("last_month", "Last month"),
]
PERIOD_LABEL = dict(PERIODS)

# Which preset drives the Slack production report + insights (weekly cadence).
SLACK_PERIOD = "last_week"


def _month_bounds(year: int, month: int):
    first = date(year, month, 1)
    nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return first, nxt - timedelta(days=1)


def _prev_month(first_of_month: date):
    y = first_of_month.year if first_of_month.month > 1 else first_of_month.year - 1
    m = first_of_month.month - 1 or 12
    return _month_bounds(y, m)


def compute_periods(today: date = None) -> dict:
    """Return {key: {"cur": (since, until), "prev": (since, until)}} as dates.

    "Today" is treated as incomplete, so week/month-to-date ranges end at
    yesterday. Each preset's prev is the immediately preceding equal-length
    window for WoW-style comparison.
    """
    today = today or date.today()
    y = today - timedelta(days=1)  # yesterday (last complete day)
    r = {}

    # Yesterday
    r["yesterday"] = {
        "cur":  (y, y),
        "prev": (y - timedelta(days=1), y - timedelta(days=1)),
    }

    # This week: Monday → yesterday.  prev = same span in last week.
    mon_this = today - timedelta(days=today.weekday())
    mon_last = mon_this - timedelta(days=7)
    tw_until = max(y, mon_this)
    span = (tw_until - mon_this).days
    r["this_week"] = {
        "cur":  (mon_this, tw_until),
        "prev": (mon_last, mon_last + timedelta(days=span)),
    }

    # Last week: Monday → Sunday.  prev = the week before.
    sun_last = mon_this - timedelta(days=1)
    r["last_week"] = {
        "cur":  (mon_last, sun_last),
        "prev": (mon_last - timedelta(days=7), sun_last - timedelta(days=7)),
    }

    # Last 7 days (ending yesterday)
    l7 = y - timedelta(days=6)
    r["last_7d"] = {
        "cur":  (l7, y),
        "prev": (l7 - timedelta(days=7), y - timedelta(days=7)),
    }

    # Last 30 days (ending yesterday)
    l30 = y - timedelta(days=29)
    r["last_30d"] = {
        "cur":  (l30, y),
        "prev": (l30 - timedelta(days=30), y - timedelta(days=30)),
    }

    # This month: 1st → yesterday.  prev = same day-span in last month.
    first_this = today.replace(day=1)
    tm_until = max(y, first_this)
    mspan = (tm_until - first_this).days
    first_prev, last_prev = _prev_month(first_this)
    r["this_month"] = {
        "cur":  (first_this, tm_until),
        "prev": (first_prev, min(first_prev + timedelta(days=mspan), last_prev)),
    }

    # Last month: full previous month.  prev = the month before that.
    first_pp, last_pp = _prev_month(first_prev)
    r["last_month"] = {
        "cur":  (first_prev, last_prev),
        "prev": (first_pp, last_pp),
    }

    return r


def range_label(since: date, until: date) -> str:
    if since == until:
        return since.strftime("%b %-d, %Y")
    if since.year == until.year and since.month == until.month:
        return f"{since.strftime('%b')} {since.day}–{until.day}, {until.year}"
    if since.year == until.year:
        return f"{since.strftime('%b %-d')} – {until.strftime('%b %-d')}, {until.year}"
    return f"{since.strftime('%b %-d, %Y')} – {until.strftime('%b %-d, %Y')}"


# ── Data pull ─────────────────────────────────────────────────────────────────

def pull_all(periods: dict) -> dict:
    """Pull every (preset, cur/prev, group, account). Key = (pkey, which, group, acct)."""
    tasks = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for pkey, r in periods.items():
            for which in ("cur", "prev"):
                if which not in r:
                    continue
                since, until = r[which]
                s, u = since.isoformat(), until.isoformat()
                for group, accounts in ACCOUNTS.items():
                    for acct_name, acct_id in accounts.items():
                        tasks[(pkey, which, group, acct_name)] = ex.submit(
                            fetch_campaigns, acct_id, s, u
                        )

    results = {}
    for key, future in tasks.items():
        try:
            results[key] = future.result()
        except Exception as e:
            print(f"Error pulling {key}: {e}")
            results[key] = []
    return results


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate(campaigns: list) -> dict:
    spend        = sum(c["spend"] for c in campaigns)
    qe           = sum(c["qe"] for c in campaigns)
    reach        = sum(c["reach"] for c in campaigns)
    installs     = sum(c["installs"] for c in campaigns)
    inst_spend   = sum(c["spend"] for c in campaigns if c["is_install"])
    active_camps = sum(1 for c in campaigns if c["spend"] > 0)
    red_freq     = sum(1 for c in campaigns if c["frequency"] >= FREQ_YELLOW)
    return {
        "spend":    spend,
        "qe":       qe,
        "reach":    reach,
        "er":       (qe / reach * 100) if reach > 0 else 0.0,
        "cpe":      (spend / qe) if qe > 0 else 0.0,
        "installs": installs,
        "cpi":      (inst_spend / installs) if installs > 0 else 0.0,
        "active_camps":   active_camps,
        "red_freq_camps": red_freq,
        "campaigns": campaigns,
    }


def build_simple_groups(results: dict, pkey: str, which: str) -> dict:
    """Group-level aggregate (old shape, keeps `campaigns`) — used by Slack/insights."""
    groups = {}
    for group_name in ACCOUNTS:
        camps = []
        for acct_name in ACCOUNTS[group_name]:
            camps += results.get((pkey, which, group_name, acct_name), [])
        groups[group_name] = aggregate(camps)
    return groups


# ── Frequency watch list ──────────────────────────────────────────────────────

def build_watch_list_for(results: dict, pkey: str) -> list:
    items = []
    for group_name in ACCOUNTS:
        for acct_name in ACCOUNTS[group_name]:
            for c in results.get((pkey, "cur", group_name, acct_name), []):
                if c["frequency"] >= FREQ_GREEN:
                    items.append({
                        "name":      c["name"],
                        "account":   acct_name,
                        "group":     group_name,
                        "frequency": c["frequency"],
                        "reach":     c["reach"],
                        "flag":      freq_flag(c["frequency"]),
                        "spend":     c["spend"],
                    })
    items.sort(key=lambda x: x["frequency"], reverse=True)
    return items[:8]


# ── Key insights ──────────────────────────────────────────────────────────────

def generate_insights(groups_cur: dict, groups_prev: dict) -> list:
    insights = []
    for name in ("BRAND", "GROWTH", "VERTICAL"):
        w1 = groups_cur[name]
        w2 = groups_prev[name]

        if w2["spend"] > 0:
            pct = (w1["spend"] - w2["spend"]) / w2["spend"] * 100
            if abs(pct) >= 20:
                direction = "tăng" if pct > 0 else "giảm"
                insights.append(
                    f"{name}: Spend {direction} {abs(pct):.1f}% WoW "
                    f"(SGD {fmt_money(w1['spend'])} vs SGD {fmt_money(w2['spend'])})"
                )

        if w2["er"] > 0:
            pp = w1["er"] - w2["er"]
            if abs(pp) >= 0.5:
                direction = "cải thiện" if pp > 0 else "giảm"
                insights.append(
                    f"{name}: ER {direction} {abs(pp):.2f}pp WoW "
                    f"({fmt_pct(w1['er'])} vs {fmt_pct(w2['er'])})"
                )

        if name == "GROWTH":
            i1, i2 = w1.get("installs", 0), w2.get("installs", 0)
            if i1 > 0 or i2 > 0:
                insights.append(
                    f"GROWTH: {fmt_int(i1)} installs ({fmt_wow(i1, i2)} WoW), "
                    f"CPI SGD {fmt_money(w1['cpi'])}"
                )

    high_freq = sum(
        1 for name in ("BRAND", "GROWTH", "VERTICAL")
        for c in groups_cur[name].get("campaigns", [])
        if c["frequency"] >= FREQ_YELLOW
    )
    if high_freq:
        insights.append(
            f"⚠️ {high_freq} campaign(s) đang ở mức Freq ≥7× — cần cân nhắc refresh creative"
        )

    return insights[:5]


# ── Snapshot builders (for GitHub Pages dashboard) ────────────────────────────

def _campaign_out(c: dict) -> dict:
    """Per-campaign row the dashboard renders (superset for all tab types)."""
    return {
        "name":        c.get("name", ""),
        "spend":       round(c.get("spend", 0), 2),
        "reach":       int(c.get("reach", 0)),
        "impressions": int(c.get("impressions", 0)),
        "freq":        round(c.get("frequency", 0), 2),
        "clicks":      int(c.get("clicks", 0)),
        "cpc":         round(c.get("cpc", 0), 4),
        "ctr":         round(c.get("ctr", 0), 4),
        "qe":          int(c.get("qe", 0)),
        "cpe":         round(c.get("cpe", 0), 2),
        "er":          round(c.get("er", 0), 4),
        "link_clicks": int(c.get("link_clicks", 0)),
        "installs":    int(c.get("installs", 0)),
        "is_install":  bool(c.get("is_install", False)),
        "is_active":   bool(c.get("is_active", False)),
    }


def _aggregate_detail(camps: list) -> dict:
    """Aggregate metrics for an account or group, incl. weighted avg_freq."""
    spend      = sum(c.get("spend", 0) for c in camps)
    reach      = sum(c.get("reach", 0) for c in camps)
    impr       = sum(c.get("impressions", 0) for c in camps)
    qe         = sum(c.get("qe", 0) for c in camps)
    lc         = sum(c.get("link_clicks", 0) for c in camps)
    clicks     = sum(c.get("clicks", 0) for c in camps)
    installs   = sum(c.get("installs", 0) for c in camps)
    inst_spend = sum(c.get("spend", 0) for c in camps if c.get("is_install"))
    return {
        "spend":          round(spend, 2),
        "reach":          int(reach),
        "impressions":    int(impr),
        "clicks":         int(clicks),
        "avg_freq":       round(impr / reach, 2) if reach else 0.0,
        "qe":             int(qe),
        "cpe":            round(spend / qe, 2) if qe else 0.0,
        "er":             round(qe / reach * 100, 4) if reach else 0.0,
        "link_clicks":    int(lc),
        "cpl":            round(spend / qe, 2) if qe else 0.0,
        "installs":       int(installs),
        "cpi":            round(inst_spend / installs, 2) if installs else 0.0,
        "active_camps":   sum(1 for c in camps if c.get("spend", 0) > 0),
        "red_freq_camps": sum(1 for c in camps if c.get("frequency", 0) >= FREQ_YELLOW),
    }


def build_detail_groups(results: dict, pkey: str, which: str, with_campaigns: bool = True) -> dict:
    """group → (metrics + accounts → (metrics + campaigns[])) for the dashboard.

    `prev` snapshots pass with_campaigns=False (they only feed WoW deltas, so
    campaign rows / per-account breakdown are dropped to keep files small)."""
    groups = {}
    for group_name in ACCOUNTS:
        all_camps = []
        accounts = {}
        for acct_name in ACCOUNTS[group_name]:
            camps = results.get((pkey, which, group_name, acct_name), [])
            all_camps += camps
            if with_campaigns:
                acct = _aggregate_detail(camps)
                acct["campaigns"] = [_campaign_out(c) for c in camps]
                accounts[acct_name] = acct
        group = _aggregate_detail(all_camps)
        if with_campaigns:
            group["accounts"] = accounts
        groups[group_name] = group
    return groups


def save_period_snapshots(results: dict, periods: dict) -> None:
    """Write one JSON per preset + an index.json listing presets in display order."""
    data_dir = Path(__file__).parent / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    index = []

    for pkey, plabel in PERIODS:
        r = periods.get(pkey)
        if not r:
            continue
        since, until = r["cur"]
        groups = build_detail_groups(results, pkey, "cur", with_campaigns=True)
        total_spend = sum(g["spend"] for g in groups.values())

        snapshot = {
            "key":              pkey,
            "period_label":     plabel,
            "week_label":       range_label(since, until),   # reused by dashboard render fns
            "since":            since.isoformat(),
            "until":            until.isoformat(),
            "week_start":       since.isoformat(),
            "total_spend":      round(total_spend, 2),
            "generated_at":     generated_at,
            "detail_available": True,
            "groups":           groups,
            "watch_list": [
                {
                    "name":      item["name"],
                    "account":   item["account"],
                    "group":     item.get("group", ""),
                    "frequency": round(item["frequency"], 2),
                    "reach":     int(item.get("reach", 0)),
                    "spend":     round(item["spend"], 2),
                    "flag":      item["flag"],
                }
                for item in build_watch_list_for(results, pkey)
            ],
        }
        if "prev" in r:
            ps, pu = r["prev"]
            snapshot["prev"] = build_detail_groups(results, pkey, "prev", with_campaigns=False)
            snapshot["prev_label"] = range_label(ps, pu)

        (data_dir / f"{pkey}.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2)
        )
        index.append({"key": pkey, "label": plabel})
        print(f"  Snapshot saved: docs/data/{pkey}.json ({range_label(since, until)})")

    (data_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    test_mode = os.environ.get("TEST_MODE", "").lower() in ("1", "true", "yes")

    print("Computing period presets...")
    periods = compute_periods()
    for pkey, plabel in PERIODS:
        cs, cu = periods[pkey]["cur"]
        print(f"  {plabel:<13}: {cs} → {cu}")

    n_calls = sum(len(r) for r in periods.values()) * sum(len(a) for a in ACCOUNTS.values())
    print(f"\nPulling campaign data ({n_calls} API calls)...")
    results = pull_all(periods)

    print("\nSaving period snapshots for dashboard...")
    save_period_snapshots(results, periods)

    # Slack production report keeps the weekly cadence (last_week vs the week before).
    print("\nBuilding Slack report (based on last week)...")
    lw_cur  = build_simple_groups(results, SLACK_PERIOD, "cur")
    lw_prev = build_simple_groups(results, SLACK_PERIOD, "prev")
    weekly_groups = {
        name: {"w1": lw_cur[name], "w2": lw_prev[name]}
        for name in ("BRAND", "GROWTH", "VERTICAL")
    }
    watch_list = build_watch_list_for(results, SLACK_PERIOD)
    insights   = generate_insights(lw_cur, lw_prev)
    lw_since, lw_until = periods[SLACK_PERIOD]["cur"]
    w_label = range_label(lw_since, lw_until)

    print(f"Sending Slack messages (test_mode={test_mode})...")
    send_reports(weekly_groups, watch_list, insights, w_label, test_mode=test_mode)

    print("\nDone ✅")


if __name__ == "__main__":
    main()
