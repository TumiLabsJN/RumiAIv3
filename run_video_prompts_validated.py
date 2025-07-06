#!/usr/bin/env python3
"""
Run Claude prompts with ML data validation
Ensures only real ML detection data is sent to Claude for analysis
"""

import os
import sys
import json
import argparse
from datetime import datetime
from ml_data_validator import MLDataValidator, validate_ml_data
from run_claude_insight import ClaudeInsightRunner

def load_unified_analysis(video_id):
    """Load unified analysis data for a video"""
    unified_file = f"unified_analysis_{video_id}.json"
    
    if not os.path.exists(unified_file):
        print(f"Error: Unified analysis file not found: {unified_file}")
        print("Please run the complete video analysis first.")
        return None
    
    with open(unified_file, 'r') as f:
        return json.load(f)

def save_validated_data(video_id, prompt_type, validated_data):
    """Save validated data for inspection"""
    output_file = f"validated_data_{video_id}_{prompt_type}.json"
    with open(output_file, 'w') as f:
        json.dump(validated_data, f, indent=2)
    print(f"Validated data saved to: {output_file}")

def run_validated_prompt(video_id, prompt_type, validate_only=False):
    """Run a specific prompt with validated ML data"""
    
    # Load unified analysis
    unified_data = load_unified_analysis(video_id)
    if not unified_data:
        return False
    
    # Validate and extract ML data
    print(f"Validating ML data for prompt type: {prompt_type}")
    validator = MLDataValidator()
    validated_data = validator.extract_real_ml_data(unified_data, prompt_type)
    
    # Get validation report
    validation_report = validator.get_validation_report()
    print(f"Validation complete: {validation_report['summary']}")
    
    # Save validated data
    save_validated_data(video_id, prompt_type, validated_data)
    
    if validate_only:
        print("Validation-only mode: Data validated and saved, no Claude prompts run.")
        return True
    
    # Prepare prompt data
    prompt_data = {
        'video_id': video_id,
        'validated_ml_data': validated_data,
        'validation_report': validation_report['summary']
    }
    
    # Run Claude prompt
    runner = ClaudeInsightRunner()
    
    try:
        if prompt_type == 'hook_analysis':
            result = runner.run_hook_analysis(prompt_data)
        elif prompt_type == 'cta_alignment':
            result = runner.run_cta_alignment(prompt_data)
        elif prompt_type == 'creative_density':
            result = runner.run_creative_density(prompt_data)
        elif prompt_type == 'emotional_journey':
            result = runner.run_emotional_journey(prompt_data)
        elif prompt_type == 'viral_mechanics':
            result = runner.run_viral_mechanics(prompt_data)
        elif prompt_type == 'trend_alignment':
            result = runner.run_trend_alignment(prompt_data)
        elif prompt_type == 'complete_analysis':
            result = runner.run_complete_analysis(prompt_data)
        else:
            print(f"Unknown prompt type: {prompt_type}")
            return False
        
        # Save result
        output_file = f"validated_result_{video_id}_{prompt_type}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Analysis complete. Result saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error running Claude prompt: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run Claude prompts with ML data validation')
    parser.add_argument('video_id', help='Video ID to analyze')
    parser.add_argument('--prompt-type', '-p', 
                       choices=['hook_analysis', 'cta_alignment', 'creative_density', 
                               'emotional_journey', 'viral_mechanics', 'trend_alignment', 'complete_analysis'],
                       default='complete_analysis',
                       help='Type of prompt to run (default: complete_analysis)')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate data without running Claude prompts')
    parser.add_argument('--list-available', action='store_true',
                       help='List available unified analysis files')
    
    args = parser.parse_args()
    
    if args.list_available:
        print("Available unified analysis files:")
        for file in os.listdir('.'):
            if file.startswith('unified_analysis_') and file.endswith('.json'):
                video_id = file.replace('unified_analysis_', '').replace('.json', '')
                print(f"  {video_id}")
        return
    
    print(f"Running validated prompt analysis for video: {args.video_id}")
    print(f"Prompt type: {args.prompt_type}")
    print(f"Validation only: {args.validate_only}")
    print("-" * 50)
    
    success = run_validated_prompt(args.video_id, args.prompt_type, args.validate_only)
    
    if success:
        print("\n✅ Analysis completed successfully")
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main()