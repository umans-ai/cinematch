#!/usr/bin/env bash
set -e

echo "🔧 Installing git hooks..."

# Configure git to use .githooks directory
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/pre-commit
chmod +x .githooks/pre-push

echo "✅ Git hooks installed"
echo ""
echo "Hooks installed:"
echo "  • pre-commit: Runs 'just check' before each commit"
echo "  • pre-push:   Runs 'just check' before push (safety net)"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
