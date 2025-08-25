#!/usr/bin/env bash
# expand_geo.sh — append "in {State}" to each keyword in a seed CSV.
# Input/Output CSV columns (exact order):
# Action,Keyword status,Campaign,Ad group,Keyword,Match type
#
# Usage:
#   ./expand_geo.sh seeds.csv expanded.csv
#   ./expand_geo.sh seeds.csv expanded.csv --include-original
#
# Notes:
# - Preserves all non-keyword columns from the input.
# - Generates one row per seed × 50 states with
#   Keyword = "<seed> in <State>".
# - If --include-original is passed, original seed rows are kept too.
# - Assumes the input CSV has no embedded commas within fields.

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 input.csv output.csv [--include-original]" >&2
  exit 1
fi

IN="$1"
OUT="$2"
INCLUDE_ORIGINAL="${3:-}"

if [[ ! -f "$IN" ]]; then
  echo "Input file not found: $IN" >&2
  exit 1
fi

# 50 U.S. states
states=(
  "Alabama" "Alaska" "Arizona" "Arkansas" "California" "Colorado"
  "Connecticut" "Delaware" "Florida" "Georgia" "Hawaii" "Idaho"
  "Illinois" "Indiana" "Iowa" "Kansas" "Kentucky" "Louisiana"
  "Maine" "Maryland" "Massachusetts" "Michigan" "Minnesota"
  "Mississippi" "Missouri" "Montana" "Nebraska" "Nevada"
  "New Hampshire" "New Jersey" "New Mexico" "New York"
  "North Carolina" "North Dakota" "Ohio" "Oklahoma" "Oregon"
  "Pennsylvania" "Rhode Island" "South Carolina" "South Dakota"
  "Tennessee" "Texas" "Utah" "Vermont" "Virginia" "Washington"
  "West Virginia" "Wisconsin" "Wyoming"
)
# CSV escape: double any double-quotes
csv_escape() {
  local s="$1"
  printf '%s' "${s//\"/\"\"}"
}

# Read header, write it to output as-is
header="$(head -n1 "$IN")"
printf '%s\n' "$header" > "$OUT"

# Process rows (skip header). Split by ',' into 6 fields.
# Assumes no embedded commas in fields.
tail -n +2 "$IN" | while IFS=',' read -r action status campaign adgroup \
  keyword matchtype; do
  # Trim possible surrounding quotes
  action="${action%\"}";   action="${action#\"}"
  status="${status%\"}";   status="${status#\"}"
  campaign="${campaign%\"}"; campaign="${campaign#\"}"
  adgroup="${adgroup%\"}"; adgroup="${adgroup#\"}"
  keyword="${keyword%\"}"; keyword="${keyword#\"}"
  matchtype="${matchtype%\"}"; matchtype="${matchtype#\"}"

  # Optionally keep the original seed row
  if [[ "$INCLUDE_ORIGINAL" == "--include-original" ]]; then
    printf '"%s","%s","%s","%s","%s","%s"\n' \
      "$(csv_escape "$action")" \
      "$(csv_escape "$status")" \
      "$(csv_escape "$campaign")" \
      "$(csv_escape "$adgroup")" \
      "$(csv_escape "$keyword")" \
      "$(csv_escape "$matchtype")" >> "$OUT"
  fi

  # Add a geo-variant per state (prefix)
  for st in "${states[@]}"; do
    geo_kw="${st} ${keyword}"
    printf '"%s","%s","%s","%s","%s","%s"\n' \
      "$(csv_escape "$action")" \
      "$(csv_escape "$status")" \
      "$(csv_escape "$campaign")" \
      "$(csv_escape "$adgroup")" \
      "$(csv_escape "$geo_kw")" \
      "$(csv_escape "$matchtype")" >> "$OUT"
  done

  # Add a geo-variant per state (suffix)
  for st in "${states[@]}"; do
    geo_kw="${keyword} in ${st}"
    printf '"%s","%s","%s","%s","%s","%s"\n' \
      "$(csv_escape "$action")" \
      "$(csv_escape "$status")" \
      "$(csv_escape "$campaign")" \
      "$(csv_escape "$adgroup")" \
      "$(csv_escape "$geo_kw")" \
      "$(csv_escape "$matchtype")" >> "$OUT"
  done
done

echo "Wrote expanded CSV → $OUT"
