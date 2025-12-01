#!/bin/bash
# Quick launch script for THE ROUNDTABLE Streamlit UI

echo "🎭 Launching THE ROUNDTABLE - Animated Edition..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Streamlit not found. Installing..."
    pip install streamlit>=1.39.0
fi

echo "🚀 Starting Streamlit app..."
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py
