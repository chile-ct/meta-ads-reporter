#!/usr/bin/env python3
"""
Generate rich JSON for Jun 16-22, 2026 week.
Campaign data pulled via Meta MCP. Text generated from data analysis.
Run once: python3 build_jun16_rich.py
"""
import json, os
from pathlib import Path

OUT = Path(__file__).parent / "docs" / "data" / "2026-06-16.json"

# ── Raw campaign data (from MCP pull Jun 16-22) ────────────────────────────
RAW = {
    "gds_brand": [
        {"name":"brand_eng_gds_reward_b2c_0626 - Copy","audience":"consumers · Engagement",
         "spend":66.02,"reach":22226,"impressions":34761,"clicks":488,"ctr":1.40,"cpc":0.14,"cpm":1.90,"freq":1.56,"freq_flag":"✅","qe":5,"cpe":13.20,"er":0.0225},
        {"name":"brand_eng_gds_b2c_0626","audience":"consumers · Engagement",
         "spend":194.12,"reach":106573,"impressions":186108,"clicks":5135,"ctr":2.76,"cpc":0.04,"cpm":1.04,"freq":1.75,"freq_flag":"✅","qe":45,"cpe":4.31,"er":0.0422},
        {"name":"brand_view_livestream_0526_0626","audience":"consumers · Video Views",
         "spend":64.29,"reach":40555,"impressions":47238,"clicks":153,"ctr":0.32,"cpc":0.42,"cpm":1.36,"freq":1.16,"freq_flag":"✅","qe":4,"cpe":16.07,"er":0.0099},
    ],
    "pty_branding_sgd": [
        {"name":"brand_reach_market_index_q1_2026_b2b","audience":"biz/recruiter · AudNet+Feed (Reach)",
         "spend":220.02,"reach":570160,"impressions":733496,"clicks":1122,"ctr":0.15,"cpc":0.20,"cpm":0.30,"freq":1.29,"freq_flag":"✅","qe":82,"cpe":2.68,"er":0.0144},
        {"name":"brand_eng_market_index_q1_2026_b2b","audience":"biz/recruiter · Engagement",
         "spend":139.42,"reach":100896,"impressions":226580,"clicks":4012,"ctr":1.77,"cpc":0.03,"cpm":0.62,"freq":2.25,"freq_flag":"✅","qe":501,"cpe":0.28,"er":0.4966},
        {"name":"brand_eng_sale_pty_b2c_0626","audience":"consumers · Engagement",
         "spend":170.12,"reach":168838,"impressions":292183,"clicks":46327,"ctr":15.86,"cpc":0.00,"cpm":0.58,"freq":1.73,"freq_flag":"✅","qe":273,"cpe":0.62,"er":0.1617},
        {"name":"brand_eng_renter_pty_b2c_0626","audience":"consumers · Engagement",
         "spend":74.13,"reach":118483,"impressions":125543,"clicks":5834,"ctr":4.65,"cpc":0.01,"cpm":0.59,"freq":1.06,"freq_flag":"✅","qe":132,"cpe":0.56,"er":0.1114},
        {"name":"brand_eng_pty_b2b_0626","audience":"biz/recruiter · Engagement",
         "spend":352.50,"reach":253168,"impressions":497873,"clicks":2283,"ctr":0.46,"cpc":0.15,"cpm":0.71,"freq":1.97,"freq_flag":"✅","qe":4,"cpe":88.13,"er":0.0016},
    ],
    "veh_brand": [
        {"name":"brand_eng_veh_b2c_0626","audience":"consumers · Engagement",
         "spend":156.35,"reach":108853,"impressions":158316,"clicks":7277,"ctr":4.60,"cpc":0.02,"cpm":0.99,"freq":1.45,"freq_flag":"✅","qe":78,"cpe":2.00,"er":0.0717},
    ],
    "job_branding_sgd": [
        {"name":"brand_job_eng_b2c_0626","audience":"consumers · Engagement",
         "spend":253.79,"reach":250835,"impressions":357951,"clicks":16801,"ctr":4.69,"cpc":0.02,"cpm":0.71,"freq":1.43,"freq_flag":"✅","qe":556,"cpe":0.46,"er":0.2216},
        {"name":"brand_job_eng_b2b_0626","audience":"biz/recruiter · Engagement",
         "spend":122.86,"reach":73602,"impressions":130644,"clicks":7788,"ctr":5.96,"cpc":0.02,"cpm":0.94,"freq":1.78,"freq_flag":"✅","qe":35,"cpe":3.51,"er":0.0476},
    ],
    "growth_sgd": [
        {"name":"digital_gds_appinstall_fb_atc_broad_040626","audience":"broad · App Install",
         "spend":174.27,"reach":33278,"impressions":55770,"clicks":566,"ctr":1.01,"cpc":0.31,"cpm":3.12,"freq":1.68,"freq_flag":"✅","qe":590,"cpe":0.30,"er":0.0},
        {"name":"digital_gds_appinstall_fb_atc_web_visitor_l180d_040626","audience":"web visitors L180D · App Install",
         "spend":173.38,"reach":22735,"impressions":43077,"clicks":292,"ctr":0.68,"cpc":0.59,"cpm":4.02,"freq":1.89,"freq_flag":"✅","qe":315,"cpe":0.55,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut15_110626","audience":"retargeting · App (live15 test)",
         "spend":19.62,"reach":5323,"impressions":15907,"clicks":102,"ctr":0.64,"cpc":0.19,"cpm":1.23,"freq":2.99,"freq_flag":"✅","qe":102,"cpe":0.19,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut13_110626","audience":"retargeting · App (live13 test)",
         "spend":20.09,"reach":4603,"impressions":11282,"clicks":53,"ctr":0.47,"cpc":0.38,"cpm":1.78,"freq":2.45,"freq_flag":"✅","qe":53,"cpe":0.38,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut12_110626","audience":"retargeting · App (live12 test)",
         "spend":19.35,"reach":2960,"impressions":7776,"clicks":6,"ctr":0.08,"cpc":3.23,"cpm":2.49,"freq":2.63,"freq_flag":"✅","qe":7,"cpe":2.76,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut21","audience":"retargeting · App (live test)",
         "spend":10.10,"reach":2424,"impressions":4538,"clicks":39,"ctr":0.86,"cpc":0.26,"cpm":2.23,"freq":1.87,"freq_flag":"✅","qe":40,"cpe":0.25,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut20","audience":"retargeting · App (live test)",
         "spend":10.05,"reach":3232,"impressions":6596,"clicks":32,"ctr":0.49,"cpc":0.31,"cpm":1.52,"freq":2.04,"freq_flag":"✅","qe":34,"cpe":0.30,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut19","audience":"retargeting · App (live test)",
         "spend":10.44,"reach":2519,"impressions":4903,"clicks":20,"ctr":0.41,"cpc":0.52,"cpm":2.13,"freq":1.95,"freq_flag":"✅","qe":20,"cpe":0.52,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut18","audience":"retargeting · App (live test)",
         "spend":10.47,"reach":3066,"impressions":5824,"clicks":25,"ctr":0.43,"cpc":0.42,"cpm":1.80,"freq":1.90,"freq_flag":"✅","qe":26,"cpe":0.40,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut17","audience":"retargeting · App (live test)",
         "spend":10.31,"reach":1828,"impressions":3458,"clicks":10,"ctr":0.29,"cpc":1.03,"cpm":2.98,"freq":1.89,"freq_flag":"✅","qe":10,"cpe":1.03,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live_shortcut16_110626","audience":"retargeting · App (live16 test)",
         "spend":3.28,"reach":1140,"impressions":1685,"clicks":9,"ctr":0.53,"cpc":0.36,"cpm":1.95,"freq":1.48,"freq_flag":"✅","qe":9,"cpe":0.36,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live10s_shortcut19","audience":"retargeting · App (live10s test)",
         "spend":5.09,"reach":1136,"impressions":2176,"clicks":4,"ctr":0.18,"cpc":1.27,"cpm":2.34,"freq":1.92,"freq_flag":"✅","qe":4,"cpe":1.27,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live10s_shortcut21","audience":"retargeting · App (live10s test)",
         "spend":3.80,"reach":860,"impressions":1493,"clicks":17,"ctr":1.14,"cpc":0.22,"cpm":2.55,"freq":1.74,"freq_flag":"✅","qe":17,"cpe":0.22,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live10s_shortcut20","audience":"retargeting · App (live10s test)",
         "spend":3.04,"reach":951,"impressions":1656,"clicks":4,"ctr":0.24,"cpc":0.76,"cpm":1.84,"freq":1.74,"freq_flag":"✅","qe":5,"cpe":0.61,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live10s_shortcut17","audience":"retargeting · App (live10s test)",
         "spend":5.65,"reach":1103,"impressions":2387,"clicks":10,"ctr":0.42,"cpc":0.57,"cpm":2.37,"freq":2.16,"freq_flag":"✅","qe":10,"cpe":0.57,"er":0.0},
        {"name":"digital_gds_appinstall_fb_test_retar_live10s_shortcut18","audience":"retargeting · App (live10s test)",
         "spend":3.14,"reach":826,"impressions":1588,"clicks":7,"ctr":0.44,"cpc":0.45,"cpm":1.98,"freq":1.92,"freq_flag":"✅","qe":7,"cpe":0.45,"er":0.0},
    ],
    "job_sgd": [
        {"name":"digital_fb_job_nvkd","audience":"biz dev · Web link",
         "spend":78.07,"reach":7771,"impressions":59748,"clicks":1370,"ctr":2.29,"cpc":0.06,"cpm":1.31,"freq":7.69,"freq_flag":"🔴","qe":1097,"cpe":0.07,"er":14.12},
        {"name":"digital_fb_job_taixe","audience":"drivers · Web link",
         "spend":13.89,"reach":4325,"impressions":9495,"clicks":1345,"ctr":14.17,"cpc":0.01,"cpm":1.46,"freq":2.20,"freq_flag":"✅","qe":1236,"cpe":0.01,"er":28.58},
        {"name":"digital_fb_job_shipper","audience":"shippers · Web link",
         "spend":23.98,"reach":4065,"impressions":17351,"clicks":1465,"ctr":8.44,"cpc":0.02,"cpm":1.38,"freq":4.27,"freq_flag":"🟡","qe":1545,"cpe":0.02,"er":38.01},
        {"name":"digital_fb_job_nvpv","audience":"service staff · Web link",
         "spend":13.96,"reach":4261,"impressions":7926,"clicks":650,"ctr":8.20,"cpc":0.02,"cpm":1.76,"freq":1.86,"freq_flag":"✅","qe":837,"cpe":0.02,"er":19.64},
        {"name":"digital_fb_job_nvkv","audience":"sales staff · Web link",
         "spend":14.08,"reach":3956,"impressions":7896,"clicks":814,"ctr":10.31,"cpc":0.02,"cpm":1.78,"freq":2.00,"freq_flag":"✅","qe":748,"cpe":0.02,"er":18.91},
        {"name":"digital_fb_job_worker","audience":"general workers · Web link",
         "spend":41.64,"reach":7173,"impressions":31979,"clicks":3250,"ctr":10.16,"cpc":0.01,"cpm":1.30,"freq":4.46,"freq_flag":"🟡","qe":3720,"cpe":0.01,"er":51.86},
        {"name":"digital_fb_job_banhang","audience":"retail staff · Web link",
         "spend":51.94,"reach":7571,"impressions":32356,"clicks":2422,"ctr":7.49,"cpc":0.02,"cpm":1.61,"freq":4.27,"freq_flag":"🟡","qe":2441,"cpe":0.02,"er":32.24},
        {"name":"digital_fb_job_baove","audience":"security staff · Web link",
         "spend":57.65,"reach":7685,"impressions":31929,"clicks":3170,"ctr":9.93,"cpc":0.02,"cpm":1.81,"freq":4.15,"freq_flag":"🟡","qe":3019,"cpe":0.02,"er":39.28},
    ],
    "gds_elt_sgd": [
        {"name":"digital_elt_bl_tf_engage_video_sănĐT","audience":"smartphone buyers · TF Video Engagement",
         "spend":58.83,"reach":91414,"impressions":122354,"clicks":2913,"ctr":2.38,"cpc":0.02,"cpm":0.48,"freq":1.34,"freq_flag":"✅","qe":340,"cpe":0.17,"er":0.37},
        {"name":"digital_elt_fb_web_rtg","audience":"retargeting · Web link",
         "spend":70.07,"reach":32292,"impressions":125482,"clicks":4660,"ctr":3.71,"cpc":0.02,"cpm":0.56,"freq":3.89,"freq_flag":"🟡","qe":4231,"cpe":0.02,"er":13.10},
        {"name":"digital_elt_bl_mf_clicklink_web","audience":"electronics · MF Click Link (web)",
         "spend":215.85,"reach":23394,"impressions":171926,"clicks":14504,"ctr":8.44,"cpc":0.01,"cpm":1.26,"freq":7.35,"freq_flag":"🔴","qe":11654,"cpe":0.02,"er":49.82},
        {"name":"digital_elt_bl_tf_engagement_sănĐT","audience":"smartphone buyers · TF Engagement",
         "spend":78.79,"reach":122311,"impressions":142058,"clicks":29968,"ctr":21.10,"cpc":0.00,"cpm":0.55,"freq":1.16,"freq_flag":"✅","qe":501,"cpe":0.16,"er":0.41},
    ],
}

