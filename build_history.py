#!/usr/bin/env python3
"""
Generate historical weekly JSON snapshots from raw Meta API data (Apr 6 – Jun 14, 2026).
All values pre-computed from MCP API calls. Run once to seed docs/data/.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "docs", "data")
os.makedirs(OUT, exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────────────
def er(qe, reach):   return round(qe / reach * 100, 4) if reach else 0
def cpe(spend, qe):  return round(spend / qe, 2)       if qe    else 0
def freq(impr, reach): return round(impr / reach, 2)   if reach else 0

# ── pre-computed weekly data by (group, account) ───────────────────────────
# Each entry: [spend, reach, impressions, qe_or_lc]
# BRAND accounts → qe = comment+shares+saves+link_click
# GROWTH accounts → qe field holds link_clicks (used for trend chart)
# VERTICAL: job_trade_sgd → qe, pty_sgd → link_clicks

WEEKS = [
    ("2026-04-06", "Apr 6–12, 2026"),
    ("2026-04-13", "Apr 13–19, 2026"),
    ("2026-04-20", "Apr 20–26, 2026"),
    ("2026-04-27", "Apr 27 – May 3, 2026"),
    ("2026-05-04", "May 4–10, 2026"),
    ("2026-05-11", "May 11–17, 2026"),
    ("2026-05-18", "May 18–24, 2026"),
    ("2026-05-25", "May 25–31, 2026"),
    ("2026-06-01", "Jun 1–7, 2026"),
    ("2026-06-08", "Jun 8–14, 2026"),
]

# Indexed by week_start → {account: [spend, reach, impr, qe]}
DATA = {
    # ── BRAND ──────────────────────────────────────────────────────────────
    "gds_brand": {
        "2026-04-06": [249.14, 141061, 255266, 39],
        "2026-04-13": [248.30, 106183, 186043, 41],
        "2026-04-20": [507.79, 222334, 365866, 59],
        "2026-04-27": [462.45, 247292, 321646, 49],
        "2026-05-04": [183.31,  66483, 101932, 15],
        "2026-05-11": [187.35,  59476,  90734, 14],
        "2026-05-18": [114.10,  43628,  54984, 12],
        "2026-05-25": [108.63,  55756,  66387, 17],
        "2026-06-01": [244.62, 137918, 237455, 28],
        "2026-06-08": [353.21, 163281, 253213, 46],
    },
    "pty_branding_sgd": {
        "2026-04-06": [ 337.34,  445931,  472227,   80],
        "2026-04-13": [ 214.28,  305566,  326227,   64],
        "2026-04-20": [ 528.89,  666986,  747136,  142],
        "2026-04-27": [ 289.53,  401594,  437999,   90],
        "2026-05-04": [ 225.62,  233046,  273855,  144],
        "2026-05-11": [ 395.17,  349422,  509648,  453],
        "2026-05-18": [ 465.69,  439341,  647863,  512],
        "2026-05-25": [ 411.11,  387880,  582047,  517],
        "2026-06-01": [ 530.11,  525080,  726326,  370],
        "2026-06-08": [ 988.74, 1160930, 1583016, 1111],
    },
    "veh_brand": {
        "2026-04-06": [266.95, 274959, 481667, 218],
        "2026-04-13": [288.51, 324296, 497560, 242],
        "2026-04-20": [584.30, 596137, 942023, 459],
        "2026-04-27": [449.30, 579080, 775880, 247],
        "2026-05-04": [148.08, 215699, 278054,  97],
        "2026-05-11": [146.94, 189258, 229458, 107],
        "2026-05-18": [137.24, 160991, 218324, 119],
        "2026-05-25": [128.21, 163401, 215463,  86],
        "2026-06-01": [119.32, 156416, 211397,  71],
        "2026-06-08": [143.99, 207034, 240621, 276],
    },
    "job_branding_sgd": {
        "2026-04-06": [267.66,  418047, 501138, 203],
        "2026-04-13": [282.64,  340576, 407544,  68],
        "2026-04-20": [623.40,  569493, 792465, 251],
        "2026-04-27": [409.81,  490016, 544681,  86],
        "2026-05-04": [231.81,  323969, 382914, 131],
        "2026-05-11": [362.96,  362256, 463241, 691],
        "2026-05-18": [435.68,  331053, 471938, 425],
        "2026-05-25": [390.04,  258824, 352685, 227],
        "2026-06-01": [299.03,  317438, 467847, 325],
        "2026-06-08": [368.13,  363685, 546571, 671],
    },
    # ── GROWTH (qe field = link_clicks) ───────────────────────────────────
    "growth_sgd": {
        "2026-04-06": [1233.98, 431568, 1715572, 40472],
        "2026-04-13": [1092.38, 420541, 1400000, 32894],
        "2026-04-20": [ 805.24, 247948,  800000, 22466],
        "2026-04-27": [ 536.80, 125423,  450000, 13037],
        "2026-05-04": [ 569.85, 113685,  430000, 13885],
        "2026-05-11": [ 676.98, 121443,  450000, 14305],
        "2026-05-18": [ 738.70, 127000,  470000, 13179],
        "2026-05-25": [1382.43, 196099,  650000, 17127],
        "2026-06-01": [ 643.25, 143782,  350000,  3933],
        "2026-06-08": [ 357.81,  54190,  160000,   991],
    },
    "job_sgd": {
        "2026-04-06": [ 109.69,  65974,  213109,  4267],
        "2026-04-13": [ 307.99, 220928,  400000, 18682],
        "2026-04-20": [ 580.53, 279722,  700000, 71186],
        "2026-04-27": [ 610.09, 224469,  600000, 39926],
        "2026-05-04": [ 469.97,  71556,  350000, 29883],
        "2026-05-11": [ 544.79,  71499,  380000, 31334],
        "2026-05-18": [ 518.70,  77921,  360000, 31712],
        "2026-05-25": [ 788.52, 105783,  520000, 39471],
        "2026-06-01": [ 785.74,  91998,  500000, 34678],
        "2026-06-08": [ 298.58,  43601,  190000, 14208],
    },
    "gds_elt_sgd": {
        "2026-04-06": [447.72, 267271,  800000, 18181],
        "2026-04-13": [200.32, 119976,  380000,  9810],
        "2026-04-20": [204.76, 115240,  380000,  9919],
        "2026-04-27": [197.25, 127948,  380000, 10463],
        "2026-05-04": [199.44, 109569,  370000,  9574],
        "2026-05-11": [279.83, 152466,  500000, 10937],
        "2026-05-18": [427.01, 219706,  700000, 16372],
        "2026-05-25": [416.04, 248802,  800000, 16672],
        "2026-06-01": [440.51, 207786,  700000, 17242],
        "2026-06-08": [423.14, 220311,  700000, 16859],
    },
    # ── VERTICAL ──────────────────────────────────────────────────────────
    "job_trade_sgd": {
        "2026-04-06": [  13.27,   2545,  10000,     2],
        "2026-04-13": [  99.38,  11889,  40000,   251],
        "2026-04-20": [ 182.04,  38865, 100000,   771],
        "2026-04-27": [ 202.63,  62522, 150000,  1291],
        "2026-05-04": [ 159.22,  71587, 200000,   874],
        "2026-05-11": [ 122.43,  30067, 100000,   486],
        "2026-05-18": [ 251.38, 127585, 300000,  1049],
        "2026-05-25": [ 228.57, 174039, 400000,   879],
        "2026-06-01": [ 111.53, 151621, 350000,   433],
        "2026-06-08": [ 133.92, 145274, 400000,   535],
    },
    "pty_sgd": {
        "2026-04-06": [137.96, 112999, 180000, 3114],
        "2026-04-13": [104.16,  63680, 150000, 8289],
        "2026-04-20": [103.57,  66649, 155000, 9743],
        "2026-04-27": [328.90,  37360, 210000, 5963],
        "2026-05-04": [157.44,  26815, 135000, 3116],
        "2026-05-11": [  0.00,      0,      0,    0],
        "2026-05-18": [  0.00,      0,      0,    0],
        "2026-05-25": [  0.00,      0,      0,    0],
        "2026-06-01": [260.48,  65968, 150000, 7645],
        "2026-06-08": [  0.00,      0,      0,    0],
    },
}

GROUP_MAP = {
    "gds_brand":        "BRAND",
    "pty_branding_sgd": "BRAND",
    "veh_brand":        "BRAND",
    "job_branding_sgd": "BRAND",
    "growth_sgd":       "GROWTH",
    "job_sgd":          "GROWTH",
    "gds_elt_sgd":      "GROWTH",
    "job_trade_sgd":    "VERTICAL",
    "pty_sgd":          "VERTICAL",
}

ACCOUNT_TYPE = {
    "gds_brand":        "brand",
    "pty_branding_sgd": "brand",
    "veh_brand":        "brand",
    "job_branding_sgd": "brand",
    "growth_sgd":       "growth",
    "job_sgd":          "growth",
    "gds_elt_sgd":      "growth",
    "job_trade_sgd":    "brand",   # uses QE
    "pty_sgd":          "growth",  # uses link_clicks
}


def build_week(week_start, week_label):
    groups = {
        "BRAND":    {"spend": 0, "reach": 0, "impr": 0, "qe": 0, "accounts": {}},
        "GROWTH":   {"spend": 0, "reach": 0, "impr": 0, "qe": 0, "accounts": {}},
        "VERTICAL": {"spend": 0, "reach": 0, "impr": 0, "qe": 0, "accounts": {}},
    }

    for acct, weeks in DATA.items():
        row = weeks.get(week_start)
        if not row:
            continue
        sp, rch, impr, qe = row
        grp = GROUP_MAP[acct]
        atype = ACCOUNT_TYPE[acct]

        g = groups[grp]
        g["spend"]  = round(g["spend"]  + sp,   2)
        g["reach"]  += rch
        g["impr"]   += impr
        g["qe"]     += qe

        acct_data = {
            "spend": sp,
            "reach": rch,
        }
        if atype == "brand":
            acct_data["qe"]   = qe
            acct_data["cpe"]  = cpe(sp, qe)
            acct_data["er"]   = er(qe, rch)
            acct_data["avg_freq"] = freq(impr, rch)
        else:
            acct_data["link_clicks"] = qe
            acct_data["avg_freq"]    = freq(impr, rch)

        g["accounts"][acct] = acct_data

    # Compute group-level summaries
    out_groups = {}
    for gname, g in groups.items():
        sp   = g["spend"]
        rch  = g["reach"]
        impr = g["impr"]
        qe   = g["qe"]

        gdata = {
            "spend": sp,
            "reach": rch,
            "avg_freq": freq(impr, rch),
            "accounts": g["accounts"],
        }
        if gname in ("BRAND", "VERTICAL"):
            gdata["qe"]  = qe
            gdata["cpe"] = cpe(sp, qe)
            gdata["er"]  = er(qe, rch)
        else:
            gdata["link_clicks"] = qe

        out_groups[gname] = gdata

    total_spend = round(
        out_groups["BRAND"]["spend"] +
        out_groups["GROWTH"]["spend"] +
        out_groups["VERTICAL"]["spend"], 2
    )

    return {
        "week_start": week_start,
        "week_label": week_label,
        "total_spend": total_spend,
        "generated_at": "2026-06-23T08:00:00Z",
        "notes": "Historical data pulled via Meta MCP (Apr–Jun 2026). VERTICAL pty_sgd paused May 11–Jun 7. Impressions approximate for growth accounts.",
        "groups": out_groups,
        "watch_list": [],   # Historical weeks: no per-campaign freq data
    }


index = []
for week_start, week_label in WEEKS:
    data = build_week(week_start, week_label)
    path = os.path.join(OUT, f"{week_start}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ {week_start}  spend={data['total_spend']:,.2f}  brand_qe={data['groups']['BRAND']['qe']}")
    index.append(week_start)

# Preserve existing Jun 16 entry and add all historical ones
existing_index_path = os.path.join(OUT, "index.json")
try:
    with open(existing_index_path) as f:
        existing = json.load(f)
except Exception:
    existing = []

# Merge: historical + existing (avoiding duplicates)
full_index = sorted(set(index + existing))
with open(existing_index_path, "w") as f:
    json.dump(full_index, f)
print(f"\n✓ index.json updated: {full_index}")
