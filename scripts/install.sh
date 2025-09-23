#!/bin/bash

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
bash scripts/cleanup.sh
bash scripts/seed.sh
