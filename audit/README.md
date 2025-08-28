# Audit & Compliance Tools

Tools for comprehensive auditing of Google Ads campaigns, including URL validation, UTM parameter checking, and asset compliance.

## Tools

### `ads_audit.py`
**Purpose**: Comprehensive Google Ads campaign audit tool for URL validation, UTM parameter enforcement, asset compliance checking, and sitelink analysis.

## Core Features

### URL & Landing Page Analysis
- **HTTPS Validation**: Identifies non-secure URLs
- **Domain Mismatch Detection**: Compares display URLs with final URLs
- **HTTP Status Checking**: Probes URLs for accessibility (optional)
- **Landing Page Aggregation**: Analyzes traffic data from landing_page_view

### UTM Parameter Enforcement
- **Required Parameters**: Enforce presence of specific UTM parameters
- **Case Validation**: Enforce lowercase/uppercase for UTM values
- **Exact Value Matching**: Validate UTM parameters against expected values
- **Regex Pattern Matching**: Validate UTM parameters with custom patterns
- **Auto-tagging Support**: Skip UTM checks when gclid is present
- **Duplicate Detection**: Find URLs with duplicate UTM parameters
- **Empty Value Detection**: Identify UTM parameters with blank values

### RSA Asset Auditing
- **Asset Status**: Track enabled/disabled RSA assets
- **Policy Compliance**: Check asset approval status
- **Text Content Analysis**: Extract headlines and descriptions

### Sitelink Asset Analysis
- **Asset Discovery**: Locate all sitelink assets in the account
- **Placement Mapping**: Map sitelinks to campaigns and ad groups
- **Link Text Extraction**: Capture sitelink display text
- **UI-Friendly Output**: Generate data for easy asset location in Google Ads UI

### Advanced Landing Page Analysis
- **Unexpanded URLs**: Direct final URLs as configured in ads
- **Expanded URLs**: URLs after redirect resolution (when available)
- **Performance Correlation**: 30-day clicks and impressions data
- **Cross-Reference Mapping**: Ad-to-URL relationships for UI lookups

### Strategic Analysis
- **UTM Coverage Analysis**: Identify ads with missing or incomplete tracking parameters
- **Homepage vs Deep-Link Analysis**: Find ads directing traffic to specific pages vs homepage
- **Traffic Source Mapping**: Categorize how users reach different URL destinations
- **URL Pattern Recognition**: Classify URL types (product pages, landing pages, content, etc.)

### Reporting & Output
Generates comprehensive CSV reports:
- `ads.csv` - Ad-level data with URLs and metadata
- `rsa_assets.csv` - RSA headline and description assets
- `landing_pages.csv` - Unexpanded landing page performance data (30-day)
- `expanded_landing_pages.csv` - Landing pages after redirect resolution (30-day)
- `ad_url_map.csv` - Ad-to-URL crosswalk for UI lookups
- `sitelink_urls.csv` - Sitelink asset placement mapping
- `utm_analysis.csv` - UTM parameter coverage analysis per ad URL
- `homepage_analysis.csv` - Homepage vs non-homepage destination analysis  
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

### Comprehensive Asset Analysis
```bash
python ads_audit.py \
  --customer-id 1234567890 \
  --out ./audit-results \
  --check-http \
  --utm-required utm_source utm_medium utm_campaign utm_term \
  --utm-case lower \
  --utm-expect utm_medium=cpc \
  --allow-autotag-only
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
Contains aggregated unexpanded landing page data:
- Unexpanded final URLs as configured in ads
- 30-day clicks and impressions
- Customer attribution

### `expanded_landing_pages.csv`
Contains aggregated expanded landing page data (when available):
- Expanded final URLs after redirect resolution
- 30-day clicks and impressions
- Customer attribution
- Note: Not available in all Google Ads accounts/API versions

### `ad_url_map.csv`
Contains ad-to-URL crosswalk data:
- Ad ID, campaign ID, ad group ID
- Full URL and URL without query parameters
- Source type (ad.final_urls or ad.final_mobile_urls)
- Useful for UI lookups and URL troubleshooting

### `sitelink_urls.csv`
Contains sitelink asset placement data:
- Asset ID, name, and link text
- Campaign or ad group placement
- Placement type (campaign/ad_group)
- Note: URL fields omitted for API v21 compatibility

### `utm_analysis.csv`
Contains UTM parameter analysis per ad URL:
- Ad hierarchy (ad ID, campaign, ad group)
- URL type (final_urls or final_mobile_urls)
- Full URL being analyzed
- UTM status (has_utm, gclid_only, no_tracking)
- Count of UTM parameters found
- List of UTM parameter names
- Presence of gclid auto-tagging

### `homepage_analysis.csv`
Contains homepage vs non-homepage destination analysis:
- Ad hierarchy and URL source information
- Full URL and extracted path
- Homepage classification (true/false)
- URL category (homepage, product_page, landing_page, etc.)
- Path depth (number of subdirectories)
- Domain information
- Includes sitelink destinations as potential non-homepage sources

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
- **Expanded Landing Pages**: May not be available in all accounts, handled gracefully
- **Sitelink Analysis**: Limited to placement mapping to maintain API v21 compatibility

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
7. **Sitelink maintenance**: Use `sitelink_urls.csv` to locate and update sitelink assets in the UI
8. **URL troubleshooting**: Use `ad_url_map.csv` for quick ad-to-URL lookups during issue resolution
9. **Landing page analysis**: Compare `landing_pages.csv` and `expanded_landing_pages.csv` to identify redirect issues
10. **UTM governance**: Use `utm_analysis.csv` to identify ads missing tracking parameters
11. **Traffic strategy**: Use `homepage_analysis.csv` to understand which ads drive traffic to specific pages vs homepage