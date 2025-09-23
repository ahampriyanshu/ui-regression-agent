#!/bin/bash

echo "🚀 Running demo..."
bash scripts/install.sh
python3 app.py screenshots/production.png screenshots/preview.png
