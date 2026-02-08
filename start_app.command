#!/bin/bash
cd "$(dirname "$0")"

# Check if .venv exists, if so activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the streamlit app
streamlit run app.py
