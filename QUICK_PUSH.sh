#!/bin/bash
# Quick Push Script for Capstone Project
# Run this from your local machine to push all commits to GitHub

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║              CAPSTONE PROJECT - QUICK PUSH TO GITHUB                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will push 5 commits to https://github.com/rvats01/Capstone_Project.git"
echo ""
echo "Commits to push:"
echo "  1. be581b5 - Transform UI theme from dark to light colors"
echo "  2. 49d14d2 - Add specialized skills modules for agent capabilities"
echo "  3. d44d0b0 - Add comprehensive skills documentation"
echo "  4. 32fa4ab - Add skills implementation summary documentation"
echo "  5. 94731c0 - Add project completion report"
echo ""
echo "Total changes: 2,590+ lines of code and documentation"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Starting push..."
    echo ""
    
    # Check git status
    echo "Step 1: Checking git status..."
    git status
    echo ""
    
    # Push to origin main
    echo "Step 2: Pushing to origin main..."
    git push origin main -v
    
    # Verify push
    echo ""
    echo "Step 3: Verifying push..."
    git log -1 --format="%H %s"
    
    echo ""
    echo "✅ Push complete!"
    echo ""
    echo "Verify on GitHub:"
    echo "  https://github.com/rvats01/Capstone_Project/commits/main"
    echo ""
else
    echo "Push cancelled."
    exit 1
fi
