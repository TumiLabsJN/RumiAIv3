#!/bin/bash

# safe_zip.sh — Clean and zip your RumiAI project safely
# Usage: bash safe_zip.sh [optional-output-filename.zip]

ZIP_NAME=${1:-rumiai_clean.zip}
EXCLUDE_DIRS=(
  "venv/*"
  "downloads/*"
  "temp/*"
  "frame_outputs/*"
  "enhanced_human_analysis_outputs/*"
  "unified_analysis/*"
  "insights/*"
  "__pycache__/*"
  "*.pyc"
  "*.pyo"
  "*.DS_Store"
  "*.log"
)

echo "🧼 Cleaning and packaging RumiAI project..."
echo "📦 Output zip: $ZIP_NAME"
echo ""

#!/bin/bash

# safe_zip.sh — Clean and zip your RumiAI project safely
# Usage: bash safe_zip.sh [optional-output-filename.zip]

ZIP_NAME=${1:-rumiai_clean.zip}
EXCLUDE_DIRS=(
  "venv/*"
  "downloads/*"
  "temp/*"
  "frame_outputs/*"
  "enhanced_human_analysis_outputs/*"
  "unified_analysis/*"
  "insights/*"
  "__pycache__/*"
  "*.pyc"
  "*.pyo"
  "*.DS_Store"
  "*.log"
)

echo "🧼 Cleaning and packaging RumiAI project..."
echo "📦 Output zip: $ZIP_NAME"
echo ""

# Build zip exclude pattern
EXCLUDES=()
for dir in "${EXCLUDE_DIRS[@]}"; do
  EXCLUDES+=("-x" "$dir")
done

# Create zip
zip -r "$ZIP_NAME" . -x "*/.*" "${EXCLUDES[@]}"

echo ""
echo "✅ Done! Created $ZIP_NAME excluding runtime outputs and envs."
du -sh "$ZIP_NAME"
