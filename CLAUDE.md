# Meta Ads Weekly Reporter — Claude Runbook

Đây là hướng dẫn đầy đủ để Claude chạy báo cáo Meta Ads hàng tuần cho Chotot.
Đọc file này trước khi bắt đầu bất kỳ tác vụ nào liên quan đến báo cáo.

---

## Session Setup (chạy đầu mỗi session)

Trước khi làm bất kỳ việc gì liên quan đến GitHub push, Claude cần config git với Personal Access Token:

```bash
git remote set-url origin https://chile-ct:TOKEN@github.com/chile-ct/meta-ads-reporter.git
git config user.email noreply@anthropic.com
git config user.name Claude
```

**Cách lấy TOKEN:** Token được lưu trong GitHub Secrets của repo (`GH_PAT`). Nếu không có sẵn, hỏi người dùng cung cấp PAT (tạo tại github.com/settings/tokens, scope: `repo`).

Nếu người dùng chưa cung cấp token khi bắt đầu session → hỏi ngay: *"Bạn có GitHub PAT không? Cần để push data lên GitHub sau khi chạy xong."*

---

## Lịch chạy

**Data pipeline (dashboard):** Nên chạy **mỗi ngày** 9h sáng ICT (cron `0 2 * * *`) để các period preset "Yesterday" / "Last 7 days" luôn mới. Mỗi lần chạy pull lại toàn bộ 7 preset.
**Slack production report:** Vẫn theo tuần — thứ 2 lúc 9h sáng ICT (dựa trên preset `last_week`).
**Test run:** Bất kỳ lúc nào ngoài lịch trên → Slack chỉ gửi self DM.

> ⚠️ Cron hiện tại là `0 2 * * 1` (chỉ thứ 2). Đổi sang `0 2 * * *` để chạy hằng ngày. File `.github/workflows/*` chỉ push được bằng PAT có scope `workflow` (PAT hiện dùng thiếu scope này → phải sửa thủ công trên GitHub web UI).

**CRITICAL — Quy tắc Slack:**
- Production run (thứ 2 lúc 9h sáng) → gửi đến **cả 3** target
- Test run (mọi trường hợp khác) → chỉ gửi đến **self DM** (D01J9JRNERH)

---

## 13 Ad Accounts

Group = Team. Dashboard hiển thị group **GROWTH** dưới tab **Digital**. Phase (Demand/App) là metadata: App = focus install/CPI, Demand = focus link-click/QE.

| Group | Account name | Account ID | Phase |
|---|---|---|---|
| BRAND | gds_brand | 253279950744492 | — |
| BRAND | pty_branding_sgd | 697690298835029 | — |
| BRAND | veh_brand | 937141594251635 | — |
| BRAND | job_branding_sgd | 339646702235039 | — |
| GROWTH | job_sgd | 1009648153146994 | Demand |
| GROWTH | growth_sgd | 217167486615130 | App |
| GROWTH | veh_sgd | 211751247179666 | Demand |
| GROWTH | gds_elt_sgd | 655717678725444 | Demand |
| GROWTH | pty_app | 1924712638163043 | App |
| GROWTH | job_app | 1021879607190581 | App |
| GROWTH | pty_sgd | 189567943020118 | Demand |
| VERTICAL | pty_seller_sgd | 1632822317085217 | — |
| VERTICAL | job_trade_sgd | 1581743339281376 | — |

**Lưu ý MCP:** 3 account `veh_sgd`, `pty_app`, `pty_seller_sgd` hiện đang "Ads MCP disabled" — không pull được qua Meta Ads MCP (pull thủ công). Pipeline Python cron (GitHub Actions, dùng Graph API token) vẫn pull được bình thường.

---

## Slack Targets

| Target | ID | Khi nào gửi |
|---|---|---|
| Self DM (người chạy) | D01J9JRNERH | Luôn luôn |
| #ct-marketing-performance | C0B93T2655Z | Production only |
| Hang Le Tuyet DM | U09FKRCU8JY | Production only |

---

## Metric Definitions

