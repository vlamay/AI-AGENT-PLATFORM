#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🚀 AI AGENT PLATFORM - PUSH TO GITHUB                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd /home/devops/Downloads/AI-AGENT-PLATFORM

echo "📊 Repository Status:"
git status -s
echo ""

echo "📦 Total Files: $(git ls-files | wc -l)"
echo "📝 Commits: $(git rev-list --all --count)"
echo ""

read -p "Do you want to push to GitHub now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔐 Choose authentication method:"
    echo "1) Personal Access Token"
    echo "2) GitHub CLI"
    echo "3) SSH Key"
    echo ""
    read -p "Enter choice (1-3): " auth_choice
    
    case $auth_choice in
        1)
            echo ""
            echo "📋 To use Personal Access Token:"
            echo "1. Visit: https://github.com/settings/tokens"
            echo "2. Generate new token with 'repo' permissions"
            echo "3. Run this command with your token:"
            echo ""
            echo "git push https://YOUR_TOKEN@github.com/vlamay/AI-AGENT-PLATFORM.git main"
            ;;
        2)
            echo ""
            echo "🔑 Checking GitHub CLI..."
            if command -v gh &> /dev/null; then
                gh auth login
                git push -u origin main
            else
                echo "❌ GitHub CLI not installed. Install with:"
                echo "sudo apt install gh"
            fi
            ;;
        3)
            echo ""
            echo "🔑 Changing remote to SSH..."
            git remote set-url origin git@github.com:vlamay/AI-AGENT-PLATFORM.git
            git push -u origin main
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
else
    echo "Push cancelled. Run this script again when ready."
fi

echo ""
echo "✅ Done!"
echo "🌐 Check repository at: https://github.com/vlamay/AI-AGENT-PLATFORM"

