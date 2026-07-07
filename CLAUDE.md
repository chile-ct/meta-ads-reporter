# Meta Ads Weekly Reporter — Claude Runbook

Đây là hướng dẫn đầy đủ để Claude chạy báo cáo Meta Ads hàng tuần cho Chotot.
Đọc file này trước khi bắt đầu bất kỳ tác vụ nào liên quan đến báo cáo.

---

## Lịch chạy

**Production run:** Mỗi thứ 2 lúc 9h sáng ICT
**Test run:** Bất kỳ lúc nào ngoài lịch trên

**CRITICAL — Quy tắc Slack:**
- Production run (thứ 2 lúc 9h sáng) → gửi đến **cả 3** target
- Test run (mọi trường hợp khác) → chỉ gửi đến **self DM** (D01J9JRNERH)

---

## 9 Ad Accounts

| Group | Account name | Account ID |
|---|---|---|
| BRAND | gds_brand | 253279950744492 |
| BRAND | pty_branding_sgd | 697690298835029 |
| BRAND | veh_brand | 937141594251635 |
| BRAND | job_branding_sgd | 339646702235039 |
| GROWTH | growth_sgd | 217167486615130 |
| GROWTH | job_sgd | 1009648153146994 |
| GROWTH | gds_elt_sgd | 655717678725444 |
| VERTICAL | job_trade_sgd | 1581743339281376 |
| VERTICAL | pty_sgd | 189567943020118 |

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

### Step 1 — Date ranges
- **W1** = tuần vừa kết thúc (Mon–Sun)
- **W2** = tuần trước đó (Mon–Sun)
- Thường chạy vào sáng thứ 2, nên W1 = tuần trước, W2 = 2 tuần trước

### Step 2 — Pull Meta Ads data
Dùng `mcp__Facebook_Ads_MCP__ads_get_ad_entities` cho mỗi account:
```
level: campaign
time_range: {since: "YYYY-MM-DD", until: "YYYY-MM-DD"}
fields: spend, reach, impressions, frequency, clicks, cpc, ctr, actions
filtering: [{field: "spend", operator: "GREATER_THAN", value: "0"}]
```
Pull W1 và W2 cho tất cả 9 accounts (18 API calls).

**Tên field action đúng tại campaign level:**
- `actions:comment`
- `actions:post_save`
- `actions:link_click`

### Step 3 — Compute metrics
Tính theo định nghĩa ở trên cho từng group. Tính WoW %. Gán frequency flags.

### Step 4 — Build JSON report
Cấu trúc file:
```json
{
  "week_start": "YYYY-MM-DD",
  "week_label": "Mon DD–DD, YYYY",
  "total_spend": 0.00,
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "detail_available": true,
  "groups": {
    "BRAND": { "spend", "reach", "avg_freq", "qe", "cpe", "er", "accounts": {...} },
    "GROWTH": { "spend", "reach", "avg_freq", "link_clicks", "accounts": {...} },
    "VERTICAL": { "spend", "reach", "avg_freq", "qe", "cpl", "accounts": {...} }
  },
  "watch_list": [ ...campaigns sorted by freq desc, all freq >= 3... ]
}
```
Mỗi account trong `accounts` có `campaigns` array với: name, spend, reach, freq, clicks, cpc, ctr, và metrics tương ứng (qe/cpe/er hoặc link_clicks).

### Step 5 — Push JSON to GitHub
- Path: `docs/data/YYYY-MM-DD.json` trên branch `main`
- Cập nhật `docs/data/index.json` (thêm date mới vào đầu mảng)
- Dùng `mcp__github__create_or_update_file` với SHA của file hiện tại (nếu update)
- Nếu 403: lưu file tại `/tmp/YYYY-MM-DD.json`, báo user paste thủ công lên GitHub web UI

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

Dashboard tự động load từ `docs/data/index.json` → đọc từng file JSON theo ngày.
Không cần deploy gì thêm — GitHub Pages tự serve khi file được push lên `main`.

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
