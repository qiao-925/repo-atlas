#!/bin/bash

# This script automates the process of fetching, analyzing, and rendering the repo-atlas dashboard.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "--- Step 1: Fetching repository data ---"
python3 scripts/fetch_repos.py

echo "\n--- Step 2: Analyzing portfolio ---"
python3 scripts/analyze_portfolio.py

echo "\n--- Step 3: Rendering HTML dashboard ---"
python3 scripts/render_reports.py

echo "\n--- All steps completed successfully! ---"
echo "You can now open dashboard.html in your browser."
