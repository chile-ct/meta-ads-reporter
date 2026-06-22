import os
import time
from notion_client import Client
from reporter.config import NOTION_PAGE_ID
from reporter.formatters import fmt_money, fmt_int, fmt_pct, fmt_freq, fmt_wow

NOTION_KEY = os.environ.get("NOTION_API_KEY", "")


def _notion() -> Client:
    return Client(auth=NOTION_KEY)


# ── Block builders ────────────────────────────────────────────────────────────

def _h1(text: str) -> dict:
    return {"object": "block", "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}


def _h2(text: str) -> dict:
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}


def _h3(text: str) -> dict:
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}


def _p(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}


def _code(text: str) -> dict:
    return {"object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}],
                     "language": "plain text"}}


def _bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


# ── Content builders ──────────────────────────────────────────────────────────

def _group_summary_blocks(month_groups: dict, month_label: str) -> list:
    hdr = f"{'Group':<10} {'Spend (SGD)':>14}  {'QE':>8}  {'ER%':>7}  {'Installs':>10}  {'CPI':>8}"
    sep = "─" * 65
    rows = [hdr, sep]
    for name in ("BRAND", "GROWTH", "VERTICAL"):
        g = month_groups[name]
        rows.append(
            f"{name:<10} {fmt_money(g['spend']):>14}"
            f"  {fmt_int(g['qe']):>8}"
            f"  {fmt_pct(g['er']):>7}"
            f"  {fmt_int(g['installs']) if g['installs'] > 0 else '—':>10}"
            f"  {fmt_money(g['cpi']) if g['cpi'] > 0 else '—':>8}"
        )
    return [_h2(f"🗂 Group Summary — {month_label}"), _code("\n".join(rows))]


def _freq_watch_blocks(watch_list: list) -> list:
    blocks = [_h2("🚨 Frequency Watch List")]
    if not watch_list:
        blocks.append(_p("All campaigns within acceptable frequency ✅"))
        return blocks
    hdr = f"{'Campaign':<38} {'Account':<18} {'Freq':>5}  {'Spend':>10}"
    sep = "─" * 75
    rows = [hdr, sep]
    for item in watch_list[:8]:
        rows.append(
            f"{item['name'][:37]:<38} {item['account'][:17]:<18}"
            f" {item['frequency']:.1f}×{item['flag']:>2}  {fmt_money(item['spend']):>10}"
        )
    blocks.append(_code("\n".join(rows)))
    return blocks


def _account_blocks(acct_name: str, campaigns: list) -> list:
    if not campaigns:
        return [_h3(acct_name), _p("No active spend this period.")]

    total_spend = sum(c["spend"] for c in campaigns)
    total_qe    = sum(c["qe"] for c in campaigns)
    total_reach = sum(c["reach"] for c in campaigns)
    total_inst  = sum(c["installs"] for c in campaigns)
    avg_er      = (total_qe / total_reach * 100) if total_reach > 0 else 0.0

    summary = (
        f"Spend: SGD {fmt_money(total_spend)}  "
        f"QE: {fmt_int(total_qe)}  "
        f"ER: {fmt_pct(avg_er)}"
    )
    if total_inst > 0:
        inst_spend = sum(c["spend"] for c in campaigns if c["is_install"])
        cpi = inst_spend / total_inst
        summary += f"  Installs: {fmt_int(total_inst)}  CPI: SGD {fmt_money(cpi)}"

    hdr = f"{'Campaign':<42} {'Spend':>10}  {'QE':>7}  {'ER%':>6}  {'Freq':>8}"
    sep = "─" * 80
    rows = [hdr, sep]
    for c in sorted(campaigns, key=lambda x: x["spend"], reverse=True):
        rows.append(
            f"{c['name'][:41]:<42} {fmt_money(c['spend']):>10}"
            f"  {fmt_int(c['qe']):>7}"
            f"  {fmt_pct(c['er']):>6}"
            f"  {fmt_freq(c['frequency']):>8}"
        )

    return [_h3(acct_name), _p(summary), _code("\n".join(rows))]


def _group_blocks(group_name: str, accounts_data: dict) -> list:
    blocks = [_divider(), _h2(group_name)]
    for acct_name, campaigns in accounts_data.items():
        blocks += _account_blocks(acct_name, campaigns)
    return blocks


# ── Page management ───────────────────────────────────────────────────────────

def _clear_page(notion: Client) -> None:
    cursor = None
    while True:
        kwargs = {"block_id": NOTION_PAGE_ID, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = notion.blocks.children.list(**kwargs)
        for block in resp.get("results", []):
            notion.blocks.delete(block_id=block["id"])
            time.sleep(0.05)
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")


def _append_blocks(notion: Client, blocks: list) -> None:
    batch_size = 95
    for i in range(0, len(blocks), batch_size):
        notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=blocks[i : i + batch_size],
        )
        time.sleep(0.3)


def write_monthly_report(
    month_groups: dict,
    month_by_account: dict,
    watch_list: list,
    month_label: str,
) -> None:
    notion = _notion()

    all_blocks = []

    # Header
    all_blocks += [_h1(f"📊 Meta Ads Monthly Report — {month_label}")]

    # Group Summary
    all_blocks += _group_summary_blocks(month_groups, month_label)

    # Freq Watch List (immediately after Group Summary)
    all_blocks += _freq_watch_blocks(watch_list)

    # Per-group per-account breakdown
    for group_name in ("BRAND", "GROWTH", "VERTICAL"):
        all_blocks += _group_blocks(group_name, month_by_account[group_name])

    _clear_page(notion)
    _append_blocks(notion, all_blocks)

    # Update page title
    notion.pages.update(
        page_id=NOTION_PAGE_ID,
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": f"Meta Ads Report — {month_label}"}}]
            }
        },
    )
