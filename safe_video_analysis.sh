#!/bin/bash

# Safe Video Analysis Runner - Prevents timeout issues
# Usage: ./safe_video_analysis.sh <tiktok_url>

URL=$1
if [ -z "$URL" ]; then
    echo "Usage: ./safe_video_analysis.sh <tiktok_url>"
    exit 1
fi

# Extract video ID from URL
VIDEO_ID=$(echo $URL | grep -oP '(?<=video/)\d+')
echo "📹 Video ID: $VIDEO_ID"

# Create log directory
mkdir -p logs

# Run with nohup to prevent interruption
echo "🚀 Starting analysis in background..."
echo "📝 Log file: logs/analysis_${VIDEO_ID}.log"

nohup node test_rumiai_complete_flow.js "$URL" > "logs/analysis_${VIDEO_ID}.log" 2>&1 &
PID=$!

echo "✅ Analysis started with PID: $PID"
echo ""
echo "📊 Monitor progress with:"
echo "   tail -f logs/analysis_${VIDEO_ID}.log"
echo ""
echo "🔍 Check if complete with:"
echo "   ls -la unified_analysis/${VIDEO_ID}.json"
echo ""
echo "💡 If interrupted, resume with:"
echo "   node resume_analysis.js $VIDEO_ID"