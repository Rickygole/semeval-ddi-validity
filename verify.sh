#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  if command -v python3.11 >/dev/null 2>&1; then PY=python3.11; else PY=python3; fi
fi
VENV="${VERIFY_VENV:-.venv}"
if [ ! -x "$VENV/bin/python" ]; then
  "$PY" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q -r requirements-verify.txt
fi
exec "$VENV/bin/python" scripts/verify_release.py "$@"
