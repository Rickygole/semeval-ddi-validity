set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/artifacts/rev3/rev3_bundle.tgz}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cd "$ROOT"
rsync -a --exclude __pycache__ --exclude '*.pyc' ddiood "$STAGE/"
cp requirements.txt requirements-gpu.txt "$STAGE/"

find "$STAGE" -name '.DS_Store' -delete
mkdir -p "$(dirname "$OUT")"
COPYFILE_DISABLE=1 tar -czf "$OUT" -C "$STAGE" .
echo "$OUT"
du -h "$OUT" | cut -f1
tar -tzf "$OUT" | grep -c -v '/$' | xargs echo "files:"
