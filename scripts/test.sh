#!/bin/bash

echo "🧪 Running tests..."
bash scripts/exec.sh
python3 -m pytest tests/ -v --junit-xml=unit.xml -n auto
