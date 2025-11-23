#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true

if [ "$#" -eq 0 ]; then
  python -m src.producer_consumer.runner \
    --items 15 \
    --buffer-capacity 5 \
    --producers 2 \
    --consumers 3 \
    --delay 0.0
else
  python -m src.producer_consumer.runner "$@"
fi
