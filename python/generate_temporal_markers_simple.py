#!/usr/bin/env python3
"""
Simplified Temporal Marker Generator
Generates temporal markers by calling the existing temporal_marker_integration module
"""

import os
import sys
import json
import argparse

# Add parent directory to path to import from current directory structure
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description='Generate temporal markers for video')
    parser.add_argument('--video-path', required=True, help='Path to video file')
    parser.add_argument('--video-id', required=True, help='Video ID')
    parser.add_argument('--run-id', default='default', help='Run ID for tracking')
    parser.add_argument('--deps', required=True, help='JSON string of dependency paths')
    parser.add_argument('--compact-mode', default='false', help='Enable compact mode')
    
    args = parser.parse_args()
    
    try:
        # Import the existing temporal marker integration
        from python.temporal_marker_integration import TemporalMarkerPipeline
        
        # Progress to stderr
        print(f"Progress: Initializing temporal marker generation", file=sys.stderr)
        
        # Create pipeline
        pipeline = TemporalMarkerPipeline(args.video_id)
        
        # Generate markers
        print(f"Progress: Generating temporal markers", file=sys.stderr)
        markers = pipeline.extract_all_markers()
        
        # Apply compact mode if needed
        if args.compact_mode.lower() == 'true' and markers:
            print(f"Progress: Applying compact mode", file=sys.stderr)
            # Simple compacting - just keep essential fields
            compacted = {
                'first_5_seconds': markers.get('first_5_seconds', {}),
                'cta_window': markers.get('cta_window', {}),
                'metadata': markers.get('metadata', {})
            }
            markers = compacted
        
        print(f"Progress: Generation complete", file=sys.stderr)
        
        # Output JSON to stdout
        print(json.dumps(markers))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        # Output empty markers on error
        print(json.dumps({
            'first_5_seconds': {},
            'cta_window': {},
            'metadata': {'error': str(e)}
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()