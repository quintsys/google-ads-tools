# Analysis & Reporting Tools

Tools for analyzing existing Google Ads campaign data and generating detailed reports on keywords, ads, and performance metrics.

## Tools

### `list_positive_keywords.py`
**Purpose**: Analyze positive (non-negative) keywords in ad groups with detailed breakdowns by match type and status.

**Usage**:
```bash
# Console output
python list_positive_keywords.py --customer-id 1234567890 --ad-group-id 987654321

# Export to CSV
python list_positive_keywords.py \
  --customer-id 1234567890 \
  --ad-group-id 987654321 \
  --to-csv keywords_analysis.csv
```

**Output Information**:
- Total keyword count
- Breakdown by match type (Broad, Phrase, Exact)
- Breakdown by status (Enabled, Paused)
- Individual keyword details with bid information

**Example Console Output**:
```
Positive keywords in ad group 187136680689: 104

By match type:
  BROAD        18
  EXACT        86

By status:
  ENABLED      18
  PAUSED       86
```

**CSV Output Columns**:
- `criterion_id`: Unique keyword identifier
- `status`: Keyword status (ENABLED/PAUSED)
- `keyword_text`: The actual keyword text
- `match_type`: Match type (BROAD/PHRASE/EXACT)
- `cpc_bid_micros`: Cost-per-click bid in micros (divide by 1,000,000 for actual bid)

### `list_rsas_summary.py`
**Purpose**: Generate summaries of Responsive Search Ads (RSAs) showing headlines, descriptions, and URLs.

**Usage**:
```bash
python list_rsas_summary.py \
  --customer-id 1234567890 \
  --ad-group-id 987654321
```

**Output Information**:
- RSA count in the ad group
- Up to 3 headlines per RSA
- Up to 2 descriptions per RSA  
- Final URLs
- Ad status and metadata

**Example Output**:
```
=== RSA #1 ===
Final URLs: ['https://example.com/page1']
Headlines:
  1. "Best Online School"
  2. "Accredited Education" 
  3. "Flexible Learning"
Descriptions:
  1. "Get your diploma online with our accredited programs."
  2. "Study at your own pace with expert support."

=== RSA #2 ===
[Additional RSA details...]
```

## Common Use Cases

### Keyword Analysis Workflows

#### 1. Pre-Optimization Analysis
```bash
# Analyze current keyword distribution
python list_positive_keywords.py --customer-id CID --ad-group-id AGID --to-csv before_optimization.csv

# Identify broad keywords that should be paused
grep "BROAD.*ENABLED" before_optimization.csv

# Count exact match keywords
grep "EXACT" before_optimization.csv | wc -l
```

#### 2. Post-Recovery Validation
```bash
# After using recovery tools, validate keyword distribution
python list_positive_keywords.py --customer-id CID --ad-group-id DEST_AGID

# Compare with source ad group
python list_positive_keywords.py --customer-id CID --ad-group-id SOURCE_AGID
```

#### 3. Match Type Strategy Validation
```bash
# Export for analysis in spreadsheet
python list_positive_keywords.py \
  --customer-id CID \
  --ad-group-id AGID \
  --to-csv match_type_analysis.csv

# Quick match type breakdown
python list_positive_keywords.py --customer-id CID --ad-group-id AGID | grep -A5 "By match type"
```

### RSA Analysis Workflows

#### 1. Content Inventory
```bash
# Review all RSAs in an ad group
python list_rsas_summary.py --customer-id CID --ad-group-id AGID > rsa_inventory.txt

# Count total RSAs
python list_rsas_summary.py --customer-id CID --ad-group-id AGID | grep "=== RSA #" | wc -l
```

#### 2. Content Quality Review
Use the tool output to:
- Verify headline and description quality
- Check for consistent messaging
- Identify duplicate content across RSAs
- Validate final URLs are correct

#### 3. Migration Validation
After converting ETAs to RSAs:
```bash
# Check newly created RSAs
python list_rsas_summary.py --customer-id CID --ad-group-id DEST_AGID

# Compare content with original ETAs (manual review)
```

## Integration with Other Tools

### With Recovery Tools
```bash
# Before recovery - analyze source
python list_positive_keywords.py --customer-id CID --ad-group-id SOURCE_AGID
python list_rsas_summary.py --customer-id CID --ad-group-id SOURCE_AGID

# Perform recovery
python ../recovery/recover_to_existing_ad_group.py [options]

# After recovery - validate destination  
python list_positive_keywords.py --customer-id CID --ad-group-id DEST_AGID
python list_rsas_summary.py --customer-id CID --ad-group-id DEST_AGID
```

### With Audit Tools
```bash
# Analyze keywords first
python list_positive_keywords.py --customer-id CID --ad-group-id AGID --to-csv keywords.csv

# Then run comprehensive audit
python ../audit/ads_audit.py --customer-id CID --out ./audit-results
```

## Output Formats

### Console Output
- Human-readable summaries
- Statistical breakdowns
- Hierarchical display for RSAs

### CSV Output (Keywords Only)
- Machine-readable format
- Compatible with spreadsheet applications
- Suitable for further data analysis
- Can be imported into other tools

## Error Handling

Both tools include robust error handling:
- **Invalid Customer ID**: Clear error message with suggestions
- **Invalid Ad Group ID**: Verification that ad group exists
- **No Keywords/RSAs Found**: Informative message rather than error
- **API Errors**: Descriptive error messages with troubleshooting hints

## Performance Notes

- **Keyword Tool**: Very fast, uses simple Google Ads API query
- **RSA Tool**: Slightly slower due to complex ad asset queries
- **Large Ad Groups**: Both tools handle large ad groups efficiently
- **Rate Limiting**: Built-in respect for API rate limits

## Dependencies

```bash
pip install google-ads
```

## Best Practices

### For Keyword Analysis
1. **Export to CSV**: Use `--to-csv` for detailed analysis
2. **Regular Monitoring**: Track keyword distribution changes over time
3. **Match Type Strategy**: Use output to enforce match type policies
4. **Bid Analysis**: Examine `cpc_bid_micros` for bid management

### for RSA Analysis  
1. **Content Review**: Regularly review RSA content for quality
2. **Performance Correlation**: Use with performance data to identify top performers
3. **A/B Testing**: Document RSA variations for testing purposes
4. **Brand Compliance**: Verify messaging aligns with brand guidelines

### Integration Tips
1. **Workflow Integration**: Chain with recovery and audit tools
2. **Documentation**: Save outputs for compliance and auditing
3. **Automation**: Consider scripting regular analysis runs
4. **Alerting**: Monitor for unexpected changes in keyword counts or RSA content