ACCOUNT_GROUPS = {
    "gds_brand": "BRAND", "pty_branding_sgd": "BRAND",
    "veh_brand": "BRAND", "job_branding_sgd": "BRAND",
    "growth_sgd": "GROWTH", "job_sgd": "GROWTH", "gds_elt_sgd": "GROWTH",
}

BRAND_ACCTS   = ["gds_brand","pty_branding_sgd","veh_brand","job_branding_sgd"]
GROWTH_ACCTS  = ["growth_sgd","job_sgd","gds_elt_sgd"]

def agg(camps):
    sp  = sum(c["spend"] for c in camps)
    rch = sum(c["reach"] for c in camps)
    imp = sum(c["impressions"] for c in camps)
    clk = sum(c["clicks"] for c in camps)
    qe  = sum(c["qe"] for c in camps)
    return dict(
        spend=round(sp,2), reach=rch, impressions=imp, clicks=clk,
        qe=qe,
        cpe=round(sp/qe,2) if qe else 0,
        er=round(qe/rch*100,4) if rch else 0,
        avg_freq=round(imp/rch,2) if rch else 0,
        cpm=round(sp/imp*1000,2) if imp else 0,
        cpc=round(sp/clk,2) if clk else 0,
        ctr=round(clk/imp*100,2) if imp else 0,
        active_camps=len(camps),
        red_freq_camps=sum(1 for c in camps if c["freq"]>=7),
    )

