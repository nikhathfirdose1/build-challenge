#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true

if [ "$#" -eq 0 ]; then
  python -m src.sales_analysis.runner \
    --top-n 5 \
    --month 2024-03
else
  python -m src.sales_analysis.runner "$@"
fi
