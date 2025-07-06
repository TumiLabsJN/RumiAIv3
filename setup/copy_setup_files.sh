#!/bin/bash
# Copy all necessary setup files to a target directory
# Usage: ./copy_setup_files.sh /path/to/new/repo

TARGET_DIR="$1"

if [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 /path/to/new/repo"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory $TARGET_DIR does not exist"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📋 Copying setup files to $TARGET_DIR..."

# Create setup directory
mkdir -p "$TARGET_DIR/setup"

# Copy setup scripts
cp "$SCRIPT_DIR/bootstrap.py" "$TARGET_DIR/setup/" && echo "✅ Copied bootstrap.py"
cp "$SCRIPT_DIR/requirements_check.py" "$TARGET_DIR/setup/" && echo "✅ Copied requirements_check.py"
cp "$SCRIPT_DIR/verify_setup.py" "$TARGET_DIR/setup/" && echo "✅ Copied verify_setup.py"
cp "$SCRIPT_DIR/setup_helper.py" "$TARGET_DIR/setup/" && echo "✅ Copied setup_helper.py"
cp "$SCRIPT_DIR/generate_py312_requirements.py" "$TARGET_DIR/setup/" && echo "✅ Copied generate_py312_requirements.py"
cp "$SCRIPT_DIR/README.md" "$TARGET_DIR/setup/" && echo "✅ Copied setup README.md"

# Copy requirements files
cp "$PARENT_DIR/requirements.txt" "$TARGET_DIR/" && echo "✅ Copied requirements.txt"
cp "$PARENT_DIR/requirements_py312.txt" "$TARGET_DIR/" && echo "✅ Copied requirements_py312.txt"

# Copy package.json if it exists
if [ -f "$PARENT_DIR/package.json" ]; then
    cp "$PARENT_DIR/package.json" "$TARGET_DIR/" && echo "✅ Copied package.json"
fi

# Copy prompt templates directory
if [ -d "$PARENT_DIR/prompt_templates" ]; then
    cp -r "$PARENT_DIR/prompt_templates" "$TARGET_DIR/" && echo "✅ Copied prompt_templates directory"
fi

# Create .env.example if it doesn't exist
if [ ! -f "$TARGET_DIR/.env.example" ]; then
    cat > "$TARGET_DIR/.env.example" << 'EOF'
# RumiAI Environment Variables

# Required API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
APIFY_TOKEN=your-apify-token-here

# Optional Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
PORT=3001
RUMIAI_TEST_MODE=true
YOLO_FRAME_SKIP=2
CLEANUP_VIDEO=false
CLAUDE_API_URL=https://api.anthropic.com/v1/messages
EOF
    echo "✅ Created .env.example"
fi

echo ""
echo "✅ Setup files copied successfully!"
echo ""
echo "Next steps:"
echo "1. cd $TARGET_DIR"
echo "2. cp .env.example .env"
echo "3. Edit .env with your API keys"
echo "4. python3 setup/bootstrap.py"
echo "5. python3 setup/verify_setup.py"