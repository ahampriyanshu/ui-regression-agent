#!/bin/bash

echo "🧹 Cleaning workspace..."
rm -f data/databases/*.db
rm -rf .pytest_cache/
rm -rf tests/__pycache__/
rm -rf data/__pycache__/
rm -rf mcp_servers/__pycache__/
rm -rf __pycache__/
rm -f unit.xml