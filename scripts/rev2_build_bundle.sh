set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
A="$ROOT/artifacts/amend7"
OUT="${1:-$ROOT/artifacts/rev2/rev2_bundle.tgz}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cd "$ROOT"
mkdir -p "$STAGE/amend7" "$STAGE/rev2"
rsync -a --exclude __pycache__ --exclude '*.pyc' ddiood "$STAGE/"
cp requirements.txt requirements-gpu.txt "$STAGE/"
for f in train_pairs.csv di_sections.json primary_sets.json manifest.json; do
  cp "$A/$f" "$STAGE/amend7/"
done
cp results/revision/post8/label_audit_sheet.csv "$STAGE/rev2/"

find "$STAGE" -name '.DS_Store' -delete
mkdir -p "$(dirname "$OUT")"
COPYFILE_DISABLE=1 tar -czf "$OUT" -C "$STAGE" .
echo "$OUT"
du -h "$OUT" | cut -f1
ls -l "$OUT" | awk '{print $5, "bytes"}'
tar -tzf "$OUT" | grep -c -v '/$' | xargs echo "files:"
tar -tzvf "$OUT" | awk '{print $5, $NF}' | sort -rn | head -8