# ── Per-account data ───────────────────────────────────────────────────────
def build_account(acct_name, group_type):
    camps = RAW[acct_name]
    a = agg(camps)
    a["campaigns"] = [dict(c) for c in camps]

    if group_type == "BRAND":
        a["recommendations"] = RECO_BRAND[acct_name]
        a["objective"] = "Engagement / Reach"
    else:
        a["recommendations"] = RECO_GROWTH[acct_name]
        a["objective"] = "Traffic / App Events"
    return a

# ── Per-account recommendations ───────────────────────────────────────────
RECO_BRAND = {
    "gds_brand": [
        "CPE SGD 6.01 và ER 0.032% đều dưới benchmark của Brand group — creative chưa resonant. Test UGC hoặc format trực tiếp hơn (product-reward, testimonial).",
        "brand_eng_gds_reward_b2c_0626 - Copy chỉ đạt 5 QE ở CPE SGD 13.20, tệ hơn 3× so với campaign chính (CPE 4.31). Pause copy variant, redirect ngân sách về main b2c campaign.",
        "brand_view_livestream_0526_0626 chỉ đạt 4 QE với CPE cao nhất (SGD 16.07) — ROI thấp nhất trong account. Đánh giá xem format livestream có phù hợp với mục tiêu QE không.",
        "Reach 169K với avg freq 1.58 ✅ còn nhiều headroom — có thể mở rộng audience hoặc layer lookalike để tăng scale mà không bị saturation.",
        "Đặt weekly QE floor target cho gds_brand; pace hiện tại 54 QE/tuần quá thấp để đo lường brand signal có ý nghĩa.",
    ],
    "pty_branding_sgd": [
        "🚨 brand_eng_pty_b2b_0626 tiêu SGD 352.50 nhưng chỉ đạt 4 QE (CPE SGD 88.13, ER 0.0016%) — pause hoặc overhaul creative ngay lập tức. Kiểm tra campaign objective có đang optimize cho Engagement không.",
        "brand_eng_market_index_q1_2026_b2b là ngôi sao của account: CPE SGD 0.28, ER 0.497%, 501 QE — ứng viên hàng đầu để tăng budget 20–30% từ campaign b2b đang underperform.",
        "brand_eng_renter_pty_b2c_0626 ở freq 1.06 ✅ với CPE SGD 0.56 và 132 QE — hiệu suất tốt, còn nhiều room to scale trước khi đụng ngưỡng 🟡.",
        "brand_eng_sale_pty_b2c_0626 tạo 46K+ clicks với CTR 15.86% — message property sale đang resonant mạnh với audience; cân nhắc tăng budget cho campaign này.",
        "Reallocate 40% ngân sách của brand_eng_pty_b2b_0626 về market_index b2b engagement campaign để cải thiện account CPE tổng thể.",
    ],
    "veh_brand": [
        "Campaign duy nhất đang chạy tốt: 108K reach, freq 1.45 ✅, CPE SGD 2.00 — nhưng ER (0.072%) vẫn dưới benchmark Brand group.",
        "78 QE từ 108K reach — mật độ QE thấp. Test creative format mạnh hơn (video với product features, comparison trước/sau, UGC).",
        "Frequency vẫn xa ngưỡng ✅, audience headroom rộng — opportunity tăng budget 30–50% trước khi đạt 🟡 zone.",
        "CTR 4.60% cao nhất trong Brand accounts — audience đang click nhưng không engage sâu; cải thiện landing experience hoặc thêm save/share incentive trong ad.",
        "Test thêm creative variant (B2B dealer-facing hoặc seasonal) để segment messaging và cải thiện QE depth.",
    ],
    "job_branding_sgd": [
        "Account hiệu quả nhất trong Brand group: CPE SGD 0.64 blended, 591 QE, 324K reach ở avg freq 1.55 ✅.",
        "B2C campaign dẫn đầu QE (556) trong account với frequency headroom rộng — scale ngân sách ở đây trước.",
        "B2B campaign có QE yếu (35, CPE SGD 3.51) so với B2C — review creative và targeting B2B; chỉ đang reach 73K (22% tổng reach của account).",
        "Cả 2 campaigns đều ở ✅ frequency với audience pool rộng — account có thể hấp thụ thêm ngân sách đáng kể trước khi saturation.",
        "Build lookalike audience từ B2C engaged users (556 QE interactions = strong intent signal) để mở rộng prospecting pool.",
    ],
}

