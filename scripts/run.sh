#!/bin/bash

echo "🌐 Starting web app..."
bash scripts/install.sh
streamlit run app.py --server.port 8000
