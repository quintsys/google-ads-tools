# Ogburn School — Google Ads Recovery & Geo Expansion Runbook (macOS)

This document captures **everything we set up and ran** to recover assets from a removed ad group, copy them safely into a new ad group, handle geo keyword expansion, and rebuild legacy ETAs as RSAs. It’s written for macOS and assumes a terminal (zsh/bash).

---

## Table of Contents

1. [Prerequisites](#prerequisites)  
2. [Python Environments on macOS](#python-environments-on-macos)  
3. [Using Mise for Python](#using-mise-for-python)  
4. [Generate OAuth Credentials](#generate-oauth-credentials)  
5. [Enable the Google Ads API in Cloud](#enable-the-google-ads-api-in-cloud)  
6. [Create `~/.google-ads.yaml`](#create-google-adsyaml)  
7. [Verify Account Access & Hierarchy](#verify-account-access--hierarchy)  
8. [Identify the Correct IDs](#identify-the-correct-ids)  
9. [Recovery Script: Copy from Removed Ad Group](#recovery-script-copy-from-removed-ad-group)  
10. [Negative Keywords](#negative-keywords)  
11. [Listing Keywords](#listing-keywords)  
12. [Pausing Broad Keywords](#pausing-broad-keywords)  
13. [Rebuilding ETAs as RSAs](#rebuilding-etas-as-rsas)  
14. [Geo Expansion Utilities](#geo-expansion-utilities)  
15. [Troubleshooting](#troubleshooting)  
16. [Operational Notes](#operational-notes)

---

## Prerequisites

- macOS with **Python 3** (via mise or brew).  
- Terminal (zsh/bash).  
- Access to:
  - **Google Ads** client + optionally MCC.  
  - **Google Cloud Console** project for OAuth client.  
  - **Developer Token** from Ads → Tools → API Center.

---

## Python Environments on macOS

macOS/Homebrew ships Python as “externally managed” (PEP 668). You can:  
- use `python -m venv` for per-project isolation  
- or better, use **mise** (see next section).

Example with venv:

```bash
python3 -m venv ~/venvs/ads-oauth
source ~/venvs/ads-oauth/bin/activate
pip install --upgrade pip
pip install google-ads google-auth-oauthlib grpcio grpcio-status
```

---

## Using Mise for Python

If you already use mise for ruby/node, add python:

```bash
mise install python 3.13.5
echo "python 3.13.5" >> .tool-versions
```

Then in the project:

```bash
python --version
pip install google-ads
```

Optionally still create `.venv` for per-project deps.

---

## Generate OAuth Credentials

1. In Cloud Console → APIs & Services → Credentials  
   - Create OAuth client ID (desktop app).  
   - Copy `client_id` and `client_secret`.  

2. Generate a refresh token with our helper:

```bash
python generate_refresh_token.py \
  --client-id 'xxx.apps.googleusercontent.com' \
  --client-secret 'yyy'
```

Browser flow → login → get refresh token.

---

## Enable the Google Ads API in Cloud

Enable API in same project:

```bash
gcloud services enable googleads.googleapis.com --project=<PROJECT_ID>
```

---

## Create `~/.google-ads.yaml`

```yaml
developer_token: "DEV_TOKEN"
client_id: "CLIENT_ID.apps.googleusercontent.com"
client_secret: "CLIENT_SECRET"
refresh_token: "REFRESH_TOKEN"
login_customer_id: "8630268244"   # MCC
endpoint: googleads.googleapis.com
use_proto_plus: True
```

---

## Verify Account Access & Hierarchy

```bash
python list_accessible_customers.py
python list_hierarchy_check_target.py
```

Confirm:  
- MCC: `8630268244` (QUINTSYS)  
- Client: `6091332809` (Ogburn School)

---

## Identify the Correct IDs

- Customer ID: `6091332809`  
- Source (removed ad group): `65028146118`  
- Destination ad group: `187136680689` (“High - Online School #3”)  
- Campaign: `1659861328`

---

## Recovery Script: Copy from Removed Ad Group

`recover_to_existing_ad_group.py`

Flags:  
- `--dry-run` preview  
- `--only-exact` force exact  
- `--pause-on-create` pause new positives  
- `--copy-negatives` include negatives

Example:

```bash
python recover_to_existing_ad_group.py \
  --customer-id 6091332809 \
  --source-ad-group-id 65028146118 \
  --dest-ad-group-id 187136680689 \
  --only-exact \
  --pause-on-create \
  --copy-negatives
```

---

## Negative Keywords

- Copied with `--copy-negatives`.  
- Preserve match type.  
- No “paused” state (always active).  
- Verify in Ads UI.

---

## Listing Keywords

`list_positive_keywords.py` → shows current positives.

Sample result:

```
Positive keywords in ad group 187136680689: 104

By match type:
  BROAD        18
  EXACT        86

By status:
  ENABLED      18
  PAUSED       86
```

So this ad group now has 18 broad (enabled) and 86 exact (paused).

---

## Pausing Broad Keywords

We want pure exact. Option 1: Ads Editor. Option 2: API mutate.

GAQL to find them:

```sql
SELECT ad_group_criterion.resource_name,
       ad_group_criterion.keyword.text
FROM ad_group_criterion
WHERE ad_group_criterion.type = KEYWORD
  AND ad_group_criterion.negative = FALSE
  AND ad_group_criterion.keyword.match_type = BROAD
  AND ad_group_criterion.status = ENABLED
  AND ad_group_criterion.ad_group = 'customers/6091332809/adGroups/187136680689'
```

Then call `adGroupCriteria:mutate` with `status: PAUSED`.

---

## Rebuilding ETAs as RSAs

Script: `rebuild_etas_as_rsas.py`

- ETAs can’t be recreated, but we mapped them to RSAs.  
- Flags:  
  - `--pause-on-create`  
  - `--no-pin` (let Google mix headlines/descriptions)  
  - `--pad-mode generic` (fill missing slots with generic text)

Run:

```bash
python rebuild_etas_as_rsas.py \
  --customer-id 6091332809 \
  --source-ad-group-id 65028146118 \
  --dest-ad-group-id 187136680689 \
  --pause-on-create \
  --no-pin \
  --pad-mode generic
```

Result: 7 ETAs rebuilt → 7 RSAs (paused).

---

## Geo Expansion Utilities

- `expand_geo.py` → generate state-based variants.  
- `txt_to_seed_csv.sh` → text → Ads CSV format.  
- Strategy: build controlled lists, avoid overloading a single ad group.

---

## Troubleshooting

- **pip install fails** → always use venv or mise.  
- **ModuleNotFoundError** → install inside venv.  
- **FileNotFoundError google-ads.yaml** → symlink or env var.  
- **SERVICE_DISABLED** → enable API in project.  
- **No customer found** → wrong login_customer_id or wrong user.  
- **GRPC errors** → upgrade google-ads lib, don’t pin versions.

---

## Operational Notes

- Recovery script is idempotent.  
- `--dry-run` always first.  
- ETAs are lost; only RSAs can be recreated.  
- Clean up broad positives → keep exact-only strategy.  
- Labeling/logging optional (`--label`).  
- Monitor negatives for conflicts.

---

**Owner:** QUINTSYS — Admissions-Ads project  
**Scope:** Ogburn School Google Ads — asset recovery, geo expansion & hygiene