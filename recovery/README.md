# Recovery & Migration Tools

Tools for recovering deleted assets from Google Ads campaigns and migrating between ad formats (ETA to RSA conversion).

## Tools

### `recover_to_existing_ad_group.py`
**Purpose**: Copy keywords and RSAs from a REMOVED ad group into an existing ad group with intelligent deduplication.

**Key Features**:
- **Idempotent**: Safe to re-run multiple times
- **Deduplication**: Automatically skips existing keywords and RSAs
- **Match Type Control**: Force exact match for all recovered keywords
- **Safety Controls**: Option to create items in paused state
- **Negative Keywords**: Optional copying of negative keywords
- **Dry Run Mode**: Preview all changes before execution

### `rebuild_etas_as_rsas.py`
**Purpose**: Convert legacy Expanded Text Ads (ETAs) to Responsive Search Ads (RSAs) with intelligent content handling.

**Key Features**:
- **Pinning Options**: ETA-like pinning or flexible Google optimization
- **Content Padding**: Handle ETAs with insufficient headlines/descriptions
- **Deduplication**: Skip RSAs that already exist with same content
- **Safety Controls**: Create new RSAs in paused state
- **Dry Run Mode**: Preview all conversions before execution

## Recovery Tool Usage

### Basic Recovery
```bash
python recover_to_existing_ad_group.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222
```

### Safe Recovery with Preview
```bash
# 1. Dry run to preview changes
python recover_to_existing_ad_group.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222 \
  --dry-run \
  --copy-negatives

# 2. Execute with safety controls
python recover_to_existing_ad_group.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222 \
  --only-exact \
  --pause-on-create \
  --copy-negatives
```

### Command Line Arguments (Recovery)
- `--customer-id`: Google Ads customer ID (required)
- `--source-ad-group-id`: ID of the removed ad group to recover from (required)
- `--dest-ad-group-id`: ID of the existing ad group to copy to (required)
- `--dry-run`: Preview changes without executing (recommended first)
- `--only-exact`: Force all keywords to exact match type
- `--pause-on-create`: Create new keywords and ads in paused state
- `--copy-negatives`: Include negative keywords in the recovery process

## ETA to RSA Migration Usage

### Basic Migration
```bash
python rebuild_etas_as_rsas.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222
```

### Advanced Migration with Options
```bash
# Preview with padding for incomplete ETAs
python rebuild_etas_as_rsas.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222 \
  --dry-run \
  --pad-mode generic \
  --no-pin

# Execute with safe defaults
python rebuild_etas_as_rsas.py \
  --customer-id 1234567890 \
  --source-ad-group-id 111111111 \
  --dest-ad-group-id 222222222 \
  --pause-on-create \
  --pad-mode skip
```

### Command Line Arguments (Migration)
- `--customer-id`: Google Ads customer ID (required)  
- `--source-ad-group-id`: ID of ad group containing ETAs (required)
- `--dest-ad-group-id`: ID of ad group to create RSAs in (required)
- `--dry-run`: Preview conversions without creating RSAs
- `--pad-mode`: How to handle ETAs with insufficient content:
  - `skip`: Only convert ETAs with ≥3 headlines and ≥2 descriptions (default)
  - `generic`: Pad missing content with safe filler text
- `--no-pin`: Allow Google to optimize headline/description placement (vs ETA-like pinning)
- `--pause-on-create`: Create new RSAs in paused state

## Workflow Examples

### Complete Asset Recovery
```bash
# Step 1: Analyze source ad group (if still accessible)
python ../analysis/list_positive_keywords.py --customer-id CID --ad-group-id SOURCE_ID
python ../analysis/list_rsas_summary.py --customer-id CID --ad-group-id SOURCE_ID

# Step 2: Preview keyword recovery
python recover_to_existing_ad_group.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --dry-run \
  --copy-negatives

# Step 3: Execute keyword recovery
python recover_to_existing_ad_group.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --only-exact \
  --pause-on-create \
  --copy-negatives

# Step 4: Preview ETA to RSA conversion
python rebuild_etas_as_rsas.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --dry-run \
  --pad-mode generic

# Step 5: Execute ETA conversion
python rebuild_etas_as_rsas.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --pause-on-create \
  --pad-mode generic

# Step 6: Validate results
python ../analysis/list_positive_keywords.py --customer-id CID --ad-group-id DEST_ID
python ../analysis/list_rsas_summary.py --customer-id CID --ad-group-id DEST_ID
```

### Emergency Recovery (Fast)
```bash
# Quick recovery of essential assets
python recover_to_existing_ad_group.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --only-exact

python rebuild_etas_as_rsas.py \
  --customer-id CID \
  --source-ad-group-id SOURCE_ID \
  --dest-ad-group-id DEST_ID \
  --pad-mode skip
```

## Safety Features

