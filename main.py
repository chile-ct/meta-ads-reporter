import os
import sys
import json
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from reporter.config import ACCOUNTS, FREQ_GREEN, FREQ_YELLOW
from reporter.meta_api import fetch_campaigns
from reporter.formatters import fmt_money, fmt_int, fmt_pct, fmt_wow, freq_flag
from reporter.slack_sender import send_reports


# ── Date ranges ───────────────────────────────────────────────────────────────

def compute_date_ranges() -> dict:
    today = date.today()
    # Monday of last week
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)

    w1_since = last_monday.strftime("%Y-%m-%d")
    w1_until = last_sunday.strftime("%Y-%m-%d")
    w2_since = (last_monday - timedelta(days=7)).strftime("%Y-%m-%d")
    w2_until = (last_sunday - timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "w1": (w1_since, w1_until),
        "w2": (w2_since, w2_until),
    }


def week_label(date_ranges: dict) -> str:
    since, until = date_ranges["w1"]
    d0 = date.fromisoformat(since)
    d1 = date.fromisoformat(until)
    if d0.month == d1.month:
        return f"{d0.strftime('%b')} {d0.day}–{d1.day}, {d1.year}"
    return f"{d0.strftime('%b %d')} – {d1.strftime('%b %d')}, {d1.year}"


# ── Data pull ─────────────────────────────────────────────────────────────────

def pull_all(date_ranges: dict) -> dict:
    tasks = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for period, (since, until) in date_ranges.items():
            for group, accounts in ACCOUNTS.items():
                for acct_name, acct_id in accounts.items():
                    key = (period, group, acct_name)
                    tasks[key] = ex.submit(fetch_campaigns, acct_id, since, until)

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
    # A campaign is counted as "active" if it spent money during the window
    # (paused-mid-week campaigns still spent, so they count). red_freq_camps
    # flags the ones that hit the critical frequency threshold.
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


def build_groups(results: dict, period: str) -> dict:
    groups = {}
    for group_name in ACCOUNTS:
        all_campaigns = []
        for acct_name in ACCOUNTS[group_name]:
            all_campaigns += results.get((period, group_name, acct_name), [])
        groups[group_name] = aggregate(all_campaigns)
    return groups


# ── Frequency watch list ──────────────────────────────────────────────────────

def build_watch_list(groups_w1: dict) -> list:
    items = []
    for group_name, group in groups_w1.items():
        for acct_name in ACCOUNTS[group_name]:
            pass  # we need per-account data; use group campaigns tagged by account

    # Re-collect from raw campaigns with account tag added
    # (campaigns don't carry account name, so we need groups_w1 raw campaigns per account)
    # This is handled via build_watch_list_from_results instead
    return items


def build_watch_list_from_results(results: dict) -> list:
    items = []
    for group_name in ACCOUNTS:
        for acct_name in ACCOUNTS[group_name]:
            campaigns = results.get(("w1", group_name, acct_name), [])
            for c in campaigns:
                if c["frequency"] >= FREQ_GREEN:
                    items.append({
                        "name":      c["name"],
                        "account":   acct_name,
                        "frequency": c["frequency"],
                        "flag":      freq_flag(c["frequency"]),
                        "spend":     c["spend"],
                    })
    items.sort(key=lambda x: x["frequency"], reverse=True)
    return items[:8]


# ── Key insights ──────────────────────────────────────────────────────────────

