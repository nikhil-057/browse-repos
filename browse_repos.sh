#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./venv/bin/activate
python ./browse_repos.py
