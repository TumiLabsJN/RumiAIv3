#!/usr/bin/env python3
"""
Create FPS registry for videos during analysis pipeline
"""

import json
import sys
from pathlib import Path
from fps_utils import FPSContextManager


def create_registry_from_unified_analysis(video_id):
    """Create FPS registry from existing unified analysis"""
    
    unified_path = Path(f"unified_analysis/{video_id}.json")
    if not unified_path.exists():
        print(f"❌ No unified analysis found for {video_id}")
        return False
    
    with open(unified_path, 'r') as f:
        unified_data = json.load(f)
    
    # Extract metadata
    metadata = unified_data.get('metadata', {})
    video_metadata = {
        'fps': metadata.get('fps', 30.0),
        'duration': unified_data.get('duration_seconds', 0),
        'total_frames': metadata.get('total_frames', 0)
    }
    
    # Default analysis config (can be customized)
    analysis_config = {
        'extraction_fps': unified_data.get('fps', 1.0),  # From unified data fps field
        'ocr_sampling': 15,  # Every 15th frame
        'scene_detection_fps': metadata.get('fps', 30.0)  # Original video FPS
    }
    
    # Create registry
    manager = FPSContextManager(video_id)
    registry = manager.create_registry_for_video(video_metadata, analysis_config)
    
    print(f"✅ Created FPS registry for {video_id}")
    print(f"   Original FPS: {video_metadata['fps']}")
    print(f"   Duration: {video_metadata['duration']:.1f}s")
    print(f"   Analysis FPS: {analysis_config['extraction_fps']}")
    
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 create_fps_registry.py <video_id>")
        print("Example: python3 create_fps_registry.py 7367449043070356782")
        sys.exit(1)
    
    video_id = sys.argv[1]
    success = create_registry_from_unified_analysis(video_id)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()