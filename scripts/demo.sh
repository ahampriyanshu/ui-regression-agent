#!/bin/bash

echo "🚀 Running demo..."
bash scripts/install.sh
python3 app.py screenshots/baseline.png screenshots/updated.png
