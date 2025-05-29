#!/usr/bin/env bash
set -euo pipefail
CWD="$(pwd)"
trap "cd $CWD" EXIT
cd "$(dirname "$0")"
rm -rf ./venv
python -m venv ./venv
source ./venv/bin/activate
poetry install
