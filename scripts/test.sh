#!/bin/bash

echo "🧪 Running tests..."
bash scripts/install.sh
python3 -m pytest tests/ -v --junit-xml=unit.xml -n auto
