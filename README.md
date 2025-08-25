# Google Ads Management Tools

A comprehensive collection of Python and shell tools for managing Google Ads campaigns, including authentication, auditing, analysis, recovery, and data processing capabilities.

## 📁 Tool Categories

### 🔐 [Authentication & Account Discovery](./auth/)
Tools for OAuth setup and account hierarchy exploration.

| Tool | Description | Usage |
|------|-------------|-------|
| `generate_refresh_token.py` | Generate OAuth refresh tokens for Google Ads API | `python generate_refresh_token.py --client-id CLIENT_ID --client-secret SECRET` |
| `list_accessible_customers.py` | List all accessible customer accounts | `python list_accessible_customers.py` |
| `list_hierarchy_check_target.py` | Check account hierarchy and find specific customer IDs | `python list_hierarchy_check_target.py` |

### 🔍 [Audit & Compliance](./audit/)
Comprehensive auditing tools for campaign health and compliance.

| Tool | Description | Key Features |
|------|-------------|--------------|
| `ads_audit.py` | Complete Google Ads URL and RSA audit tool | • URL validation (HTTPS, UTM params)<br/>• Domain mismatch detection<br/>• HTTP status checking<br/>• UTM parameter enforcement<br/>• RSA asset auditing<br/>• Landing page analysis |

### 📊 [Analysis & Reporting](./analysis/)
Tools for analyzing campaign data and generating reports.

| Tool | Description | Usage |
|------|-------------|-------|
| `list_positive_keywords.py` | List positive keywords in ad groups with match type counts | `python list_positive_keywords.py --customer-id CID --ad-group-id AGID` |
| `list_rsas_summary.py` | Summary view of Responsive Search Ads (headlines, descriptions, URLs) | `python list_rsas_summary.py --customer-id CID --ad-group-id AGID` |

### 🔧 [Recovery & Migration](./recovery/)
Tools for recovering deleted assets and migrating between ad types.

| Tool | Description | Key Features |
|------|-------------|--------------|
| `recover_to_existing_ad_group.py` | Copy keywords and RSAs from removed ad groups | • Idempotent operation<br/>• Keyword deduplication<br/>• Copy negatives option<br/>• Pause on create<br/>• Match type forcing |
| `rebuild_etas_as_rsas.py` | Convert legacy ETAs to Responsive Search Ads | • ETA-like pinning<br/>• Padding modes<br/>• RSA deduplication<br/>• Safe filler content |

### 📈 [Data Processing](./data-processing/)
Tools for processing and transforming campaign data.

| Tool | Description | Usage |
|------|-------------|-------|
| `expand_geo.py` | Generate geographic keyword variations (states, metros) | `python expand_geo.py --input seeds.csv --output expanded.csv --mode states` |
| `txt_to_seed_csv.sh` | Convert text keyword list to Google Ads CSV format | `./txt_to_seed_csv.sh keywords.txt seeds.csv "Campaign Name" "Ad Group"` |

## 🚀 Quick Start

### Prerequisites

1. **Python Environment** (Python 3.8+)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install google-ads requests tldextract
   ```

2. **Google Ads API Setup**
   - Enable Google Ads API in Google Cloud Console
   - Create OAuth client credentials
   - Generate refresh token using `auth/generate_refresh_token.py`

3. **Configuration File** (`~/.google-ads.yaml`)
   ```yaml
   developer_token: "YOUR_DEV_TOKEN"
   client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com" 
   client_secret: "YOUR_CLIENT_SECRET"
   refresh_token: "YOUR_REFRESH_TOKEN"
   login_customer_id: "MCC_ID"  # Optional MCC ID
   endpoint: googleads.googleapis.com
   use_proto_plus: True
   ```

### Example Workflows

#### 1. Account Setup & Discovery
```bash
# Generate OAuth token
python auth/generate_refresh_token.py --client-id YOUR_ID --client-secret YOUR_SECRET

# Verify access
python auth/list_accessible_customers.py

# Check hierarchy
python auth/list_hierarchy_check_target.py
```

#### 2. Campaign Audit
```bash
# Basic audit
python audit/ads_audit.py --customer-id 1234567890 --out ./audit-results

# Advanced audit with HTTP checking and UTM validation
python audit/ads_audit.py \
  --customer-id 1234567890 \
  --out ./audit-results \
  --check-http \
  --utm-required utm_source utm_medium utm_campaign \
  --utm-case lower \
  --utm-expect utm_medium=cpc \
  --allow-autotag-only
