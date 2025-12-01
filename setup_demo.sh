#!/bin/bash
# Quick setup script for THE ROUNDTABLE Demo

echo "🎭 THE ROUNDTABLE - Demo Setup"
echo "================================"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# REQUIRED: Your Google Gemini API Key
# Get it from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-key-here

# OPTIONAL: Not needed for demo (we use mock data)
NOTION_TOKEN=
GOOGLE_OAUTH_CREDENTIALS=

# Settings
MAX_DEBATE_ROUNDS=3
EOF
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo "   Run: nano .env"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check if API key is set
if grep -q "GOOGLE_API_KEY=your-key-here" .env 2>/dev/null || ! grep -q "GOOGLE_API_KEY=" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: GOOGLE_API_KEY not configured!"
    echo "Please edit .env and add your API key from:"
    echo "https://aistudio.google.com/app/apikey"
    echo ""
fi

echo "To run the demo:"
echo "  1. Console version: python main_demo.py"
echo "  2. UI version: streamlit run streamlit_app.py"
echo ""
