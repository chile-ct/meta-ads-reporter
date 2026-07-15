# Chotot Meta Ads Dashboard — Handoff cho Duyên

> Tài liệu này giúp bạn bắt kịp context nhanh mà không cần đọc lại toàn bộ lịch sử. Cập nhật lần cuối: 2026-07-15.

---

## 1. Tổng quan

Dashboard tự động theo dõi hiệu suất Meta Ads hàng tuần cho Chotot, gồm 9 ad accounts chia 3 nhóm (Brand / Growth / Vertical). Mỗi thứ 2, một Claude routine tự động:

1. Kéo data từ Meta Ads API cho tuần vừa qua (Mon–Sun)
2. Tính metrics, build file JSON
3. Push file JSON lên GitHub → dashboard tự cập nhật
4. Gửi báo cáo qua Slack

**Links quan trọng:**
- Dashboard: https://chile-ct.github.io/meta-ads-reporter/
- Repo: https://github.com/chile-ct/meta-ads-reporter
- Claude Routine: https://claude.ai/code/routines/trig_01UvWJuFt54akLLCUssqq6vS

---

## 2. Cấu trúc repo

```
meta-ads-reporter/
├── docs/
│   ├── index.html          ← toàn bộ UI dashboard (1 file duy nhất, vanilla JS)
│   └── data/
│       ├── index.json      ← danh sách tất cả tuần có data (dashboard đọc file này trước)
│       ├── 2026-04-06.json ← dữ liệu tuần Apr 6–12
│       ├── 2026-04-13.json
│       │   ... (mỗi file = 1 tuần)
│       └── 2026-06-23.json ← tuần mới nhất
├── patch_history.py        ← script backfill data lịch sử (Apr–Jun 2026), dùng 1 lần
├── main.py                 ← script pull data thủ công (reference)
└── requirements.txt
```

> **Lưu ý `index.json`:** Khi thêm file tuần mới, phải cập nhật `docs/data/index.json` để dashboard biết file đó tồn tại. Routine tự làm việc này — nếu làm thủ công thì nhớ thêm vào.

---

## 3. Account Groups & IDs

| Group | Account name | Ad Account ID |
|---|---|---|
| **BRAND** | gds_brand | 253279950744492 |
| | pty_branding_sgd | 697690298835029 |
| | veh_brand | 937141594251635 |
| | job_branding_sgd | 339646702235039 |
| **GROWTH** | growth_sgd | 217167486615130 |
| | job_sgd | 1009648153146994 |
| | gds_elt_sgd | 655717678725444 |
| **VERTICAL** | job_trade_sgd | 1581743339281376 |
| | pty_sgd | 189567943020118 |

---

## 4. Metrics & Công thức

| Metric | Công thức | Áp dụng cho |
|---|---|---|
| QE (Quality Engagement) | comment + link_click + post_save + post_shares | BRAND, VERTICAL |
| CPE (Cost Per Engagement) | spend / QE | BRAND |
| ER (Engagement Rate) | (QE / reach) × 100 | BRAND |
| CPL (Cost Per Lead) | spend / QE | VERTICAL |
| Link Clicks | clicks từ API | GROWTH |
| Frequency flag | ✅ < 3× · 🟡 3–6× · 🔴 ≥ 7× | tất cả |
| Watch List | tất cả campaigns có freq ≥ 3.0, sort desc | tất cả |

**Quirk quan trọng — VERTICAL accounts:** `job_trade_sgd` và `pty_sgd` **không hỗ trợ action fields** (comment, link_click, post_save, post_shares) khi gọi Meta Ads API — sẽ trả lỗi "Internal error". Phải fetch với basic fields only: `name, amount_spent, impressions, reach, clicks, cpm, cpc, ctr, frequency`. Do đó VERTICAL không có QE/CPL từ engagement actions — chỉ có spend/reach/clicks/freq.

---

## 5. Cấu trúc file JSON (schema chuẩn)

Mỗi tuần là 1 file `docs/data/YYYY-MM-DD.json` (đặt tên theo thứ 2 đầu tuần).

```json
{
  "week_start": "2026-06-23",
  "week_label": "Jun 23–29, 2026",
  "total_spend": 3288.50,
  "generated_at": "2026-06-29T10:00:00Z",
  "detail_available": true,
  "groups": {
    "BRAND": {
      "spend": 1504.81,
      "reach": 1500000,
      "avg_freq": 1.45,
      "qe": 620,
      "cpe": 2.43,
      "er": 0.0413,
      "accounts": {
        "gds_brand": {
          "spend": 250.00, "reach": 140000, "qe": 45, "cpe": 5.56, "er": 0.0321, "avg_freq": 1.80,
          "campaigns": [
            { "name": "brand_eng_gds_b2c_0626", "spend": 250.00, "reach": 140000,
              "freq": 1.80, "clicks": 5800, "cpc": 0.04, "ctr": 2.30,
              "qe": 45, "cpe": 5.56, "er": 0.0321 }
          ]
        }
        // ... pty_branding_sgd, veh_brand, job_branding_sgd (cùng shape)
      }
    },
    "GROWTH": {
      "spend": 1549.38, "reach": 800000, "avg_freq": 3.20, "link_clicks": 65000,
      "accounts": {
        "growth_sgd": {
          "spend": 1100.00, "reach": 450000, "link_clicks": 42000, "avg_freq": 3.50,
          "campaigns": [
            { "name": "growth_video_standalone_demand", "spend": 350.00,
              "reach": 140000, "freq": 5.80, "clicks": 17000, "cpc": 0.02, "ctr": 2.15 }
          ]
        }
        // ... job_sgd, gds_elt_sgd (cùng shape)
      }
    },
    "VERTICAL": {
      "spend": 234.31, "reach": 120000, "avg_freq": 2.10, "qe": 0, "cpl": 0,
      "accounts": {
        "job_trade_sgd": {
          "spend": 234.31, "reach": 120000, "qe": 0, "cpl": 0, "avg_freq": 2.10,
          "campaigns": [
            { "name": "job_recruiter_growth_jun26", "spend": 234.31,
              "reach": 120000, "freq": 2.10, "clicks": 800, "cpc": 0.29, "ctr": 0.67 }
          ]
        },
        "pty_sgd": { "spend": 0, "reach": 0, "link_clicks": 0, "avg_freq": 0, "campaigns": [] }
      }
    }
  },
  "watch_list": [
    { "account": "growth_sgd", "group": "GROWTH", "campaign": "growth_video_standalone_demand",
      "freq": 5.80, "spend": 350.00 }
  ]
}
```

