# txt_to_seed_csv.sh
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 keywords.txt seeds.csv 'Campaign Name' ['Ad Group Name']" >&2
  exit 1
fi

IN="$1"
OUT="$2"
CAMPAIGN="$3"
ADGROUP="${4:-General}"
ACTION="Add"
STATUS="Enabled"
MATCH="[exact]"   # keep the literal [exact] text or put Exact if you like

echo 'Action,Keyword status,Campaign,Ad group,Keyword,Match type' > "$OUT"

# read keywords and write rows
while IFS= read -r kw; do
  [[ -z "${kw// }" ]] && continue
  # minimal CSV quoting
  kw="${kw%$'\r'}"
  printf '"%s","%s","%s","%s","%s","%s"\n' \
    "$ACTION" "$STATUS" "$CAMPAIGN" "$ADGROUP" "$kw" "$MATCH" >> "$OUT"
done < "$IN"

echo "Wrote seed CSV → $OUT"