### Idempotent Operations
Both tools are safe to re-run:
- **Keywords**: Deduplicated by (text, match_type, negative_flag)
- **RSAs**: Deduplicated by (headlines, descriptions, URLs, paths)
- **No Duplicates**: Existing assets are automatically skipped

### Dry Run Mode
Always available for preview:
```bash
--dry-run  # Shows what would be created without making changes
```

### Validation Checks
- Source ad group accessibility verification
- Destination ad group existence check  
- Customer account access validation
- API connectivity testing

### Error Recovery
- **Partial Failures**: Operations continue after individual item failures
- **Detailed Logging**: Clear error messages for troubleshooting
- **Rollback Safe**: No modifications on validation failures

## Content Handling (ETA to RSA)

### Padding Modes

#### Skip Mode (Default)
- Only converts ETAs with sufficient content (≥3 headlines, ≥2 descriptions)
- Safest option, no content modification
- Use when ETA content is already RSA-ready

#### Generic Mode
- Pads insufficient content with unique, safe filler
- Example filler headlines: "Learn More", "Get Started", "Discover Options"  
- Example filler descriptions: "Find the solution that works for you.", "Quality service you can trust."
- Use when you need to convert all ETAs regardless of content completeness

### Pinning Strategies

#### Default (ETA-like pinning)
- Headline 1 → RSA Headline 1 (pinned to position 1)
- Headline 2 → RSA Headline 2 (pinned to position 2)  
- Headline 3 → RSA Headline 3 (pinned to position 3)
- Description 1 → RSA Description 1 (pinned to position 1)
- Description 2 → RSA Description 2 (pinned to position 2)
- Maintains ETA appearance and control

#### No Pinning (`--no-pin`)
- All headlines and descriptions unpinned
- Google optimizes placement automatically
- Better for performance but less control

## Output and Logging

### Console Output
- **Progress Indicators**: Real-time operation status
- **Statistics**: Counts of created, skipped, and failed items
- **Error Details**: Specific failure reasons with suggested fixes

### Example Output
```
=== DRY RUN MODE ===
Source ad group 111111111: 25 positive keywords, 5 negative keywords, 3 RSAs

Would create in destination ad group 222222222:
  Keywords (positive):
    - "online school" [exact] (NEW)
    - "distance learning" [exact] (SKIP: already exists)
    [... more keywords ...]
  
  Keywords (negative):  
    - "free" [exact] (NEW)
    [... more negatives ...]
    
  RSAs:
    - RSA with headlines: ["Best School", "Top Education", "Learn Online"] (NEW)
    [... more RSAs ...]

Summary: Would create 20 positive keywords, 3 negative keywords, 2 RSAs
```

## Error Scenarios & Solutions

### "Source ad group not found"
- **Cause**: Ad group was permanently deleted or wrong ID
- **Solution**: Verify ID, check if recently deleted (may be recoverable via Google Ads UI)

### "Destination ad group not accessible"
- **Cause**: Wrong customer ID, insufficient permissions, or ad group doesn't exist
- **Solution**: Verify customer ID and ad group ID, check account access

### "Insufficient headlines for RSA"
- **Cause**: ETA has < 3 headlines and `--pad-mode skip` is used
- **Solution**: Use `--pad-mode generic` or manually add headlines to source ETA first

### "Keywords already exist"
- **Cause**: Previous recovery attempt or manual keyword additions
- **Solution**: This is normal behavior (idempotent), tool will skip duplicates

### "RSA creation failed: DUPLICATE_CONTENT"
- **Cause**: RSA with identical content already exists in destination
- **Solution**: This is expected behavior, tool skips duplicates automatically

## Best Practices

### Before Recovery
1. **Document State**: Screenshot or export current ad group state
2. **Dry Run Always**: Never skip the `--dry-run` preview
3. **Validate IDs**: Double-check source and destination ad group IDs
4. **Account Access**: Verify permissions with auth tools

### During Recovery
1. **Monitor Progress**: Watch console output for errors
2. **Pause on Create**: Use `--pause-on-create` for manual review
3. **Force Exact**: Use `--only-exact` for strict match type control
4. **Include Negatives**: Use `--copy-negatives` for complete recovery

### After Recovery
1. **Validate Results**: Use analysis tools to verify successful recovery
2. **Review Content**: Manually check RSA content quality
3. **Enable Gradually**: Unpause recovered assets in phases
4. **Monitor Performance**: Track performance of recovered assets

### Operational Guidelines
1. **Test Environment**: Practice on non-production accounts first
2. **Backup Strategy**: Export data before major recovery operations
3. **Documentation**: Keep records of recovery operations and outcomes
4. **Team Communication**: Coordinate recovery efforts with team members

## Dependencies

```bash
pip install google-ads
```

## Integration with Other Tools

- **Use with Analysis Tools**: Validate recovery results
- **Use with Audit Tools**: Check recovered asset compliance  
- **Use with Data Processing**: Process recovered keywords for geo expansion