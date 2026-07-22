# Grouping by Team (dashboard: GROWTH => "Digital" tab).
# Phase (Demand/App) kept as metadata in ACCOUNT_PHASE below.
ACCOUNTS = {
    "BRAND": {
        "gds_brand":        "253279950744492",
        "pty_branding_sgd": "697690298835029",
        "veh_brand":        "937141594251635",
        "job_branding_sgd": "339646702235039",
    },
    "GROWTH": {
        "job_sgd":     "1009648153146994",
        "growth_sgd":  "217167486615130",
        "veh_sgd":     "211751247179666",
        "gds_elt_sgd": "655717678725444",
        "pty_app":     "1924712638163043",
        "job_app":     "1021879607190581",
        "pty_sgd":     "189567943020118",
    },
    "VERTICAL": {
        "pty_seller_sgd": "1632822317085217",
        "job_trade_sgd":  "1581743339281376",
    },
}

# Campaign phase per account: "app" => install/CPI focus, "demand" => link-click/QE focus.
ACCOUNT_PHASE = {
    "job_sgd":     "demand",
    "growth_sgd":  "app",
    "veh_sgd":     "demand",
    "gds_elt_sgd": "demand",
    "pty_app":     "app",
    "job_app":     "app",
    "pty_sgd":     "demand",
    "pty_seller_sgd": "demand",
    "job_trade_sgd":  "demand",
}

NOTION_PAGE_ID = "36fd783d-b335-81b3-8887-e747ec7da455"
NOTION_URL     = "https://app.notion.com/p/36fd783db33581b38887e747ec7da455"

SLACK_DM_SELF      = "D01J9JRNERH"          # Chi Pu self DM
SLACK_CHANNEL_PERF = "C0B93T2655Z"          # #ct-marketing-performance
SLACK_HANG         = "U09FKRCU8JY"          # Hang Le Tuyet

FREQ_GREEN  = 3.0
FREQ_YELLOW = 7.0

META_GRAPH_URL = "https://graph.facebook.com/v21.0"
META_FIELDS = (
    "campaign_id,campaign_name,spend,impressions,reach,clicks,"
    "cpm,cpc,ctr,frequency,actions"
)