RECO_GROWTH = {
    "growth_sgd": [
        "16 campaigns đang chạy nhưng phần lớn ngân sách (SGD 347.65, 72%) nằm ở 2 ATC campaigns; 14 test campaigns còn lại (mỗi cái SGD 3–20) là performance tests không hiệu quả.",
        "Không ghi nhận Mobile App Installs — verify pixel/event setup cho app install objective và xác nhận Events Manager đang track Install events đúng cách.",
        "digital_gds_appinstall_fb_atc_broad_040626 (CPM SGD 3.12) và web_visitor (CPM SGD 4.02) carry the account; web_visitor CPM cao hơn 29% do narrow retargeting audience — monitor cost inflation.",
        "Pause 14 small test campaigns (SGD 0–20, CTR và install thấp) và consolidate ngân sách vào một prospecting App Install campaign mới với broader audience.",
        "shortcut15 test (102 QE, CPE SGD 0.19) có potential nhưng cần scale để validate — test với budget lớn hơn trong 1 tuần trước khi quyết định.",
    ],
    "job_sgd": [
        "🚨 digital_fb_job_nvkd ở freq 7.69 🔴: 7.7K audience đã thấy ad này ~8× trong 1 tuần. Pause ngay và rebuild với broader biz-dev audience pool.",
        "digital_fb_job_taixe là ngôi sao: CTR 14.17%, CPC SGD 0.01, 1,236 QE ở freq 2.20 ✅ — ứng viên hàng đầu để scale ngân sách trước khi saturation.",
        "digital_fb_job_shipper (freq 4.27 🟡) và digital_fb_job_worker (freq 4.46 🟡) đang tiến gần ngưỡng đỏ — mở rộng audience pools ngay bây giờ.",
        "digital_fb_job_baove (SGD 57.65, 3,019 QE, freq 4.15 🟡) có engagement potential mạnh; mở rộng audience trước khi frequency leo thang thêm.",
        "Redistribute ngân sách của nvkd (SGD 78.07) sang taixe và nvkv — frequency headroom tốt và message relevance đã được chứng minh.",
    ],
    "gds_elt_sgd": [
        "🚨 digital_elt_bl_mf_clicklink_web ở freq 7.35 🔴: 23K audience pool đã xem ~7× với SGD 215.85 (51% account budget). Expand audience hoặc giảm budget ngay lập tức.",
        "digital_elt_bl_tf_engagement_sănĐT xuất sắc: CTR 21.10%, near-zero CPC, 122K reach ở freq 1.16 ✅ — tăng budget allocation ngay.",
        "digital_elt_fb_web_rtg tiến gần yellow (freq 3.89 🟡) — mở rộng retargeting lookback window trước khi saturation xảy ra trong tuần tới.",
        "Build custom audience từ video viewers của digital_elt_bl_tf_engage_video_sănĐT (91K viewers, freq 1.34) làm warm retargeting pool để cải thiện funnel progression.",
        "Rebalance: cap bl_mf_clicklink_web ở ≤25% account spend và redirect vào 2 campaigns ✅ engagement đang hiệu quả.",
    ],
}

