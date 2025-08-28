# Analysis Guide: UTM and Homepage Analysis

This guide helps you analyze the new CSV outputs from `ads_audit.py` to answer key strategic questions.

## Question 1: Are all ads showing URLs with UTM tracking parameters?

### Use File: `utm_analysis.csv`

#### Quick Analysis Queries

**Count ads by UTM status:**
```bash
# Using command line tools
cut -d',' -f8 utm_analysis.csv | sort | uniq -c | sort -nr

# Expected output format:
# 150 has_utm
#  25 gclid_only  
#  10 no_tracking
```

**Find ads with no tracking:**
```bash
# Ads with no UTM and no gclid
grep "no_tracking" utm_analysis.csv | cut -d',' -f1,4,5,7

# Output: ad_id, campaign_name, ad_group_name, url
```

**Find ads with only gclid (no UTM):**
```bash
# Ads relying only on auto-tagging
grep "gclid_only" utm_analysis.csv | cut -d',' -f1,4,5,7
```

#### Analysis in Spreadsheet

1. **Open `utm_analysis.csv`** in Excel/Google Sheets
2. **Create pivot table** with:
   - Rows: `campaign_name`, `ad_group_name`
   - Columns: `utm_status`
   - Values: Count of `ad_id`
3. **Filter for problems**: Focus on `no_tracking` and `gclid_only` entries
4. **Export action list**: Create list of ads needing UTM parameters

#### Key Metrics to Track

- **UTM Coverage**: % of URLs with `utm_status = "has_utm"`
- **Auto-tag Reliance**: % of URLs with `utm_status = "gclid_only"`
- **Untracked URLs**: % of URLs with `utm_status = "no_tracking"`
- **UTM Completeness**: Average `utm_count` for tracked URLs

## Question 2: Which ads send visitors to non-homepage URLs?

### Use File: `homepage_analysis.csv`

#### Quick Analysis Queries

**Count by homepage classification:**
```bash
# Count homepage vs non-homepage destinations
cut -d',' -f8 homepage_analysis.csv | sort | uniq -c

# Expected output:
# 120 False (non-homepage)
#  45 True (homepage)
```

**Find non-homepage destinations by category:**
```bash
# Group non-homepage URLs by category
awk -F',' '$8=="False" {print $10}' homepage_analysis.csv | sort | uniq -c | sort -nr

# Expected output:
#  35 landing_page
#  25 product_page
#  15 content_page
#  10 category_page
#   8 sitelink_destination
```

**Identify deep-link ads (high path depth):**
```bash
# Find ads going to deep pages (path_depth > 2)
awk -F',' '$11 > 2 {print $1,$4,$5,$7,$9,$11}' homepage_analysis.csv

# Output: ad_id campaign_name ad_group_name url url_path path_depth
```

#### Analysis in Spreadsheet

1. **Open `homepage_analysis.csv`** in Excel/Google Sheets
2. **Filter non-homepage traffic**: `is_homepage = FALSE`
3. **Create pivot table** with:
   - Rows: `url_category`, `campaign_name`
   - Values: Count of `ad_id`
4. **Analyze by source**: Group by `url_source` to see ad vs sitelink traffic
5. **Deep-link analysis**: Sort by `path_depth` descending

#### Advanced Analysis Combinations

**Cross-reference with UTM data:**
```bash
# Join utm_analysis and homepage_analysis by ad_id to see tracking on non-homepage URLs
join -t',' -1 1 -2 1 \
  <(sort -t',' -k1,1 utm_analysis.csv) \
  <(sort -t',' -k1,1 homepage_analysis.csv) \
  | awk -F',' '$14=="False" && $8=="no_tracking"' \
  > non_homepage_untracked.csv
```

## Traffic Source Analysis

### URL Sources Explained

- `ad.final_urls` - Primary ad destination URLs
- `ad.final_mobile_urls` - Mobile-specific ad URLs  
- `sitelink.campaign` - Campaign-level sitelink extensions
- `sitelink.ad_group` - Ad group-level sitelink extensions

