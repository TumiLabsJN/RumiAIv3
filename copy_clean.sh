#!/bin/bash

# copy_clean.sh — Create a lightweight local copy of RumiAI excluding all heavy outputs

SOURCE_DIR=${1:-.}
DEST_DIR=${2:-../rumiai_clean_copy}

echo "📁 Creating clean copy of RumiAI..."
echo "🔍 Source: $SOURCE_DIR"
echo "📦 Destination: $DEST_DIR"
echo ""

# Run rsync with exclusion rules from .rsyncignore.local
rsync -av --exclude-from="$SOURCE_DIR/.rsyncignore.local" "$SOURCE_DIR/" "$DEST_DIR/"

echo ""
echo "✅ Done: Clean copy created at $DEST_DIR"
echo "🧪 Tip: Run python setup/bootstrap.py in the new copy before test execution"