# ── Group level ───────────────────────────────────────────────────────────
def build_group_brand():
    accounts = {}
    all_camps = []
    for a in BRAND_ACCTS:
        ac = build_account(a, "BRAND")
        accounts[a] = ac
        all_camps += RAW[a]
    g = agg(all_camps)
    g["objective"] = "Engagement / Reach"
    g["key_highlight"] = (
        "Brand group chạy clean — tất cả 11 campaigns ở ✅ frequency zone. "
        "Action cần thiết: review brand_eng_pty_b2b_0626 (SGD 352.50 spend / 4 QE / CPE SGD 88.13). "
        "job_branding_sgd là efficiency leader (SGD 0.64 CPE); pty_branding_sgd dẫn về scale (1.2M unique reach). "
        "Cơ hội ngay: reallocate ngân sách pty_branding_sgd từ b2b engagement campaign về b2b market index campaign."
    )
    g["accounts"] = accounts
    return g

def build_group_growth():
    accounts = {}
    all_camps = []
    for a in GROWTH_ACCTS:
        ac = build_account(a, "GROWTH")
        accounts[a] = ac
        all_camps += RAW[a]
    g = agg(all_camps)
    g["objective"] = "Traffic / App Events"
    g["installs"] = 0
    g["cpi"] = 0
    g["per_account_insights"] = [
        "growth_sgd: 16 campaigns nhưng chỉ 2 có meaningful spend. Không có Mobile App Installs — verify pixel và campaign objective. CPM cao (SGD 3–4) do narrow retargeting audiences.",
        "job_sgd: CTR 7.96% trung bình và CPC SGD 0.02 cho thấy message resonance tốt — vấn đề là audience exhaustion, không phải creative. Urgently expand pools cho nvkd (🔴), worker và shipper (🟡).",
        "gds_elt_sgd: Account hiệu quả nhất về scale (269K reach, 52K clicks, CPC SGD 0.01) nhưng bl_mf_clicklink_web (freq 7.35 🔴) đang kéo xuống. Average account (2.09 ✅) được offset bởi 2 broad campaigns.",
    ]
    g["accounts"] = accounts
    return g

