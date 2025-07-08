#!/usr/bin/env python3
"""
Run a single Claude prompt for debugging/testing
"""

import sys
import json
import os
from pathlib import Path
from run_claude_insight import ClaudeInsightRunner

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_claude_single_prompt.py <video_id> <prompt_name>")
        print("Example: python run_claude_single_prompt.py 7395982344001309957 creative_density")
        sys.exit(1)
    
    video_id = sys.argv[1]
    prompt_name = sys.argv[2]
    
    # Load unified analysis
    unified_path = Path(f'unified_analysis/{video_id}.json')
    if not unified_path.exists():
        print(f"Error: Unified analysis not found at {unified_path}")
        sys.exit(1)
    
    with open(unified_path, 'r') as f:
        unified_data = json.load(f)
    
    # Get prompt text (simplified for testing)
    prompt_texts = {
        'creative_density': "Analyze the creative density and pacing of this TikTok video...",
        'emotional_journey': "Analyze the emotional journey of this video...",
        'speech_analysis': "Analyze the speech patterns and delivery...",
        'visual_overlay_analysis': "Analyze visual overlays and text elements...",
        'metadata_analysis': "Analyze the metadata, captions, and hashtags...",
        'person_framing': "Analyze how people are framed in this video...",
        'scene_pacing': "Analyze the scene changes and pacing..."
    }
    
    prompt_text = prompt_texts.get(prompt_name, "Analyze this video...")
    
    # Run the prompt
    runner = ClaudeInsightRunner()
    result = runner.run_claude_prompt(
        video_id=video_id,
        prompt_name=prompt_name,
        prompt_text=prompt_text,
        context_data=unified_data
    )
    
    if result['success']:
        print(f"✅ {prompt_name} completed successfully")
        sys.exit(0)
    else:
        print(f"❌ {prompt_name} failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()