import os
import json
import time
import requests
from reporter.config import META_GRAPH_URL, META_FIELDS


TOKEN = os.environ.get("META_ACCESS_TOKEN", "")


def _get(url: str, params: dict, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()
            if "error" in data:
                code = data["error"].get("code", 0)
                if code in (4, 17, 32, 613) and attempt < retries - 1:
                    time.sleep(2 ** attempt * 5)
                    continue
                print(f"Meta API error: {data['error']}")
                return {}
            return data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                print(f"Request failed: {e}")
    return {}


def _action(actions: list, action_type: str) -> float:
    for a in (actions or []):
        if a.get("action_type") == action_type:
            try:
                return float(a.get("value", 0))
            except (ValueError, TypeError):
                return 0.0
    return 0.0


def get_active_campaign_ids(account_id: str) -> set:
    url = f"{META_GRAPH_URL}/act_{account_id}/campaigns"
    params = {"fields": "id,effective_status", "limit": 500, "access_token": TOKEN}
    ids = set()
    while url:
        data = _get(url, params)
        for c in data.get("data", []):
            if c.get("effective_status") == "ACTIVE":
                ids.add(c["id"])
        url = data.get("paging", {}).get("next")
        params = {}
    return ids


def fetch_campaigns(account_id: str, since: str, until: str) -> list[dict]:
    # Currently-active campaign IDs are used ONLY to flag campaigns,
    # never to filter them out. A campaign paused mid-week still spent
    # money during the week, so its spend/metrics must be kept.
    active_ids = get_active_campaign_ids(account_id)

    url = f"{META_GRAPH_URL}/act_{account_id}/insights"
    params = {
        "level": "campaign",
        "fields": META_FIELDS,
        "time_range": json.dumps({"since": since, "until": until}),
        "filtering": json.dumps([{"field": "spend", "operator": "GREATER_THAN", "value": "0"}]),
        "limit": 500,
        "access_token": TOKEN,
    }

    campaigns = []
    while url:
        data = _get(url, params)
        for row in data.get("data", []):
            actions  = row.get("actions", [])
            spend    = float(row.get("spend", 0) or 0)
            impr     = int(row.get("impressions", 0) or 0)
            reach    = int(row.get("reach", 0) or 0)
            clicks   = int(row.get("clicks", 0) or 0)
            cpm      = float(row.get("cpm", 0) or 0)
            cpc      = float(row.get("cpc", 0) or 0)
            ctr      = float(row.get("ctr", 0) or 0)
            freq_raw = row.get("frequency")
            freq     = float(freq_raw) if freq_raw else (impr / reach if reach > 0 else 0.0)

            comment   = _action(actions, "comment")
            shares    = _action(actions, "post_share")
            saves     = _action(actions, "post_save")
            lclicks   = _action(actions, "link_click")
            installs  = _action(actions, "mobile_app_install")

            qe = comment + shares + saves + lclicks
            name = row.get("campaign_name", "")

            campaigns.append({
                "id":         row.get("campaign_id"),
                "name":       name,
                "is_active":  row.get("campaign_id") in active_ids,
                "spend":      spend,
                "impressions": impr,
                "reach":      reach,
                "clicks":     clicks,
                "cpm":        cpm,
                "cpc":        cpc,
                "ctr":        ctr,
                "frequency":  freq,
                "comment":    comment,
                "shares":     shares,
                "saves":      saves,
                "link_clicks": lclicks,
                "qe":         qe,
                "installs":   installs,
                "is_install": installs > 0 or "install" in name.lower(),
                "cpe":        spend / qe if qe > 0 else 0.0,
                "er":         qe / reach * 100 if reach > 0 else 0.0,
                "cpi":        spend / installs if installs > 0 else 0.0,
            })
        url = data.get("paging", {}).get("next")
        params = {}

    return campaigns