RAW_JOB_TRADE = [
    {"name":"job_recruiter_growth_jun26_sales","audience":"sales · Traffic",
     "spend":45.46,"reach":12250,"impressions":100641,"clicks":274,"ctr":0.27,"cpc":0.17,"cpm":0.45,"freq":8.22,"freq_flag":"🔴","qe":274,"cpe":0.17,"er":2.24},
    {"name":"job_recruiter_growth_AWO_reach_new","audience":"broad · Reach",
     "spend":40.89,"reach":31557,"impressions":67697,"clicks":248,"ctr":0.37,"cpc":0.16,"cpm":0.60,"freq":2.15,"freq_flag":"✅","qe":248,"cpe":0.16,"er":0.79},
    {"name":"job_recruiter_webinarAI_engagement","audience":"biz · Engagement",
     "spend":39.64,"reach":26334,"impressions":28996,"clicks":188,"ctr":0.65,"cpc":0.21,"cpm":1.37,"freq":1.10,"freq_flag":"✅","qe":188,"cpe":0.21,"er":0.71},
    {"name":"job_recruiter_webinarAI_leadform","audience":"biz · Lead gen",
     "spend":120.02,"reach":22573,"impressions":40998,"clicks":375,"ctr":0.91,"cpc":0.32,"cpm":2.93,"freq":1.82,"freq_flag":"✅","qe":375,"cpe":0.32,"er":1.66},
    {"name":"job_recruiter_webinarAI_leadform - Copy","audience":"biz · Lead gen",
     "spend":76.67,"reach":19011,"impressions":27836,"clicks":189,"ctr":0.68,"cpc":0.41,"cpm":2.75,"freq":1.46,"freq_flag":"✅","qe":189,"cpe":0.41,"er":0.99},
    {"name":"job_recruiter_growth_referral_jun26","audience":"referral · Traffic",
     "spend":34.51,"reach":5926,"impressions":58552,"clicks":157,"ctr":0.27,"cpc":0.22,"cpm":0.59,"freq":9.88,"freq_flag":"🔴","qe":157,"cpe":0.22,"er":2.65},
    {"name":"job_recruiter_growth_may-jun26_sales","audience":"sales · Traffic",
     "spend":34.12,"reach":9823,"impressions":94260,"clicks":188,"ctr":0.20,"cpc":0.18,"cpm":0.36,"freq":9.60,"freq_flag":"🔴","qe":188,"cpe":0.18,"er":1.91},
    {"name":"job_recruiter_growth_AWO_reach","audience":"broad · Reach",
     "spend":70.49,"reach":119903,"impressions":179632,"clicks":463,"ctr":0.26,"cpc":0.15,"cpm":0.39,"freq":1.50,"freq_flag":"✅","qe":463,"cpe":0.15,"er":0.39},
]

