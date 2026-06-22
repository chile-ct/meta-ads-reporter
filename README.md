# Meta Ads Weekly Reporter

Automated weekly Meta Ads performance report → Slack + Notion.  
Runs every **Monday 09:00 ICT** via GitHub Actions. Zero Claude token cost.

## What it does

1. Pulls campaign-level data from all 9 Meta ad accounts (ACTIVE campaigns with spend > 0)
2. Computes QE (comment + share + save + link_click), ER%, CPE, installs, CPI, frequency
3. Sends a WoW Group Summary to your Slack DM + `#ct-marketing-performance`
4. Sends the Vertical report separately to Hang Le Tuyet via Slack DM
5. Writes the full monthly MTD report to Notion

## GitHub Secrets required

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `META_ACCESS_TOKEN` | Your Meta Graph API user access token (long-lived, with `ads_read` + `read_insights` permissions) |
| `NOTION_API_KEY` | Notion internal integration token (`secret_...`) |
| `SLACK_BOT_TOKEN` | Slack bot OAuth token (`xoxb-...`) with `chat:write` scope |

## Manual test run

In **Actions → Weekly Meta Ads Report → Run workflow**, check **"Send to self DM only (test mode)"** to send all messages to your own DM instead of the real channels.

## Local run

```bash
export META_ACCESS_TOKEN=...
export NOTION_API_KEY=...
export SLACK_BOT_TOKEN=...
export TEST_MODE=true   # optional: send to self only

pip install -r requirements.txt
python main.py
```

## Account groups

| Group | Accounts |
|---|---|
| **BRAND** | gds_brand, pty_branding_sgd, veh_brand, job_branding_sgd |
| **GROWTH** | growth_sgd, job_sgd, gds_elt_sgd |
| **VERTICAL** | job_trade_sgd, pty_sgd |

## Frequency thresholds

| Flag | Range |
|---|---|
| ✅ | < 3× |
| 🟡 | 3–6× |
| 🔴 | ≥ 7× |
