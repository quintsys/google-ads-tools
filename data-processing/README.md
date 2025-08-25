# Data Processing Tools

Tools for transforming and processing Google Ads campaign data, including keyword expansion and format conversion.

## Tools

### `expand_geo.py`
**Purpose**: Generate geographic keyword variations by expanding seed keywords with US states, metro areas, or both.

**Key Features**:
- **Multiple Expansion Modes**: States, metros, or combined
- **Flexible Output**: Control original keyword inclusion
- **Smart Combinations**: Prefix and suffix variations
- **CSV Processing**: Maintains Google Ads CSV format compatibility

### `txt_to_seed_csv.sh`
**Purpose**: Convert a simple text file of keywords into Google Ads CSV bulk upload format.

**Key Features**:
- **Simple Input**: Plain text file, one keyword per line
- **CSV Output**: Properly formatted for Google Ads Editor
- **Configurable**: Customizable campaign, ad group, and match type
- **Clean Processing**: Handles line endings and empty lines

## Geographic Expansion Tool

### Basic Usage
```bash
# Expand with US states only
python expand_geo.py --input seeds.csv --output expanded_states.csv --mode states

# Expand with metro areas only  
python expand_geo.py --input seeds.csv --output expanded_metros.csv --mode metros

# Expand with both states and metros
python expand_geo.py --input seeds.csv --output expanded_all.csv --mode all

# Include original keywords in output
python expand_geo.py \
  --input seeds.csv \
  --output expanded_with_originals.csv \
  --mode states \
  --include-original
```

### Input CSV Format
The tool expects Google Ads CSV format:
```csv
Action,Keyword status,Campaign,Ad group,Keyword,Match type
Add,Enabled,My Campaign,My Ad Group,online school,[exact]
Add,Enabled,My Campaign,My Ad Group,distance learning,[exact]
```

### Expansion Modes

#### States Mode (`--mode states`)
Generates variations using all 50 US states:
- `"online school"` → `"Alabama online school"`, `"online school in Alabama"`, etc.
- Creates 100 variations per seed keyword (50 prefix + 50 suffix)

#### Metros Mode (`--mode metros`)  
Generates variations using major US metropolitan areas:
- `"online school"` → `"Atlanta online school"`, `"online school in Atlanta"`, etc.
- Creates variations for 50+ major metros

#### All Mode (`--mode all`)
Combines both states and metros:
- Generates both state and metro variations
- Largest output but comprehensive coverage

### Geographic Lists

#### US States (50 total)
Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming

#### Metro Areas (50+ total)
Atlanta, Austin, Baltimore, Boston, Charlotte, Chicago, Cincinnati, Cleveland, Columbus, Dallas, Denver, Detroit, Houston, Indianapolis, Jacksonville, Kansas City, Las Vegas, Los Angeles, Louisville, Memphis, Miami, Milwaukee, Minneapolis, Nashville, New Orleans, New York, Oklahoma City, Orlando, Philadelphia, Phoenix, Pittsburgh, Portland, Raleigh, Richmond, Sacramento, Salt Lake City, San Antonio, San Diego, San Francisco, Seattle, St. Louis, Tampa, Virginia Beach, Washington DC

### Command Line Arguments
- `--input`: Input CSV file path (required)
- `--output`: Output CSV file path (required)  
- `--mode`: Expansion mode - choices: states, metros, all (required)
- `--include-original`: Include original seed keywords in output (optional)

### Output Statistics
```bash
python expand_geo.py --input seeds.csv --output expanded.csv --mode states

# Example output:
# Processing 10 seed keywords...
# Generated 1,000 state variations (50 states × 10 seeds × 2 patterns)
# Wrote expanded CSV → expanded.csv
```

## Text to CSV Conversion Tool

### Basic Usage
```bash
# Convert keywords.txt to CSV format
./txt_to_seed_csv.sh keywords.txt seeds.csv "My Campaign" "My Ad Group"

# Use default ad group name
./txt_to_seed_csv.sh keywords.txt seeds.csv "My Campaign"
```

### Input Format
Simple text file with one keyword per line:
```
online school
distance learning  
remote education
virtual classroom
homeschool programs
```

### Output Format
Google Ads CSV format:
```csv
Action,Keyword status,Campaign,Ad group,Keyword,Match type
Add,Enabled,My Campaign,My Ad Group,online school,[exact]
Add,Enabled,My Campaign,My Ad Group,distance learning,[exact]
Add,Enabled,My Campaign,My Ad Group,remote education,[exact]
Add,Enabled,My Campaign,My Ad Group,virtual classroom,[exact]
Add,Enabled,My Campaign,My Ad Group,homeschool programs,[exact]
```

### Script Configuration
You can modify default values by editing the script:
- `ACTION="Add"` - Operation type
- `STATUS="Enabled"` - Default keyword status  
- `MATCH="[exact]"` - Default match type
- `ADGROUP="${4:-General}"` - Default ad group name

## Workflow Examples

### Complete Keyword Processing Pipeline
```bash
# Step 1: Convert text file to seed CSV
./txt_to_seed_csv.sh keywords.txt seeds.csv "Education Campaign" "Online School"

# Step 2: Generate geographic variations
python expand_geo.py --input seeds.csv --output geo_expanded.csv --mode states

# Step 3: Review output
head -20 geo_expanded.csv
wc -l geo_expanded.csv

# Step 4: Upload to Google Ads Editor or use with other tools
```