def build_group_vertical():
    jt_camps = RAW_JOB_TRADE
    tot_s  = sum(c["spend"] for c in jt_camps)
    tot_r  = sum(c["reach"] for c in jt_camps)
    tot_i  = sum(c["impressions"] for c in jt_camps)
    tot_cl = sum(c["clicks"] for c in jt_camps)
    tot_qe = sum(c["qe"] for c in jt_camps)
    af     = round(tot_i / tot_r, 2) if tot_r else 0
    red    = sum(1 for c in jt_camps if c["freq"] >= 7)
    return {
        "spend": round(tot_s, 2),
        "reach": tot_r,
        "impressions": tot_i,
        "clicks": tot_cl,
        "qe": tot_qe,
        "cpe": round(tot_s / tot_qe, 2) if tot_qe else 0,
        "er": round(tot_qe / tot_r * 100, 4) if tot_r else 0,
        "avg_freq": af,
        "freq_flag": "🟡",
        "cpm": round(tot_s / tot_i * 1000, 2) if tot_i else 0,
        "cpc": round(tot_s / tot_cl, 2) if tot_cl else 0,
        "ctr": round(tot_cl / tot_i * 100, 2) if tot_i else 0,
        "active_camps": len(jt_camps),
        "red_freq_camps": red,
        "objective": "Traffic / Lead gen",
        "accounts": {
            "job_trade_sgd": {
                "spend": round(tot_s, 2), "reach": tot_r, "impressions": tot_i,
                "clicks": tot_cl, "qe": tot_qe,
                "cpe": round(tot_s / tot_qe, 2) if tot_qe else 0,
                "er": round(tot_qe / tot_r * 100, 4) if tot_r else 0,
                "avg_freq": af, "cpm": round(tot_s / tot_i * 1000, 2) if tot_i else 0,
                "cpc": round(tot_s / tot_cl, 2) if tot_cl else 0,
                "ctr": round(tot_cl / tot_i * 100, 2) if tot_i else 0,
                "active_camps": len(jt_camps), "red_freq_camps": red,
                "objective": "Traffic / Lead gen",
                "campaigns": jt_camps,
                "recommendations": [
                    "3 campaigns ở freq 🔴 (≥7×): jun26_sales (8.22×), referral_jun26 (9.88×), may-jun26_sales (9.60×). Pause ngay — audience pool quá nhỏ (<13K reach). Rebuild với AWO hoặc Advantage+ audience mở rộng.",
                    "webinarAI_leadform là top spender (SGD 120.02, freq 1.82 ✅, CTR 0.91%) — campaign đang perform tốt. Scale thêm 20–30% budget tuần tới.",
                    "webinarAI_leadform - Copy chạy song song (SGD 76.67, CTR 0.68%). A/B test creative và kill bản yếu hơn sau 2 tuần để tránh self-competition.",
                    "AWO_reach là nền tảng tốt nhất về scale (119K reach, CPC SGD 0.15, freq 1.50 ✅). Tăng budget và dùng custom audience từ converters làm exclusion.",
                    "Reallocate ngân sách từ 3 campaigns 🔴 (~SGD 114) vào 2 webinarAI campaigns và AWO_reach để cải thiện overall efficiency.",
                ],
            },
            "pty_sgd": {"spend": 0, "note": "Không có active campaigns tuần này. Kiểm tra campaign schedule và budget allocation."},
        },
    }

# ── Watch list ─────────────────────────────────────────────────────────────
WATCH_LIST_ACTIONS = {
    "digital_fb_job_nvkd":                        "Pause ngay — rebuild với broader biz-dev audience",
    "digital_elt_bl_mf_clicklink_web":             "Expand audience hoặc giảm budget ngay lập tức",
    "digital_fb_job_worker":                       "Expand audience hoặc rotate creative",
    "digital_fb_job_banhang":                      "Theo dõi — expand audience trước khi breach 🔴",
    "digital_fb_job_shipper":                      "Theo dõi — expand audience trước khi breach 🔴",
    "digital_fb_job_baove":                        "Pre-emptive: refresh audience ngay tuần này",
    "digital_elt_fb_web_rtg":                      "Mở rộng retargeting lookback window",
    "job_recruiter_growth_referral_jun26":         "Pause ngay — reach 5.9K, freq 9.88×. Rebuild audience pool",
    "job_recruiter_growth_may-jun26_sales":        "Pause ngay — reach 9.8K, freq 9.60×. Mở rộng targeting",
    "job_recruiter_growth_jun26_sales":            "Pause hoặc reset audience — reach 12.3K, freq 8.22×",
}