### BRAND
- **QE** (Quality Engagement) = actions:comment + actions:post_save + actions:link_click
  - `post_shares` = 0 nếu "Not available" tại campaign level
- **CPE** = spend / QE
- **ER** = (QE / reach) × 100 (4 decimal places)
- **avg_freq** = total_impressions / total_reach (weighted average across campaigns)

### GROWTH
- **link_clicks** = sum of actions:link_click per campaign
- **avg_freq** = weighted average

### VERTICAL
- **job_trade_sgd**: QE = actions:link_click; CPL = spend / QE
- **pty_sgd**: link_clicks = actions:link_click (không tính CPL)

### WoW % change
- Formula: `(W1 − W2) / W2 × 100`
- Prefix: `+` hoặc `−`
- Nếu W2 = 0 → hiển thị "new"

### Frequency flags
- ✅ freq < 3
- 🟡 freq 3–6
- 🔴 freq ≥ 7

---

## 8-Step Weekly Workflow

### Step 1 — Date ranges (period presets)
`main.py > compute_periods()` tự tính 7 preset, mỗi preset gồm `cur` (kỳ hiện tại) + `prev` (kỳ liền trước cùng độ dài). Week/month-to-date kết thúc ở hôm qua. Slack report vẫn dùng `last_week` (cur = tuần vừa rồi, prev = tuần trước đó).

### Step 2 — Pull Meta Ads data
Dùng `mcp__Facebook_Ads_MCP__ads_get_ad_entities` cho mỗi account:
```
level: campaign
time_range: {since: "YYYY-MM-DD", until: "YYYY-MM-DD"}
fields: spend, reach, impressions, frequency, clicks, cpc, ctr, actions
filtering: [{field: "spend", operator: "GREATER_THAN", value: "0"}]
```
Pipeline Python (`main.py`) pull **7 period preset**, mỗi preset có range `cur` + range `prev` tương đương (để tính "vs kỳ trước"), cho tất cả 13 accounts → ~182 API calls. Preset: Yesterday, This week, Last week, Last 7 days, Last 30 days, This month, Last month. Week/month-to-date kết thúc ở **hôm qua** (hôm nay coi như chưa đủ ngày).

Mỗi preset là 1 query Meta thật trên đúng range đó — KHÔNG cộng dồn dữ liệu ngày, vì `reach`/`frequency` không cộng được (Meta dedupe theo range).

**Tên field action đúng tại campaign level:**
- `actions:comment`
- `actions:post_save`
- `actions:link_click`

### Step 3 — Compute metrics
Tính theo định nghĩa ở trên cho từng group. Tính delta cur vs prev. Gán frequency flags.

### Step 4 — Build JSON report (1 file / preset)
Mỗi preset ghi 1 file `docs/data/<key>.json`:
```json
{
  "key": "last_7d",
  "period_label": "Last 7 days",
  "week_label": "Jul 15–21, 2026",   // range label của kỳ hiện tại (dùng lại tên cũ)
  "since": "YYYY-MM-DD", "until": "YYYY-MM-DD",
  "prev_label": "Jul 8–14, 2026",
  "total_spend": 0.00,
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "detail_available": true,
  "groups": {
    "BRAND":    { "spend","reach","impressions","avg_freq","qe","cpe","er","installs","cpi","active_camps","red_freq_camps","accounts": {...} },
    "GROWTH":   { ...same..., "link_clicks", "accounts": {...} },
    "VERTICAL": { ...same..., "cpl", "accounts": {...} }
  },
  "prev": { "BRAND": {...group metrics, KHÔNG có accounts/campaigns...}, "GROWTH": {...}, "VERTICAL": {...} },
  "watch_list": [ ...campaigns freq >= 3, sorted desc, top 8... ]
}
```
- `groups` (kỳ hiện tại) có `accounts` → mỗi account có `campaigns` array: name, spend, reach, impressions, freq, clicks, cpc, ctr, qe, cpe, er, link_clicks, installs, is_install, is_active.
- `prev` chỉ chứa group-level metrics (không campaigns) để tính delta "vs kỳ trước" trên dashboard.

