set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/artifacts/amend7"
OUT="${1:-$A/amend7_bundle.tgz}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cd "$ROOT"
mkdir -p "$STAGE/amend7"
rsync -a --exclude __pycache__ --exclude '*.pyc' ddiood "$STAGE/"
cp requirements.txt requirements-gpu.txt "$STAGE/"
for f in train_pairs.csv retrieval.json lookup.json di_sections.json stem_names.json primary_sets.json input_audit.json manifest.json panel_manifest.json hub_candidates.json; do
  cp "$A/$f" "$STAGE/amend7/"
done
cp artifacts/bundle/delta_amend1.json.gz "$STAGE/amend7/"

find "$STAGE" -name '.DS_Store' -delete
mkdir -p "$(dirname "$OUT")"
COPYFILE_DISABLE=1 tar -czf "$OUT" -C "$STAGE" .
echo "$OUT"
du -h "$OUT" | cut -f1
ls -l "$OUT" | awk '{print $5, "bytes"}'
tar -tzf "$OUT" | grep -c -v '/$' | xargs echo "files:"
tar -tzvf "$OUT" | awk '{print $5, $NF}' | sort -rn | head -8
