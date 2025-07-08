#!/usr/bin/env python3
"""
Temporal Marker Generator for RumiAI
Generates temporal markers from video analysis outputs
Called by Node.js TemporalMarkerService
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import all the extractors and utilities
from temporal_marker_extractors import (
    OCRTemporalExtractor,
    YOLOTemporalExtractor,
    MediaPipeTemporalExtractor,
    TemporalMarkerIntegrator
)
from timestamp_normalizer import TimestampNormalizer, create_from_video_path
from temporal_marker_safety import TemporalMarkerSafety

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TemporalMarkerGenerator:
    """Main generator class called by Node.js service"""
    
    def __init__(self, video_path: str, video_id: str, run_id: str = None):
        self.video_path = Path(video_path)
        self.video_id = video_id
        self.run_id = run_id or 'default'
        self.base_dir = Path('.')
        
    def generate(self, dependencies: Dict[str, str], compact_mode: bool = False) -> Dict[str, Any]:
        """
        Generate temporal markers from analysis outputs
        
        Args:
            dependencies: Paths to dependency files (yolo, mediapipe, ocr, etc.)
            compact_mode: Whether to generate compact output
            
        Returns:
            Temporal markers dictionary
        """
        logger.info(f"Starting temporal marker generation for {self.video_id} (run: {self.run_id})")
        start_time = time.time()
        
        # Progress update for Node.js (to stderr so it doesn't interfere with JSON output)
        print(f"Progress: Initializing temporal marker generation", file=sys.stderr)
        
        # 1. Get video metadata
        video_metadata = self._get_video_metadata()
        if not video_metadata:
            raise ValueError("Could not extract video metadata")
        
        print(f"Progress: Video metadata extracted - {video_metadata['duration']}s, {video_metadata['fps']}fps", file=sys.stderr)
        
        # 2. Load dependency data
        print(f"Progress: Loading analysis dependencies", file=sys.stderr)
        dep_data = self._load_dependencies(dependencies)
        
        # 3. Extract markers from each analyzer
        print(f"Progress: Extracting OCR temporal markers", file=sys.stderr)
        ocr_markers = self._extract_ocr_markers(dep_data.get('ocr'))
        
        print(f"Progress: Extracting YOLO temporal markers", file=sys.stderr)
        yolo_markers = self._extract_yolo_markers(dep_data.get('yolo'))
        
        print(f"Progress: Extracting MediaPipe temporal markers", file=sys.stderr)
        mediapipe_markers = self._extract_mediapipe_markers(dep_data.get('mediapipe'))
        
        # 4. Integrate all markers
        print(f"Progress: Integrating temporal markers", file=sys.stderr)
        integrator = TemporalMarkerIntegrator(video_metadata)
        integrated_markers = integrator.integrate_markers(
            ocr_markers=ocr_markers,
            yolo_markers=yolo_markers,
            mediapipe_markers=mediapipe_markers
        )
        
        # 5. Add metadata
        integrated_markers['metadata'] = {
            'video_id': self.video_id,
            'run_id': self.run_id,
            'video_duration': video_metadata['duration'],
            'extraction_fps': video_metadata.get('extraction_fps', 2.0),
            'markers_version': '1.0',
            'generated_at': time.time(),
            'generation_time': time.time() - start_time
        }
        
        # 6. Apply compact mode if requested
        if compact_mode:
            print(f"Progress: Applying compact mode", file=sys.stderr)
            integrated_markers = self._apply_compact_mode(integrated_markers)
        
        # 7. Final validation
        print(f"Progress: Validating temporal markers", file=sys.stderr)
        errors = TemporalMarkerSafety.validate_markers(integrated_markers)
        if errors:
            logger.warning(f"Validation warnings: {errors}")
        
        print(f"Progress: Generation complete - {time.time() - start_time:.2f}s", file=sys.stderr)
        
        return integrated_markers
    
    def _get_video_metadata(self) -> Dict[str, Any]:
        """Extract video metadata using frame_sampler.py or ffprobe"""
        try:
            # Try using existing frame_sampler.py
            import subprocess
            python_path = Path(__file__).parent / '../venv/bin/python'
            if not python_path.exists():
                python_path = 'python3'
            
            script_path = Path(__file__).parent / 'frame_sampler.py'
            if script_path.exists():
                result = subprocess.run(
                    [str(python_path), str(script_path), str(self.video_path), 'metadata'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Parse metadata from output
                    for line in result.stdout.split('\n'):
                        if 'Video metadata:' in line:
                            metadata_str = line.replace('Video metadata: ', '')
                            metadata = eval(metadata_str)  # Safe since we control the output
                            return {
                                'fps': metadata['fps'],
                                'duration': metadata['duration'],
                                'frame_count': metadata['frame_count'],
                                'width': metadata['width'],
                                'height': metadata['height'],
                                'extraction_fps': 2.0  # Default extraction FPS
                            }
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
        
        # Fallback to defaults
        return {
            'fps': 30.0,
            'duration': 60.0,
            'frame_count': 1800,
            'width': 1080,
            'height': 1920,
            'extraction_fps': 2.0
        }
    
    def _load_dependencies(self, dep_paths: Dict[str, str]) -> Dict[str, Any]:
        """Load analysis data from dependency files"""
        dep_data = {}
        
        for dep_name, dep_path in dep_paths.items():
            if dep_path and Path(dep_path).exists():
                try:
                    with open(dep_path, 'r') as f:
                        dep_data[dep_name] = json.load(f)
                    logger.info(f"Loaded {dep_name} data from {dep_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {dep_name}: {e}")
        
        return dep_data
    
    def _extract_ocr_markers(self, ocr_data: Optional[Dict]) -> Optional[Dict]:
        """Extract temporal markers from OCR data"""
        if not ocr_data:
            return None
        
        try:
            extractor = OCRTemporalExtractor(self.video_id)
            # OCR data is already loaded, just process it
            return extractor._process_ocr_data(ocr_data)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return None
    
    def _extract_yolo_markers(self, yolo_data: Optional[Dict]) -> Optional[Dict]:
        """Extract temporal markers from YOLO data"""
        if not yolo_data:
            return None
        
        try:
            extractor = YOLOTemporalExtractor(self.video_id)
            # YOLO data is already loaded, just process it
            return extractor._process_yolo_data(yolo_data)
        except Exception as e:
            logger.error(f"YOLO extraction failed: {e}")
            return None
    
    def _extract_mediapipe_markers(self, mediapipe_data: Optional[Dict]) -> Optional[Dict]:
        """Extract temporal markers from MediaPipe data"""
        if not mediapipe_data:
            return None
        
        try:
            extractor = MediaPipeTemporalExtractor(self.video_id)
            # MediaPipe data is already loaded, just process it
            return extractor._process_mediapipe_data(mediapipe_data)
        except Exception as e:
            logger.error(f"MediaPipe extraction failed: {e}")
            return None
    
    def _apply_compact_mode(self, markers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply compact mode to reduce output size"""
        compacted = {
            'metadata': markers['metadata'],
            'first_5_seconds': markers.get('first_5_seconds', {}),
            'cta_window': markers.get('cta_window', {})
        }
        
        # Limit arrays in first_5_seconds
        if 'first_5_seconds' in compacted:
            first5 = compacted['first_5_seconds']
            if 'text_moments' in first5:
                first5['text_moments'] = first5['text_moments'][:5]
            if 'gesture_moments' in first5:
                first5['gesture_moments'] = first5['gesture_moments'][:3]
            if 'object_appearances' in first5:
                first5['object_appearances'] = first5['object_appearances'][:5]
        
        # Limit arrays in cta_window
        if 'cta_window' in compacted:
            cta = compacted['cta_window']
            if 'cta_appearances' in cta:
                cta['cta_appearances'] = cta['cta_appearances'][:5]
            if 'gesture_sync' in cta:
                cta['gesture_sync'] = cta['gesture_sync'][:3]
        
        return compacted


def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(description='Generate temporal markers for video')
    parser.add_argument('--video-path', required=True, help='Path to video file')
    parser.add_argument('--video-id', required=True, help='Video ID')
    parser.add_argument('--run-id', default='default', help='Run ID for tracking')
    parser.add_argument('--deps', required=True, help='JSON string of dependency paths')
    parser.add_argument('--compact-mode', default='false', help='Enable compact mode')
    parser.add_argument('--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Parse dependencies
    try:
        dependencies = json.loads(args.deps)
    except json.JSONDecodeError:
        logger.error("Invalid JSON for dependencies")
        sys.exit(1)
    
    # Create generator
    generator = TemporalMarkerGenerator(
        video_path=args.video_path,
        video_id=args.video_id,
        run_id=args.run_id
    )
    
    try:
        # Generate markers
        compact_mode = args.compact_mode.lower() == 'true'
        markers = generator.generate(dependencies, compact_mode)
        
        # Output as JSON to stdout for Node.js to capture
        print(json.dumps(markers))
        
        # Optionally save to file
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(markers, f, indent=2)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()