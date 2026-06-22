import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from reporter.config import SLACK_DM_SELF, SLACK_CHANNEL_PERF, SLACK_HANG, NOTION_URL
from reporter.formatters import fmt_money, fmt_int, fmt_pct, fmt_freq, fmt_wow

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")


def _send(client: WebClient, channel: str, text: str) -> bool:
    try:
        client.chat_postMessage(channel=channel, text=text, mrkdwn=True)
        return True
    except SlackApiError as e:
        print(f"Slack error [{channel}]: {e.response['error']}")
        return False


def _summary_table(groups: dict, week_label: str) -> str:
    hdr = f"{'Group':<10} {'Spend':>12} {'WoW':>8}  {'QE':>8} {'WoW':>8}  {'ER%':>6} {'WoW':>10}"
    sep = "─" * 70
    rows = [hdr, sep]
    for name in ("BRAND", "GROWTH", "VERTICAL"):
        g  = groups[name]
        w1 = g["w1"]
        w2 = g["w2"]
        rows.append(
            f"{name:<10} {fmt_money(w1['spend']):>12} {fmt_wow(w1['spend'], w2['spend']):>8}"
            f"  {fmt_int(w1['qe']):>8} {fmt_wow(w1['qe'], w2['qe']):>8}"
            f"  {fmt_pct(w1['er']):>6} {fmt_wow(w1['er'], w2['er'], pp=True):>10}"
        )
        if name == "GROWTH" and (w1.get("installs", 0) > 0 or w2.get("installs", 0) > 0):
            rows.append(
                f"  └ Installs: {fmt_int(w1['installs'])} "
                f"({fmt_wow(w1['installs'], w2.get('installs', 0))})"
                f"  CPI: {fmt_money(w1['cpi'])} "
                f"({fmt_wow(w1['cpi'], w2.get('cpi', 0))})"
            )
    return "\n".join(rows)


def _freq_table(watch_list: list) -> str:
    if not watch_list:
        return "All clear ✅"
    hdr = f"{'Campaign':<36} {'Account':<16} {'Freq':>5}  {'Spend':>10}"
    sep = "─" * 72
    rows = [hdr, sep]
    for item in watch_list[:8]:
        rows.append(
            f"{item['name'][:35]:<36} {item['account'][:15]:<16}"
            f" {item['frequency']:.1f}×{item['flag']:>2}  {fmt_money(item['spend']):>10}"
        )
    return "\n".join(rows)


def _insights_block(insights: list) -> str:
    return "\n".join(f"• {ins}" for ins in insights)


def build_message_a(groups: dict, watch_list: list, insights: list, week_label: str) -> str:
    parts = [
        f"🗂 *Weekly Performance Report — {week_label}*",
        "",
        "*📊 Group Summary (WoW)*",
        f"```{_summary_table(groups, week_label)}```",
        "",
        "*🚨 Frequency Watch List*",
        f"```{_freq_table(watch_list)}```",
    ]
    if insights:
        parts += ["", "*💡 Key Insights*", _insights_block(insights)]
    parts += ["", f"🔗 Full report: {NOTION_URL}"]
    return "\n".join(parts)


def build_message_b(vertical: dict, week_label: str) -> str:
    w1 = vertical["w1"]
    w2 = vertical["w2"]
    lines = [
        f"📊 *Vertical Group — {week_label}*",
        "",
        f"• Spend: SGD {fmt_money(w1['spend'])} ({fmt_wow(w1['spend'], w2['spend'])} WoW)",
        f"• QE: {fmt_int(w1['qe'])} ({fmt_wow(w1['qe'], w2['qe'])} WoW)",
        f"• ER: {fmt_pct(w1['er'])} ({fmt_wow(w1['er'], w2['er'], pp=True)} WoW)",
        f"• CPE: SGD {fmt_money(w1['cpe'])}",
        "",
        "*Top Campaigns:*",
    ]
    for c in sorted(w1.get("campaigns", []), key=lambda x: x["spend"], reverse=True)[:5]:
        lines.append(
            f"  • {c['name'][:42]}"
            f" — SGD {fmt_money(c['spend'])}"
            f"  QE {fmt_int(c['qe'])}"
            f"  ER {fmt_pct(c['er'])}"
            f"  {fmt_freq(c['frequency'])}"
        )
    return "\n".join(lines)


def send_reports(
    groups: dict,
    watch_list: list,
    insights: list,
    week_label: str,
    test_mode: bool = False,
) -> None:
    client = WebClient(token=SLACK_TOKEN)
    msg_a = build_message_a(groups, watch_list, insights, week_label)
    msg_b = build_message_b(groups["VERTICAL"], week_label)

    if test_mode:
        _send(client, SLACK_DM_SELF, msg_a)
        _send(client, SLACK_DM_SELF, f"[TEST — Hang's vertical report]\n\n{msg_b}")
    else:
        _send(client, SLACK_DM_SELF, msg_a)
        _send(client, SLACK_CHANNEL_PERF, msg_a)
        _send(client, SLACK_HANG, msg_b)
