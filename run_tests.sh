#!/usr/bin/env bash
# run_tests.sh — Automate the Quantium Dash test suite.
#
# Run from any directory; the script moves to the project root automatically.
#
#   bash run_tests.sh
#
# Exit 0 if all tests pass, 1 if any fail (or the setup broke).
# Designed for local use and CI pipelines (GitHub Actions, GitLab CI, etc.).

set -eu

cd "$(dirname "$0")"

# ── Activate the virtual environment ──────────────────────────────────────
# On Windows (Git Bash) the activate script may have CRLF line endings which
# sourcing chokes on, so we prefer calling the venv python directly.
PYTHON=".venv/Scripts/python.exe"

# If the script is running on a POSIX-y system (Linux / macOS / WSL) source
# the activate script instead so PATH is updated properly.
if [ -f ".venv/bin/activate" ]; then
    # POSIX venv (Linux, macOS, WSL)
    # shellcheck disable=SC1091
    source .venv/bin/activate
    PYTHON=python
fi

# ── Run the test suite ────────────────────────────────────────────────────
echo "==> Running Dash test suite ..."
if $PYTHON -m pytest tests/ -v; then
    echo ""
    echo "==> All tests passed."
    exit 0
else
    echo ""
    echo "==> Some tests FAILED."
    exit 1
fi
