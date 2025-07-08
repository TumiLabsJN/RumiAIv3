#!/usr/bin/env python3
"""
Working Temporal Marker Generator
Generates temporal markers directly from analysis outputs without missing dependencies
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

def extract_first_5_seconds_markers(yolo_data: Dict, ocr_data: Dict, mediapipe_data: Dict, duration: float) -> Dict[str, Any]:
    """Extract markers for first 5 seconds of video"""
    markers = {
        'density_progression': [0, 0, 0, 0, 0],  # Events per second for first 5 seconds
        'text_moments': [],
        'emotion_sequence': ['neutral'] * 5,
        'gesture_moments': [],
        'object_appearances': []
    }
    
    # Process text overlays from OCR
    if ocr_data and 'timeline' in ocr_data:
        for timestamp, data in ocr_data['timeline'].items():
            # Parse timestamp like "0-1s" to get start time
            try:
                start_time = int(timestamp.split('-')[0])
                if start_time < 5:
                    for text_item in data.get('text_overlays', []):
                        markers['text_moments'].append({
                            'time': start_time,
                            'text': text_item.get('text', ''),
                            'size': 'M',
                            'position': 'center'
                        })
                    # Update density
                    if start_time < 5:
                        markers['density_progression'][start_time] += len(data.get('text_overlays', []))
            except:
                continue
    
    # Process objects from YOLO
    if yolo_data and 'detections_by_frame' in yolo_data:
        seen_objects = set()
        for frame_data in yolo_data['detections_by_frame']:
            frame_num = frame_data.get('frame_number', 0)
            # Assuming 30fps, convert to seconds
            time_seconds = frame_num / 30.0
            if time_seconds < 5:
                second_idx = int(time_seconds)
                objects = [d['class'] for d in frame_data.get('detections', [])]
                if second_idx < 5:
                    markers['density_progression'][second_idx] += len(objects)
                    for obj in objects:
                        if obj not in seen_objects:
                            seen_objects.add(obj)
                            markers['object_appearances'].append({
                                'time': round(time_seconds, 1),
                                'objects': [obj]
                            })
    
    # Process gestures from MediaPipe
    if mediapipe_data and 'timeline' in mediapipe_data:
        for timestamp, data in mediapipe_data['timeline'].items():
            try:
                start_time = int(timestamp.split('-')[0])
                if start_time < 5:
                    gestures = data.get('gestures', [])
                    if gestures:
                        markers['gesture_moments'].append({
                            'time': start_time,
                            'gesture': gestures[0] if gestures else 'unknown'
                        })
                        markers['density_progression'][start_time] += 1
            except:
                continue
    
    # Sort moments by time
    markers['text_moments'] = sorted(markers['text_moments'], key=lambda x: x['time'])[:5]
    markers['gesture_moments'] = sorted(markers['gesture_moments'], key=lambda x: x['time'])[:3]
    markers['object_appearances'] = sorted(markers['object_appearances'], key=lambda x: x['time'])[:5]
    
    return markers

def extract_cta_window_markers(yolo_data: Dict, ocr_data: Dict, mediapipe_data: Dict, duration: float) -> Dict[str, Any]:
    """Extract markers for CTA window (last 15% of video)"""
    cta_start_time = duration * 0.85
    
    markers = {
        'time_range': f'last {int(15)}%',
        'cta_appearances': [],
        'gesture_sync': [],
        'object_focus': []
    }
    
    # CTA keywords to look for
    cta_keywords = ['follow', 'like', 'subscribe', 'comment', 'share', 'click', 'tap', 'link', 'bio', 'more']
    
    # Process text for CTAs
    if ocr_data and 'timeline' in ocr_data:
        for timestamp, data in ocr_data['timeline'].items():
            try:
                start_time = int(timestamp.split('-')[0])
                if start_time >= cta_start_time:
                    for text_item in data.get('text_overlays', []):
                        text_lower = text_item.get('text', '').lower()
                        if any(keyword in text_lower for keyword in cta_keywords):
                            markers['cta_appearances'].append({
                                'time': start_time,
                                'text': text_item.get('text', ''),
                                'type': 'overlay'
                            })
            except:
                continue
    
    # Process gestures in CTA window
    if mediapipe_data and 'timeline' in mediapipe_data:
        for timestamp, data in mediapipe_data['timeline'].items():
            try:
                start_time = int(timestamp.split('-')[0])
                if start_time >= cta_start_time:
                    gestures = data.get('gestures', [])
                    if gestures:
                        markers['gesture_sync'].append({
                            'time': start_time,
                            'gesture': gestures[0]
                        })
            except:
                continue
    
    # Limit results
    markers['cta_appearances'] = sorted(markers['cta_appearances'], key=lambda x: x['time'])[:5]
    markers['gesture_sync'] = sorted(markers['gesture_sync'], key=lambda x: x['time'])[:3]
    
    return markers

def main():
    parser = argparse.ArgumentParser(description='Generate temporal markers for video')
    parser.add_argument('--video-path', required=True, help='Path to video file')
    parser.add_argument('--video-id', required=True, help='Video ID')
    parser.add_argument('--run-id', default='default', help='Run ID for tracking')
    parser.add_argument('--deps', required=True, help='JSON string of dependency paths')
    parser.add_argument('--compact-mode', default='false', help='Enable compact mode')
    
    args = parser.parse_args()
    
    try:
        # Parse dependencies
        dependencies = json.loads(args.deps)
        
        # Progress to stderr
        print(f"Progress: Loading analysis dependencies", file=sys.stderr)
        
        # Load dependency data
        yolo_data = None
        ocr_data = None
        mediapipe_data = None
        
        if dependencies.get('yolo') and Path(dependencies['yolo']).exists():
            with open(dependencies['yolo'], 'r') as f:
                yolo_data = json.load(f)
        
        if dependencies.get('ocr') and Path(dependencies['ocr']).exists():
            with open(dependencies['ocr'], 'r') as f:
                ocr_data = json.load(f)
        
        if dependencies.get('mediapipe') and Path(dependencies['mediapipe']).exists():
            with open(dependencies['mediapipe'], 'r') as f:
                mediapipe_data = json.load(f)
        
        # Get video duration (default to 60s if not available)
        duration = 60.0
        if yolo_data and 'metadata' in yolo_data:
            duration = yolo_data['metadata'].get('duration', 60.0)
        
        print(f"Progress: Generating temporal markers", file=sys.stderr)
        
        # Generate markers
        temporal_markers = {
            'first_5_seconds': extract_first_5_seconds_markers(yolo_data, ocr_data, mediapipe_data, duration),
            'cta_window': extract_cta_window_markers(yolo_data, ocr_data, mediapipe_data, duration),
            'metadata': {
                'video_id': args.video_id,
                'run_id': args.run_id,
                'video_duration': duration,
                'markers_version': '1.0'
            }
        }
        
        print(f"Progress: Generation complete", file=sys.stderr)
        
        # Output JSON to stdout
        print(json.dumps(temporal_markers))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        # Output minimal markers on error
        print(json.dumps({
            'first_5_seconds': {
                'density_progression': [0, 0, 0, 0, 0],
                'text_moments': [],
                'emotion_sequence': ['neutral'] * 5,
                'gesture_moments': [],
                'object_appearances': []
            },
            'cta_window': {
                'time_range': 'last 15%',
                'cta_appearances': [],
                'gesture_sync': [],
                'object_focus': []
            },
            'metadata': {
                'video_id': args.video_id,
                'error': str(e)
            }
        }))

if __name__ == "__main__":
    main()