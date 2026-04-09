#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f "env/bin/activate" ]]; then
    source env/bin/activate
elif [[ -f "env/Scripts/activate" ]]; then
    source env/Scripts/activate
else
    echo "Error: virtual environment not found"
    exit 1
fi

python git_backup.py update-list && python git_backup.py readme && python git_backup.py zip
