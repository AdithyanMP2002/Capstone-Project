#!/bin/bash
# Helper script to push The Roundtable to GitHub

echo "🚀 Preparing to push 'The Roundtable' to GitHub..."
echo "---------------------------------------------------"

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI (gh) found."
    echo "   Creating private repository 'the-roundtable'..."
    
    # Create repo (fails gracefully if exists)
    gh repo create the-roundtable --private --source=. --remote=origin --push || echo "⚠️  Repo might already exist or auth failed. Continuing..."
    
else
    echo "ℹ️  GitHub CLI not found. Using standard git."
    echo ""
    echo "   Please enter your GitHub repository URL (e.g., https://github.com/username/the-roundtable.git):"
    read -r REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
    
    git remote add origin "$REPO_URL" || git remote set-url origin "$REPO_URL"
fi

echo ""
echo "📦 Pushing code and tags..."
git push -u origin master
git push origin V1-Local

echo ""
echo "✅ Done! Your code is now on GitHub."
echo "   Tag: V1-Local"