**Flag quan trọng:** `"detail_available": true` — phải có flag này thì dashboard mới hiển thị campaign tables, demographics, watch list. Nếu thiếu hoặc `false` thì các tab Brand/Growth/Vertical chỉ hiện tổng, không có chi tiết.

---

## 6. Cách hoạt động hàng tuần (tự động)

```
Thứ 2, 9:00 ICT
     │
     ▼
Claude Routine (trig_01UvWJuFt54akLLCUssqq6vS)
     │
     ├── Pull W1 data (tuần vừa qua, Mon–Sun) cho 9 accounts
     ├── Pull W2 data (tuần trước đó) để tính WoW %
     ├── Tính metrics (QE, CPE, ER, CPL, freq, watch_list)
     ├── Build JSON → push lên GitHub: docs/data/YYYY-MM-DD.json
     ├── Gửi Slack Message A → DM chi (D01J9JRNERH) + #channel (C0B93T2655Z)
     └── Gửi Slack Message B (Vertical only) → DM Hang Le Tuyet (U09FKRCU8JY)
```

Routine dùng Claude claude-sonnet-4-6, chạy trên claude.ai CCR environment với MCP connectors: Meta Ads, Builder_OS (GitHub), Slack.

---

## 7. Thêm tuần mới thủ công

Nếu cần thêm 1 tuần mà không muốn chờ routine (hoặc routine lỗi):

**Cách 1 — Dùng Agent trong Claude Code:**
Yêu cầu: "Pull Meta Ads data cho tuần [DATE_SINCE] đến [DATE_UNTIL], tạo file docs/data/[DATE_SINCE].json và push lên GitHub" — agent sẽ tự làm theo schema ở mục 5.

**Cách 2 — Chạy routine thủ công:**
Vào https://claude.ai/code/routines/trig_01UvWJuFt54akLLCUssqq6vS → bấm "Run now".

**Cách 3 — Thủ công hoàn toàn:**
```bash
# 1. Copy một file JSON tuần gần nhất làm template
cp docs/data/2026-06-23.json docs/data/2026-06-30.json

# 2. Sửa dữ liệu trong file mới

# 3. Cập nhật docs/data/index.json — thêm "2026-06-30" vào danh sách

# 4. Push lên GitHub
git add docs/data/
git commit -m "Add weekly report 2026-06-30"
git push
```

---

## 8. Dashboard UI (index.html)

Toàn bộ UI là 1 file `docs/index.html` — vanilla JS, không có build step, không có dependency ngoài Chart.js (CDN).

**Tabs chính:**
- **Overview**: tổng spend + group summary table + key insights
- **🏷 Brand**: per-account campaign table (Spend/Reach/Freq/QE/CPE/ER%), demographics
- **💻 Digital** (Growth): per-account campaign table (Spend/Reach/Clicks/CTR/CPC/Freq)
- **🏢 Vertical**: per-account campaign table (Spend/Reach/CPL/Freq)

**CSS variables chính** (đầu file, trong `:root`):
```
--brand:#2563eb  (xanh dương — Brand group)
--growth:#059669 (xanh lá — Growth group)
--vert:#d97706   (vàng cam — Vertical group)
--red:#dc2626    --yel:#ca8a04  (freq flags)
```

**Khi muốn thêm cột/metric mới vào campaign table:**
- Tìm function `campTable()` trong index.html (khoảng line 395–430)
- BRAND row: `name | spend | reach | freq_badge | qe | cpe | er`
- GROWTH/VERTICAL row: `name | spend | reach | clicks | ctr | cpc | freq_badge`

---

## 9. Lịch sử & Known Issues

| Vấn đề | Chi tiết |
|---|---|
| Data lịch sử Apr–Jun 2026 | Được backfill thủ công bằng `patch_history.py`. Data có thể thiếu một số trường so với tuần mới (vd: không có demographics). |
| pty_sgd | Paused từ May 11 đến Jun 7, 2026 → spend = 0 các tuần đó. |
| VERTICAL không có QE/CPL thực | Vì API lỗi với action fields → giá trị qe=0, cpl=0 trong nhiều tuần backfill. Chỉ có freq/clicks/cpc. |
| index.json | File này list tất cả weeks có sẵn. Dashboard dùng nó để build dropdown chọn tuần. Mỗi khi thêm file mới phải update index.json. |

---

## 10. Liên hệ

- **Chi** (owner): chile@chotot.vn — quyết định metrics, layout, routine schedule
- **Routine logs**: xem tại https://claude.ai/code/routines/trig_01UvWJuFt54akLLCUssqq6vS