### Selective Geographic Expansion
```bash
# Create separate files for different geographic strategies
python expand_geo.py --input seeds.csv --output states_only.csv --mode states
python expand_geo.py --input seeds.csv --output metros_only.csv --mode metros

# Combine different strategies
python expand_geo.py --input high_value_keywords.csv --output premium_geo.csv --mode all --include-original
python expand_geo.py --input broad_keywords.csv --output broad_geo.csv --mode states
```

### Quality Control Workflow
```bash
# Generate with originals for comparison
python expand_geo.py --input seeds.csv --output expanded_with_originals.csv --mode states --include-original

# Count variations per seed
python -c "
import csv
with open('expanded_with_originals.csv') as f:
    reader = csv.DictReader(f)
    keywords = [row['Keyword'] for row in reader]
    print(f'Total keywords: {len(keywords)}')
    print(f'Unique keywords: {len(set(keywords))}')
"
```

## Best Practices

### Geographic Expansion
1. **Start Small**: Test with a few seed keywords first
2. **Review Output**: Always examine a sample of generated keywords
3. **Consider Volume**: Geographic expansion can create very large keyword lists
4. **Quality Over Quantity**: Use selective expansion rather than expanding everything
5. **Monitor Performance**: Track which geographic variations perform best

### File Management
1. **Naming Convention**: Use descriptive file names with dates
2. **Backup Seeds**: Keep original seed files safe
3. **Version Control**: Track different expansion iterations
4. **Size Limits**: Be aware of Google Ads Editor and upload limits

### Performance Considerations
1. **Large Files**: Geographic expansion can create very large files
2. **Memory Usage**: Tools handle large files efficiently but monitor system resources
3. **Processing Time**: Expansion is fast but large seed files may take time
4. **Disk Space**: Ensure sufficient space for output files

## Integration Examples

### With Analysis Tools
```bash
# Process keywords, then analyze in existing ad groups
./txt_to_seed_csv.sh keywords.txt seeds.csv "Campaign" "Ad Group"
python expand_geo.py --input seeds.csv --output expanded.csv --mode states

# After uploading, analyze results
python ../analysis/list_positive_keywords.py --customer-id CID --ad-group-id AGID
```

### With Recovery Tools
```bash
# Expand recovered keywords geographically  
python ../recovery/recover_to_existing_ad_group.py [recovery options] --to-csv recovered_keywords.csv
python expand_geo.py --input recovered_keywords.csv --output geo_recovered.csv --mode metros
```

### With Audit Tools
```bash
# Process and audit in one workflow
./txt_to_seed_csv.sh keywords.txt seeds.csv "Test Campaign" "Test Ad Group"
python expand_geo.py --input seeds.csv --output expanded.csv --mode states

# After upload, audit the campaign
python ../audit/ads_audit.py --customer-id CID --out audit_results
```

## File Size Considerations

### Expansion Calculations
- **States mode**: `seeds × 100` keywords (50 prefix + 50 suffix)
- **Metros mode**: `seeds × 100+` keywords (depends on metro count)
- **All mode**: `seeds × 200+` keywords
- **With originals**: Add original seed count

### Example File Sizes
- 10 seeds + states = 1,000 keywords
- 100 seeds + states = 10,000 keywords  
- 10 seeds + all modes = 2,000+ keywords
- 100 seeds + all modes = 20,000+ keywords

### Google Ads Limits
- Google Ads Editor: 50,000 rows per file
- Bulk upload: Various limits by account type
- Ad group limits: 20,000 keywords per ad group

## Error Handling

### Common Issues
- **File Not Found**: Verify input file path
- **Permission Denied**: Check file permissions for output directory
- **Invalid CSV Format**: Ensure input CSV has required columns
- **Empty Input**: Handle files with no valid keywords
- **Disk Space**: Ensure sufficient space for large expansions

### Validation
Both tools include validation:
- Input file existence checks
- Output directory writability
- CSV format validation
- Empty line handling
- Character encoding support

## Dependencies

### Python Tool
```bash
pip install csv argparse itertools  # Usually included with Python
```

### Shell Script
- Bash shell (standard on macOS/Linux)
- Standard Unix utilities (sed, awk, grep)

## Advanced Usage

### Custom Geographic Lists
You can modify `expand_geo.py` to use custom geographic lists:
1. Edit the `STATES` and `METROS` lists in the script
2. Add new expansion modes
3. Customize expansion patterns (prefix/suffix)

### Bulk Processing
```bash
# Process multiple seed files
for file in seeds_*.csv; do
    output="expanded_${file}"
    python expand_geo.py --input "$file" --output "$output" --mode states
done
```

### Integration Scripting
```bash
#!/bin/bash
# Complete processing pipeline
INPUT_TEXT="$1"
CAMPAIGN="$2"
ADGROUP="$3"

./txt_to_seed_csv.sh "$INPUT_TEXT" seeds.csv "$CAMPAIGN" "$ADGROUP"
python expand_geo.py --input seeds.csv --output final_keywords.csv --mode states
echo "Processed $(wc -l < final_keywords.csv) keywords ready for upload"
```