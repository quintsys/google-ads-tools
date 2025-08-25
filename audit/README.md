# Audit & Compliance Tools

Tools for comprehensive auditing of Google Ads campaigns, including URL validation, UTM parameter checking, and asset compliance.

## Tools

### `ads_audit.py`
**Purpose**: Comprehensive Google Ads campaign audit tool for URL validation, UTM parameter enforcement, and asset compliance checking.

## Core Features

### 🔍 URL & Landing Page Analysis
- **HTTPS Validation**: Identifies non-secure URLs
- **Domain Mismatch Detection**: Compares display URLs with final URLs
- **HTTP Status Checking**: Probes URLs for accessibility (optional)
- **Landing Page Aggregation**: Analyzes traffic data from landing_page_view

### 📊 UTM Parameter Enforcement
- **Required Parameters**: Enforce presence of specific UTM parameters
- **Case Validation**: Enforce lowercase/uppercase for UTM values
- **Exact Value Matching**: Validate UTM parameters against expected values
- **Regex Pattern Matching**: Validate UTM parameters with custom patterns
- **Auto-tagging Support**: Skip UTM checks when gclid is present
- **Duplicate Detection**: Find URLs with duplicate UTM parameters
- **Empty Value Detection**: Identify UTM parameters with blank values

### 🎯 RSA Asset Auditing
- **Asset Status**: Track enabled/disabled RSA assets
- **Policy Compliance**: Check asset approval status
- **Text Content Analysis**: Extract headlines and descriptions

### 📈 Reporting & Output
Generates comprehensive CSV reports:
- `ads.csv` - Ad-level data with URLs and metadata
- `rsa_assets.csv` - RSA headline and description assets
- `landing_pages.csv` - Landing page performance data (30-day)
- `findings.csv` - Audit issues and recommendations

## Usage Examples

### Basic Audit
```bash
python ads_audit.py --customer-id 1234567890 --out ./audit-results
```

### Advanced Audit with HTTP Checking
```bash
python ads_audit.py \
  --customer-id 1234567890 \
  --out ./audit-results \
  --check-http \
  --timeout 10
```

### UTM Parameter Enforcement
```bash
python ads_audit.py \
  --customer-id 1234567890 \
  --out ./audit-results \
  --utm-required utm_source utm_medium utm_campaign utm_term \
  --utm-case lower \
  --utm-expect utm_medium=cpc \
  --utm-expect utm_source=google \
  --utm-match utm_campaign=/^[a-z0-9_-]+$/ \
  --allow-autotag-only
```

### Account Discovery
```bash
# List accessible accounts
python ads_audit.py --list-accounts

# Detailed account information  
python ads_audit.py --describe-accounts

# Use specific MCC for authentication
python ads_audit.py \
  --login-customer-id 8630268244 \
  --customer-id 1234567890 \
  --out ./audit-results
```

## Command Line Arguments

### Required Arguments
- `--customer-id`: Google Ads customer ID (without dashes) - optional if using account discovery flags

### Account Discovery
- `--list-accounts`: List account resource names and exit
- `--describe-accounts`: Show detailed account info (name, currency, timezone, manager status)
- `--login-customer-id`: Manager account (MCC) ID for authentication

### Output Options
- `--out`: Output directory (default: ./out)
- `--api-version`: Google Ads API version (default: v21)

### HTTP Validation
- `--check-http`: Perform HTTP status checks on final URLs
- `--timeout`: HTTP request timeout in seconds (default: 5)

### UTM Parameter Enforcement
- `--utm-required`: Space-separated list of required UTM parameters (default: utm_source utm_medium utm_campaign)
- `--utm-case`: Enforce case for UTM values - choices: lower, upper, none (default: none)
- `--utm-expect`: Exact value expectations (repeatable) - format: `key=value`
- `--utm-match`: Regex pattern expectations (repeatable) - format: `key=/pattern/`
- `--allow-autotag-only`: Skip UTM checks when gclid parameter is present

## UTM Validation Examples

### Basic Requirements
```bash
--utm-required utm_source utm_medium utm_campaign
```

### Exact Value Enforcement
```bash
--utm-expect utm_medium=cpc \
--utm-expect utm_source=google
```

### Pattern Matching
```bash
--utm-match utm_campaign=/^[a-z0-9_-]+$/ \
--utm-match utm_content=/^(ad1|ad2|ad3)$/
```

### Case Enforcement
```bash
--utm-case lower  # Enforce lowercase UTM values
```

## Output Files

### `ads.csv`
Contains one row per ad with:
- Campaign and ad group hierarchy
- Ad metadata (ID, name, type, status, strength)
- URL data (final URLs, mobile URLs, display URL)
- Tracking templates and custom parameters

### `rsa_assets.csv` 
Contains one row per RSA asset with:
- Asset hierarchy (campaign, ad group, ad)
- Field type (headline/description)
- Asset text content and status
- Policy approval information

### `landing_pages.csv`
Contains aggregated landing page data:
- Unexpanded final URLs
- 30-day clicks and impressions
- Customer attribution

### `findings.csv`
Contains audit issues with:
- Ad ID reference
- Severity level (error/warn/info)
- Issue category and detailed description

## Finding Categories

### Error Level
- **No final_urls set**: Ads missing destination URLs
- **HTTP check failed**: URLs that couldn't be accessed
- **HTTP non-2xx**: URLs returning error status codes
- **UTM missing**: Required UTM parameters not present

### Warning Level  
- **Domain mismatch**: Display URL domain differs from final URL domain
- **Non-HTTPS final URL**: Final URLs using HTTP instead of HTTPS
- **UTM empty value**: UTM parameters with blank values
- **UTM mismatch (exact)**: UTM values don't match expected exact values
- **UTM mismatch (pattern)**: UTM values don't match regex patterns

### Info Level
- **No final_mobile_urls**: Ads without mobile-specific URLs
- **UTM duplicate parameter**: URLs with duplicate UTM parameters
- **UTM case policy**: UTM values not matching case requirements
- **Tracking template missing {lpurl}**: Tracking templates without required placeholder

## Performance Considerations

- **Rate Limiting**: Tool respects Google Ads API rate limits
- **HTTP Checking**: Can be slow for large accounts (use `--timeout` to control)
- **Memory Usage**: Processes data in streams for large accounts
- **API Quotas**: Consider API quota consumption for frequent audits

## Dependencies

```bash
pip install google-ads requests tldextract
```

## Best Practices

1. **Start with discovery**: Use `--list-accounts` and `--describe-accounts` to understand account structure
2. **Test with dry runs**: Although this tool is read-only, start with small customer accounts
3. **Regular auditing**: Run weekly or monthly audits to catch issues early
4. **UTM governance**: Establish UTM parameter standards and enforce them consistently
5. **Performance monitoring**: Use `--check-http` periodically to catch broken URLs
6. **Output management**: Archive audit results with timestamps for trend analysis