### Step 5 — Push JSON to GitHub
- Path: `docs/data/<key>.json` trên branch `main` (yesterday, this_week, last_week, last_7d, last_30d, this_month, last_month).
- `docs/data/index.json` = mảng `[{ "key", "label" }, ...]` theo đúng thứ tự hiển thị trên dropdown.
- Pipeline cron (GitHub Actions) tự commit toàn bộ `docs/data/` sau khi chạy `python main.py`.
- Nếu chạy tay và bị 403: lưu file tại `/tmp/`, báo user paste thủ công lên GitHub web UI.

### Step 6 — Build Slack messages

**Message A** (gửi đến self DM + channel):
```
📊 Meta Ads Weekly: [week_label]

💰 BRAND — SGD X,XXX
Spend: $X,XXX | Reach: X.XM | Freq: X.XX ✅/🟡/🔴
QE: X,XXX | CPE: $X.XX | ER: X.XXXX%
WoW — Spend: +X% | QE: +X% | CPE: +X%

🚀 GROWTH — SGD X,XXX
Spend: $X,XXX | Reach: XXXk | Freq: X.XX
Link Clicks: XX,XXX
WoW — Spend: +X% | Clicks: +X%

🎯 VERTICAL — SGD X,XXX
[job_trade_sgd] Spend: $XXX | QE: XXX | CPL: $X.XX | Freq: X.XX
[pty_sgd] Spend: $XXX | Link Clicks: XXX | Freq: X.XX
WoW — ...

🔴 Frequency Watch List:
• campaign_name (account) — freq X.Xx, $XX.XX
...

💵 Total spend: $X,XXX.XX
```

**Message B** (gửi riêng cho Hang Le Tuyet):
Chi tiết VERTICAL group với breakdown theo từng campaign.

### Step 7 — Send Slack messages
Dùng `mcp__Slack__slack_send_message`:
- **Test run**: chỉ gửi Message A → D01J9JRNERH
- **Production run**: Message A → D01J9JRNERH + C0B93T2655Z; Message B → U09FKRCU8JY

### Step 8 — Session summary
Output plain text tóm tắt: date range, total spend, key metrics, deliverables completed.

**CRITICAL: KHÔNG bao giờ wrap output trong XML tags. Plain text only.**

---

## Dashboard

URL: `https://chile-ct.github.io/meta-ads-reporter/`

Dashboard load `docs/data/index.json` (mảng preset) → fetch từng `docs/data/<key>.json`. Dropdown header là **period selector** (Yesterday / This week / Last week / Last 7 days / Last 30 days / This month / Last month). Chart Overview so sánh **kỳ này vs kỳ trước** (bar chart), dùng field `prev` trong mỗi file.
Không cần deploy gì thêm — GitHub Pages tự serve khi file được push lên `main`.

> Các file tuần cũ `docs/data/YYYY-MM-DD.json` không còn được `index.json` tham chiếu (orphaned) — vô hại, có thể xoá sau nếu muốn.

---

## GitHub Push Notes

File data cần được commit vào `main` (không phải dev branch).
GitHub Actions workflow (`weekly-report.yml`) có `contents: write` permission — nếu chạy qua Actions thì push tự động. Nếu chạy qua Claude Code session, cần GitHub App có write access vào `chile-ct/meta-ads-reporter`.

Cách kiểm tra: vào `github.com/organizations/chile-ct/settings/installations` → Claude → Configure → đảm bảo `meta-ads-reporter` được chọn.

---

## Team member setup checklist

- [ ] Được add làm Collaborator trên `chile-ct/meta-ads-reporter` (Write access)
- [ ] Có Claude Code (claude.ai/code)
- [ ] Connect **Meta Ads MCP** với Meta access token có quyền `ads_read` + `read_insights`
- [ ] Connect **Slack MCP** với Slack bot token `xoxb-...` có scope `chat:write`
- [ ] Mở repo `chile-ct/meta-ads-reporter` trong Claude Code on the web
- [ ] Verify: GitHub App Claude được install trên org `chile-ct` với repo write access
