#!/usr/bin/env python3
"""
FPS Context Management for RumiAI Video Analysis Pipeline

This module provides utilities for managing different FPS contexts throughout
the video analysis pipeline, solving the timestamp interpretation issues.
"""

import json
import os
from pathlib import Path


class FPSContextManager:
    """Manages FPS context for video analysis timestamps"""
    
    def __init__(self, video_id):
        self.video_id = video_id
        self.registry = self._load_registry(video_id)
        self._cache = {}  # Cache for converted timestamps
    
    def _load_registry(self, video_id):
        """Load FPS registry for a video"""
        registry_path = Path(__file__).parent / 'fps_registry' / f'{video_id}.json'
        
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                return json.load(f)
        else:
            # Return default registry if not found
            print(f"⚠️ No FPS registry found for {video_id}, using defaults")
            return self._create_default_registry()
    
    def _create_default_registry(self):
        """Create default registry with common assumptions"""
        return {
            "video_id": self.video_id,
            "video_specs": {
                "original_fps": 30.0,  # Common default
                "duration": 60.0,
                "total_frames": 1800
            },
            "analysis_contexts": {
                "scene_detection": {
                    "fps": 30.0,
                    "timestamp_format": "frame-frame+1s",
                    "uses_original_fps": True
                },
                "frame_extraction": {
                    "fps": 1.0,
                    "sampling_rate": 30,
                    "timestamp_format": "frame-frame+1s"
                },
                "ocr_analysis": {
                    "effective_fps": 0.067,
                    "parent_fps": 1.0,
                    "sampling_rate": 15
                },
                "yolo_tracking": {
                    "fps": 1.0,
                    "timestamp_format": "frame-frame+1s"
                }
            }
        }
    
    def timestamp_to_seconds(self, timestamp, context='scene_detection'):
        """
        Convert any timestamp to actual seconds based on context
        
        Args:
            timestamp: String like "543-544s" or "18.5s"
            context: Which analysis context (scene_detection, yolo_tracking, etc.)
            
        Returns:
            float: Time in seconds
        """
        # Check cache first
        cache_key = f"{timestamp}_{context}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Handle frame-based timestamps like "543-544s"
            if '-' in timestamp and timestamp.endswith('s'):
                frame_start = int(timestamp.split('-')[0])
                
                # Get the appropriate FPS for this context
                context_info = self.registry['analysis_contexts'].get(context, {})
                
                if context_info.get('uses_original_fps', False):
                    fps = self.registry['video_specs']['original_fps']
                else:
                    fps = context_info.get('fps', 1.0)
                
                seconds = frame_start / fps
                
            # Handle simple second timestamps like "18.5s"
            elif timestamp.endswith('s'):
                seconds = float(timestamp[:-1])
                
            else:
                # Assume it's already in seconds
                seconds = float(timestamp)
            
            self._cache[cache_key] = seconds
            return seconds
            
        except (ValueError, KeyError) as e:
            print(f"⚠️ Error converting timestamp {timestamp}: {e}")
            return 0.0
    
    def get_display_timestamp(self, scene_data, shot_duration, context='scene_detection'):
        """
        Generate correct display timestamp for scene pacing
        
        Args:
            scene_data: Dictionary with scene information
            shot_duration: Duration in context-specific units (frames or seconds)
            context: Which analysis context
            
        Returns:
            str: Display timestamp like "18-20s"
        """
        # Best case: use actual time data if available
        if isinstance(scene_data, dict):
            if 'startTime' in scene_data and 'endTime' in scene_data:
                start = scene_data['startTime']
                end = scene_data['endTime']
                return f"{int(start)}-{int(end)}s"
            
            # Try to get frame data and convert
            if 'frame' in scene_data:
                frame = scene_data['frame']
                context_info = self.registry['analysis_contexts'].get(context, {})
                
                if context_info.get('uses_original_fps', False):
                    fps = self.registry['video_specs']['original_fps']
                else:
                    fps = context_info.get('fps', 1.0)
                
                start_seconds = frame / fps
                
                # Determine if shot_duration is in frames or seconds
                if shot_duration > self.registry['video_specs']['duration']:
                    # Likely in frames
                    duration_seconds = shot_duration / fps
                else:
                    # Already in seconds
                    duration_seconds = shot_duration
                
                end_seconds = start_seconds + duration_seconds
                
                # Sanity check
                video_duration = self.registry['video_specs']['duration']
                if end_seconds > video_duration:
                    end_seconds = video_duration
                
                return f"{int(start_seconds)}-{int(end_seconds)}s"
        
        # Fallback
        return "unknown"
    
    def create_registry_for_video(self, video_metadata, analysis_config):
        """
        Create and save FPS registry for a video
        
        Args:
            video_metadata: Dict with video specs (fps, duration, etc.)
            analysis_config: Dict with analysis pipeline configuration
        """
        registry = {
            "video_id": self.video_id,
            "video_specs": {
                "original_fps": video_metadata.get('fps', 30.0),
                "duration": video_metadata.get('duration', 0),
                "total_frames": video_metadata.get('total_frames', 0)
            },
            "analysis_contexts": {
                "scene_detection": {
                    "fps": video_metadata.get('fps', 30.0),
                    "timestamp_format": "frame-frame+1s",
                    "uses_original_fps": True,
                    "description": "PySceneDetect runs on original video"
                },
                "frame_extraction": {
                    "fps": analysis_config.get('extraction_fps', 1.0),
                    "sampling_rate": int(video_metadata.get('fps', 30) / analysis_config.get('extraction_fps', 1.0)),
                    "timestamp_format": "frame-frame+1s",
                    "description": "Frames extracted for ML analysis"
                },
                "ocr_analysis": {
                    "effective_fps": analysis_config.get('extraction_fps', 1.0) / analysis_config.get('ocr_sampling', 15),
                    "parent_fps": analysis_config.get('extraction_fps', 1.0),
                    "sampling_rate": analysis_config.get('ocr_sampling', 15),
                    "description": "OCR runs on subset of extracted frames"
                },
                "yolo_tracking": {
                    "fps": analysis_config.get('extraction_fps', 1.0),
                    "timestamp_format": "frame-frame+1s",
                    "description": "YOLO runs on extracted frames"
                },
                "mediapipe": {
                    "fps": analysis_config.get('extraction_fps', 1.0),
                    "timestamp_format": "frame-frame+1s",
                    "description": "MediaPipe runs on extracted frames"
                }
            },
            "created_at": os.environ.get('TZ', 'UTC'),
            "version": "1.0"
        }
        
        # Save registry
        registry_dir = Path(__file__).parent / 'fps_registry'
        registry_dir.mkdir(exist_ok=True)
        
        registry_path = registry_dir / f'{self.video_id}.json'
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"✅ Created FPS registry for {self.video_id}")
        self.registry = registry
        
        return registry


# Convenience functions
def get_fps_for_context(video_id, context='scene_detection'):
    """Quick helper to get FPS for a specific context"""
    manager = FPSContextManager(video_id)
    context_info = manager.registry['analysis_contexts'].get(context, {})
    
    if context_info.get('uses_original_fps', False):
        return manager.registry['video_specs']['original_fps']
    
    return context_info.get('fps', 1.0)


def convert_timestamp_to_seconds(video_id, timestamp, context='scene_detection'):
    """Quick helper to convert a single timestamp"""
    manager = FPSContextManager(video_id)
    return manager.timestamp_to_seconds(timestamp, context)