def generate_insights(groups_w1: dict, groups_w2: dict) -> list:
    insights = []

    for name in ("BRAND", "GROWTH", "VERTICAL"):
        w1 = groups_w1[name]
        w2 = groups_w2[name]

        # Spend change ≥20%
        if w2["spend"] > 0:
            pct = (w1["spend"] - w2["spend"]) / w2["spend"] * 100
            if abs(pct) >= 20:
                direction = "tăng" if pct > 0 else "giảm"
                insights.append(
                    f"{name}: Spend {direction} {abs(pct):.1f}% WoW "
                    f"(SGD {fmt_money(w1['spend'])} vs SGD {fmt_money(w2['spend'])})"
                )

        # ER swing ≥0.5pp
        if w2["er"] > 0:
            pp = w1["er"] - w2["er"]
            if abs(pp) >= 0.5:
                direction = "cải thiện" if pp > 0 else "giảm"
                insights.append(
                    f"{name}: ER {direction} {abs(pp):.2f}pp WoW "
                    f"({fmt_pct(w1['er'])} vs {fmt_pct(w2['er'])})"
                )

        # Install-specific for GROWTH
        if name == "GROWTH":
            i1, i2 = w1.get("installs", 0), w2.get("installs", 0)
            if i1 > 0 or i2 > 0:
                pct_str = fmt_wow(i1, i2)
                insights.append(
                    f"GROWTH: {fmt_int(i1)} installs ({pct_str} WoW), "
                    f"CPI SGD {fmt_money(w1['cpi'])}"
                )

    # Critical frequency
    high_freq = sum(
        1 for name in ("BRAND", "GROWTH", "VERTICAL")
        for c in groups_w1[name].get("campaigns", [])
        if c["frequency"] >= FREQ_YELLOW
    )
    if high_freq:
        insights.append(
            f"⚠️ {high_freq} campaign(s) đang ở mức Freq ≥7× — cần cân nhắc refresh creative"
        )

    return insights[:5]


# ── Weekly snapshot (for GitHub Pages dashboard) ──────────────────────────────

def save_weekly_snapshot(groups_w1: dict, watch_list: list, w_label_str: str, date_ranges: dict) -> None:
    week_start = date_ranges["w1"][0]
    snapshot = {
        "week_start":    week_start,
        "week_label":    w_label_str,
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "groups": {
            name: {
                "spend":    round(groups_w1[name]["spend"], 2),
                "qe":       int(groups_w1[name]["qe"]),
                "er":       round(groups_w1[name]["er"], 4),
                "cpe":      round(groups_w1[name]["cpe"], 2),
                "installs": int(groups_w1[name].get("installs", 0)),
                "cpi":      round(groups_w1[name].get("cpi", 0), 2),
                "active_camps":   int(groups_w1[name].get("active_camps", 0)),
                "red_freq_camps": int(groups_w1[name].get("red_freq_camps", 0)),
            }
            for name in ("BRAND", "GROWTH", "VERTICAL")
        },
        "watch_list": [
            {
                "name":      item["name"],
                "account":   item["account"],
                "frequency": round(item["frequency"], 2),
                "spend":     round(item["spend"], 2),
                "flag":      item["flag"],
            }
            for item in watch_list
        ],
    }

    data_dir = Path(__file__).parent / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    (data_dir / f"{week_start}.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2)
    )

    index_file = data_dir / "index.json"
    index = json.loads(index_file.read_text()) if index_file.exists() else []
    if week_start not in index:
        index.insert(0, week_start)
    index_file.write_text(json.dumps(index, indent=2))

    print(f"  Snapshot saved: docs/data/{week_start}.json")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    test_mode = os.environ.get("TEST_MODE", "").lower() in ("1", "true", "yes")

    print("Computing date ranges...")
    date_ranges = compute_date_ranges()
    w_label = week_label(date_ranges)
    print(f"  W1 : {date_ranges['w1'][0]} → {date_ranges['w1'][1]}")
    print(f"  W2 : {date_ranges['w2'][0]} → {date_ranges['w2'][1]}")

    print("\nPulling campaign data (26 API calls)...")
    results = pull_all(date_ranges)

    print("Aggregating metrics...")
    groups_w1 = build_groups(results, "w1")
    groups_w2 = build_groups(results, "w2")

    weekly_groups = {
        name: {"w1": groups_w1[name], "w2": groups_w2[name]}
        for name in ("BRAND", "GROWTH", "VERTICAL")
    }

    watch_list = build_watch_list_from_results(results)
    insights   = generate_insights(groups_w1, groups_w2)

    print("\nSaving weekly snapshot for dashboard...")
    save_weekly_snapshot(groups_w1, watch_list, w_label, date_ranges)

    print(f"Sending Slack messages (test_mode={test_mode})...")
    send_reports(weekly_groups, watch_list, insights, w_label, test_mode=test_mode)

    print("\nDone ✅")


if __name__ == "__main__":
    main()