```

#### 3. Asset Recovery
```bash
# Preview recovery (dry run)
python recovery/recover_to_existing_ad_group.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111 \
  --dest-ad-group-id 222222 \
  --dry-run \
  --copy-negatives

# Execute recovery
python recovery/recover_to_existing_ad_group.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111 \
  --dest-ad-group-id 222222 \
  --only-exact \
  --pause-on-create \
  --copy-negatives
```

#### 4. Data Processing
```bash
# Convert keywords to CSV
./data-processing/txt_to_seed_csv.sh keywords.txt seeds.csv "My Campaign" "My Ad Group"

# Generate geo variations
python data-processing/expand_geo.py --input seeds.csv --output geo-expanded.csv --mode states
```

## 📋 Common Command Line Arguments

### Global Arguments
- `--customer-id`: Google Ads customer ID (without dashes)
- `--login-customer-id`: Manager account (MCC) ID for authentication
- `--api-version`: Google Ads API version (default: v21)
- `--dry-run`: Preview operations without making changes

### Audit-Specific Arguments
- `--check-http`: Perform HTTP status checks on URLs
- `--timeout`: HTTP request timeout in seconds
- `--utm-required`: List of required UTM parameters
- `--utm-case`: Enforce case for UTM values (lower/upper/none)
- `--utm-expect`: Exact UTM value expectations (key=value)
- `--utm-match`: UTM regex pattern matching (key=/pattern/)
- `--allow-autotag-only`: Skip UTM checks when gclid is present

### Recovery Arguments
- `--source-ad-group-id`: Source ad group ID to copy from
- `--dest-ad-group-id`: Destination ad group ID to copy to
- `--only-exact`: Force all keywords to exact match
- `--pause-on-create`: Create new items in paused state
- `--copy-negatives`: Include negative keywords in recovery

## 🔧 Tool Configuration

### UTM Parameter Enforcement
The audit tool supports sophisticated UTM parameter validation:

```bash
# Require specific UTM parameters
--utm-required utm_source utm_medium utm_campaign utm_term

# Enforce exact values
--utm-expect utm_medium=cpc --utm-expect utm_source=google

# Pattern matching
--utm-match utm_campaign=/^[a-z0-9_-]+$/

# Case enforcement
--utm-case lower

# Allow auto-tagging only (skip UTM when gclid present)
--allow-autotag-only
```

### Recovery Safety Features
All recovery tools include safety mechanisms:

- **Idempotent Operations**: Safe to re-run multiple times
- **Dry Run Mode**: Preview changes before execution
- **Deduplication**: Automatic detection of existing assets
- **Validation**: Pre-flight checks for account access and data integrity

## 🗂️ File Structure

```
.
├── README.md                          # This index file
├── recovery.md                        # Detailed recovery documentation
├── run.sh                            # Legacy execution script
├── auth/                             # Authentication & account tools
│   ├── generate_refresh_token.py
│   ├── list_accessible_customers.py
│   └── list_hierarchy_check_target.py
├── audit/                            # Audit & compliance tools  
│   └── ads_audit.py
├── analysis/                         # Analysis & reporting tools
│   ├── list_positive_keywords.py
│   └── list_rsas_summary.py
├── recovery/                         # Recovery & migration tools
│   ├── recover_to_existing_ad_group.py
│   └── rebuild_etas_as_rsas.py
├── data-processing/                  # Data transformation tools
│   ├── expand_geo.py
│   └── txt_to_seed_csv.sh
└── out/                             # Output directory for generated files
```

## 📖 Additional Documentation

- [`recovery.md`](./recovery.md) - Comprehensive recovery runbook with step-by-step procedures
- Each tool folder contains specific documentation for that category

## 🤝 Contributing

When adding new tools:
1. Place them in the appropriate category folder
2. Update this README with tool descriptions and usage examples
3. Include proper error handling and dry-run capabilities
4. Follow the established command-line argument patterns

## ⚠️ Important Notes

- Always use `--dry-run` first when using recovery tools
- Keep your `~/.google-ads.yaml` file secure and never commit it to version control
- Test on non-production accounts when possible
- The Google Ads API has rate limits - tools include appropriate delays
- Some operations cannot be undone (especially deletions)

---

**Project**: Ogburn School Google Ads Management  
**Owner**: QUINTSYS  
**Last Updated**: 2025-08-25