### URL Categories Explained

- `homepage` - Root domain or index pages
- `product_page` - Specific product or service pages
- `landing_page` - Dedicated campaign landing pages
- `category_page` - Product/service category listings
- `content_page` - Blog posts, news articles, resources
- `info_page` - About, contact, company information
- `sitelink_destination` - Sitelink extension destinations
- `other_page` - Uncategorized destinations

## Actionable Insights

### UTM Parameter Issues

**High Priority Actions:**
1. **Add UTM to untracked URLs**: Focus on `utm_status = "no_tracking"`
2. **Enhance gclid-only URLs**: Consider adding UTM to `gclid_only` URLs for better attribution
3. **Standardize UTM parameters**: Ensure consistent UTM naming across campaigns

**Medium Priority Actions:**
1. **Audit UTM values**: Check `utm_parameters` column for consistency
2. **Campaign-level UTM strategy**: Ensure campaign names match `utm_campaign` values

### Homepage vs Deep-Link Strategy

**Strategic Questions:**
1. **Should homepage ads exist?** Consider if brand campaigns should go to homepage vs specific pages
2. **Are deep-links intentional?** Verify high `path_depth` URLs are deliberate choices
3. **Sitelink effectiveness**: Are sitelinks providing value by driving to specific pages?

**Optimization Opportunities:**
1. **Landing page alignment**: Ensure ad copy matches destination page content
2. **Mobile experience**: Check if `final_mobile_urls` go to mobile-optimized pages
3. **Conversion path optimization**: Analyze if deep-links have better conversion rates

## Reporting Templates

### Executive Summary Template

```
UTM Tracking Coverage Report
===========================
Total Ad URLs Analyzed: [total_count]
URLs with UTM Parameters: [utm_count] ([utm_percentage]%)
URLs with Auto-tag Only: [gclid_count] ([gclid_percentage]%)  
Untracked URLs: [untracked_count] ([untracked_percentage]%)

Traffic Destination Analysis
===========================
Homepage Destinations: [homepage_count] ([homepage_percentage]%)
Landing Page Destinations: [landing_count] ([landing_percentage]%)
Product Page Destinations: [product_count] ([product_percentage]%)
Other Page Types: [other_count] ([other_percentage]%)

Action Items:
1. Add UTM parameters to [untracked_count] untracked URLs
2. Review [deep_link_count] deep-link destinations for relevance
3. Audit [sitelink_count] sitelink destinations for optimization
```

### Detailed Action List Template

```
Ad ID | Campaign | Ad Group | Issue | URL | Recommended Action
------|----------|----------|-------|-----|------------------
[ad_id] | [campaign] | [ad_group] | No UTM | [url] | Add utm_source=google&utm_medium=cpc&utm_campaign=[campaign_name]
[ad_id] | [campaign] | [ad_group] | Deep Link | [url] | Verify landing page relevance and mobile experience
[ad_id] | [campaign] | [ad_group] | Sitelink | [sitelink_text] | Check sitelink destination and performance
```

## Automation Ideas

### Monitoring Scripts

```bash
# Daily UTM coverage check
utm_coverage=$(awk -F',' '$8=="has_utm"' utm_analysis.csv | wc -l)
total_urls=$(tail -n +2 utm_analysis.csv | wc -l)
coverage_percent=$(echo "scale=1; $utm_coverage * 100 / $total_urls" | bc)
echo "UTM Coverage: $coverage_percent%"

# Alert if coverage drops below threshold
if (( $(echo "$coverage_percent < 90" | bc -l) )); then
    echo "ALERT: UTM coverage below 90% threshold"
fi
```

### Integration with BI Tools

Import CSV files into your business intelligence platform to create:
- UTM coverage dashboards
- Traffic destination heatmaps  
- Campaign-level tracking compliance reports
- Historical trend analysis of URL strategy changes