def build_watch_list():
    items = []
    all_sources = list(RAW.items()) + [("job_trade_sgd", RAW_JOB_TRADE)]
    for acct_name, camps in all_sources:
        group = ACCOUNT_GROUPS.get(acct_name, "VERTICAL")
        for c in camps:
            if c["freq"] >= 3:
                items.append({
                    "account": acct_name,
                    "group": group,
                    "name": c["name"],
                    "frequency": c["freq"],
                    "freq_flag": c["freq_flag"],
                    "reach": c["reach"],
                    "spend": c["spend"],
                    "action": WATCH_LIST_ACTIONS.get(c["name"], "Theo dõi và cân nhắc refresh creative"),
                })
    items.sort(key=lambda x: x["frequency"], reverse=True)
    return items

# ── Key insights ──────────────────────────────────────────────────────────
KEY_INSIGHTS = [
    "Brand: Tất cả 11 campaigns ở ✅ frequency zone (avg 1.54). brand_eng_pty_b2b_0626 là outlier nghiêm trọng: SGD 352.50 cho 4 QE (CPE SGD 88.13). job_branding_sgd dẫn đầu efficiency (SGD 0.64 CPE); pty_branding_sgd dẫn đầu scale (1.2M unique reach).",
    "Digital: job_sgd có digital_fb_job_nvkd ở freq 7.69 🔴 — cần pause ngay. gds_elt_sgd's bl_mf_clicklink_web (freq 7.35 🔴) chiếm 51% account budget với chỉ 23K audience pool. Không ghi nhận App Installs — verify pixel configuration.",
    "Vertical: job_trade_sgd có SGD 461.80 spend, 8 campaigns, 3 ở freq 🔴 (≥7×: referral_jun26 9.88, may-jun26_sales 9.60, jun26_sales 8.22). Webinar campaigns đang perform tốt (CTR ~0.9%). pty_sgd không có spend tuần này.",
    "Overall: 5 campaigns 🔴 cross 3 accounts (job_sgd, gds_elt_sgd, job_trade_sgd). Tổng spend ở risk: >SGD 400 (~12% tổng budget). Priority: pause 3 campaigns Vertical freq ≥7× và 2 campaigns Digital freq ≥7×.",
]

# ── Build final JSON ──────────────────────────────────────────────────────
brand_group  = build_group_brand()
growth_group = build_group_growth()
vert_group   = build_group_vertical()

total_spend = round(brand_group["spend"] + growth_group["spend"] + vert_group["spend"], 2)
wl = build_watch_list()
red_count = sum(1 for w in wl if w["freq_flag"] == "🔴")
red_spend  = round(sum(w["spend"] for w in wl if w["freq_flag"] == "🔴"), 2)
red_pct    = round(red_spend / total_spend * 100, 1) if total_spend else 0

snapshot = {
    "week_start": "2026-06-16",
    "week_label": "Jun 16–22, 2026",
    "total_spend": total_spend,
    "generated_at": "2026-06-23T09:00:00+07:00",
    "detail_available": True,
    "header_note": f"⚡ Auto-updated every Monday 9:00 AM ICT · Kỳ: Jun 16–22, 2026 · Accounts: 9 · QE = Comment+Share+Save+Link Click · Freq: ✅<3 🟡3–6 🔴≥7",
    "key_insights": KEY_INSIGHTS,
    "watch_list_summary": f"{red_count} camps 🔴 · SGD {red_spend:,.2f} · {red_pct}% of GROWTH budget at risk",
    "groups": {
        "BRAND":    brand_group,
        "GROWTH":   growth_group,
        "VERTICAL": vert_group,
    },
    "watch_list": wl,
}

OUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
print(f"✓ Written {OUT}")
print(f"  BRAND:  SGD {brand_group['spend']:,.2f}  QE={brand_group['qe']}  camps={brand_group['active_camps']}")
print(f"  GROWTH: SGD {growth_group['spend']:,.2f}  clicks={growth_group['clicks']}  camps={growth_group['active_camps']}")
print(f"  Watch list: {len(wl)} items, {red_count} 🔴")
