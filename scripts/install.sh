#!/bin/bash

echo "📦 Installing dependencies..."
pip install -q --disable-pip-version-check -r requirements.txt
bash scripts/cleanup.sh
bash scripts/seed.sh
