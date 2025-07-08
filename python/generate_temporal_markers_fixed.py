#!/usr/bin/env python3
"""
Fixed Temporal Marker Generator
Generates temporal markers from the actual data structures used by RumiAI
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
    
    # Process YOLO objectAnnotations (structured differently than expected)
    if yolo_data and 'objectAnnotations' in yolo_data:
        seen_objects = set()
        for track in yolo_data['objectAnnotations']:
            entity = track.get('entity', {}).get('entityId', 'unknown')
            # Check frames in first 5 seconds
            for frame_info in track.get('frames', []):
                timestamp = frame_info.get('timestamp', 0)
                if timestamp < 5:
                    second_idx = int(timestamp)
                    if second_idx < 5:
                        markers['density_progression'][second_idx] += 1
                        if entity not in seen_objects:
                            seen_objects.add(entity)
                            markers['object_appearances'].append({
                                'time': round(timestamp, 1),
                                'objects': [entity]
                            })
    
    # Process OCR frame_details
    if ocr_data and 'frame_details' in ocr_data:
        seen_texts = set()
        for frame_detail in ocr_data['frame_details']:
            # Extract frame number from filename like "frame_0000_t0.00.jpg"
            frame_name = frame_detail.get('frame', '')
            try:
                # Extract time from frame name
                if '_t' in frame_name:
                    time_str = frame_name.split('_t')[1].split('.jpg')[0]
                    timestamp = float(time_str)
                    
                    if timestamp < 5:
                        second_idx = int(timestamp)
                        text_elements = frame_detail.get('text_elements', [])
                        
                        for text_elem in text_elements:
                            text = text_elem.get('text', '')
                            if text and second_idx < 5:
                                markers['density_progression'][second_idx] += 1
                                if text not in seen_texts and len(markers['text_moments']) < 5:
                                    seen_texts.add(text)
                                    markers['text_moments'].append({
                                        'time': round(timestamp, 1),
                                        'text': text[:50],  # Limit text length
                                        'size': 'M',
                                        'position': 'center'
                                    })
            except:
                continue
    
    # Process MediaPipe frame_details
    if mediapipe_data and 'frame_details' in mediapipe_data:
        for frame_detail in mediapipe_data['frame_details']:
            frame_name = frame_detail.get('frame', '')
            try:
                if '_t' in frame_name:
                    time_str = frame_name.split('_t')[1].split('.jpg')[0]
                    timestamp = float(time_str)
                    
                    if timestamp < 5:
                        second_idx = int(timestamp)
                        gestures = frame_detail.get('gestures', [])
                        
                        if gestures and second_idx < 5:
                            markers['density_progression'][second_idx] += 1
                            if len(markers['gesture_moments']) < 3:
                                markers['gesture_moments'].append({
                                    'time': round(timestamp, 1),
                                    'gesture': gestures[0]
                                })
            except:
                continue
    
    # Sort and limit results
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
    cta_keywords = ['follow', 'like', 'subscribe', 'comment', 'share', 'click', 'tap', 'link', 'bio', 'more', 'save', 'check']
    
    # Process OCR frame_details for CTAs
    if ocr_data and 'frame_details' in ocr_data:
        for frame_detail in ocr_data['frame_details']:
            frame_name = frame_detail.get('frame', '')
            try:
                if '_t' in frame_name:
                    time_str = frame_name.split('_t')[1].split('.jpg')[0]
                    timestamp = float(time_str)
                    
                    if timestamp >= cta_start_time:
                        text_elements = frame_detail.get('text_elements', [])
                        
                        for text_elem in text_elements:
                            text = text_elem.get('text', '')
                            text_lower = text.lower()
                            
                            if any(keyword in text_lower for keyword in cta_keywords):
                                if len(markers['cta_appearances']) < 5:
                                    markers['cta_appearances'].append({
                                        'time': round(timestamp, 1),
                                        'text': text[:50],
                                        'type': 'overlay'
                                    })
            except:
                continue
    
    # Process gestures in CTA window
    if mediapipe_data and 'frame_details' in mediapipe_data:
        for frame_detail in mediapipe_data['frame_details']:
            frame_name = frame_detail.get('frame', '')
            try:
                if '_t' in frame_name:
                    time_str = frame_name.split('_t')[1].split('.jpg')[0]
                    timestamp = float(time_str)
                    
                    if timestamp >= cta_start_time:
                        gestures = frame_detail.get('gestures', [])
                        
                        if gestures and len(markers['gesture_sync']) < 3:
                            markers['gesture_sync'].append({
                                'time': round(timestamp, 1),
                                'gesture': gestures[0]
                            })
            except:
                continue
    
    # Process objects in CTA window
    if yolo_data and 'objectAnnotations' in yolo_data:
        seen_in_cta = set()
        for track in yolo_data['objectAnnotations']:
            entity = track.get('entity', {}).get('entityId', 'unknown')
            
            for frame_info in track.get('frames', []):
                timestamp = frame_info.get('timestamp', 0)
                if timestamp >= cta_start_time and entity not in seen_in_cta:
                    seen_in_cta.add(entity)
                    if len(markers['object_focus']) < 3:
                        markers['object_focus'].append({
                            'time': round(timestamp, 1),
                            'object': entity
                        })
    
    # Sort results
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
                print(f"Progress: Loaded YOLO data with {len(yolo_data.get('objectAnnotations', []))} tracks", file=sys.stderr)
        
        if dependencies.get('ocr') and Path(dependencies['ocr']).exists():
            with open(dependencies['ocr'], 'r') as f:
                ocr_data = json.load(f)
                print(f"Progress: Loaded OCR data with {len(ocr_data.get('frame_details', []))} frames", file=sys.stderr)
        
        if dependencies.get('mediapipe') and Path(dependencies['mediapipe']).exists():
            with open(dependencies['mediapipe'], 'r') as f:
                mediapipe_data = json.load(f)
                print(f"Progress: Loaded MediaPipe data", file=sys.stderr)
        
        # Get video duration
        duration = 60.0  # Default
        if yolo_data:
            duration = yolo_data.get('total_frames', 1800) / yolo_data.get('fps', 30)
        elif ocr_data and 'insights' in ocr_data:
            duration = ocr_data['insights'].get('video_duration', 60.0)
        
        print(f"Progress: Video duration: {duration}s", file=sys.stderr)
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
        
        # Log summary to stderr
        first_5 = temporal_markers['first_5_seconds']
        cta = temporal_markers['cta_window']
        print(f"Progress: Generated markers - Text: {len(first_5['text_moments'])}, Objects: {len(first_5['object_appearances'])}, CTAs: {len(cta['cta_appearances'])}", file=sys.stderr)
        print(f"Progress: Generation complete", file=sys.stderr)
        
        # Output JSON to stdout
        print(json.dumps(temporal_markers))
        
    except Exception as e:
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
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