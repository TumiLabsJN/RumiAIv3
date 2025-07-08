"""
Temporal Marker Extractors for RumiAI
Modules to extract enhanced temporal markers from analyzer outputs
Each extractor focuses on specific patterns in first 5 seconds and CTA window
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.timestamp_normalizer import TimestampNormalizer
from python.temporal_marker_safety import TemporalMarkerSafety

logger = logging.getLogger(__name__)


class OCRTemporalExtractor:
    """
    Extracts temporal markers from OCR/text detection results.
    Focuses on text timing, size, and content patterns.
    """
    
    def __init__(self, video_metadata: Dict[str, Any]):
        """
        Initialize with video metadata for timestamp normalization.
        
        Args:
            video_metadata: Dict with fps, extraction_fps, duration, etc.
        """
        self.normalizer = TimestampNormalizer(video_metadata)
        self.video_duration = video_metadata.get('duration', 60.0)
        
    def extract_temporal_markers(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract temporal markers from OCR frame analysis results.
        
        Args:
            frame_results: List of frame analysis results from detect_tiktok_creative_elements
            
        Returns:
            Dictionary with first_5_seconds and cta_window markers
        """
        # Initialize marker structure
        markers = {
            'first_5_seconds': {
                'text_moments': [],
                'density_progression': [0, 0, 0, 0, 0],  # Per-second density
            },
            'cta_window': {
                'time_range': self._get_cta_time_range(),
                'cta_appearances': []
            }
        }
        
        # Process each frame
        for frame_result in frame_results:
            # Normalize timestamp
            frame_file = frame_result.get('frame', '')
            timestamp = self.normalizer.normalize_to_seconds(frame_file, 'frame_filename')
            
            if timestamp is None:
                continue
                
            # Extract text elements
            text_elements = frame_result.get('text_elements', [])
            
            # Process text elements for first 5 seconds
            if timestamp < 5.0:
                for text_elem in text_elements:
                    text_moment = self._process_text_element(text_elem, timestamp)
                    if text_moment:
                        markers['first_5_seconds']['text_moments'].append(text_moment)
                        
                        # Update density for the second this text appears in
                        second_idx = int(timestamp)
                        if second_idx < 5:
                            markers['first_5_seconds']['density_progression'][second_idx] += 1
            
            # Process CTA window
            cta_start, cta_end = self._get_cta_bounds()
            if cta_start <= timestamp <= cta_end:
                for text_elem in text_elements:
                    if text_elem.get('category') == 'call_to_action':
                        cta_moment = self._process_cta_element(text_elem, timestamp)
                        if cta_moment:
                            markers['cta_window']['cta_appearances'].append(cta_moment)
        
        # Apply safety limits and standardization
        markers = self._apply_safety_measures(markers)
        
        return markers
    
    def _process_text_element(self, text_elem: Dict[str, Any], timestamp: float) -> Optional[Dict[str, Any]]:
        """Process a single text element into a temporal marker."""
        text = text_elem.get('text', '')
        if not text:
            return None
            
        # Truncate and clean text
        text = TemporalMarkerSafety.truncate_text(text)
        
        # Extract size from bounding box
        bbox = text_elem.get('bbox', {})
        size = TemporalMarkerSafety.classify_text_size(bbox)
        
        # Determine position
        position = self._determine_text_position(bbox)
        
        # Build marker
        marker = {
            'time': round(timestamp, 2),
            'text': text,
            'size': size,
            'position': position,
            'confidence': round(text_elem.get('confidence', 0.5), 2)
        }
        
        # Add category if it's a CTA in first 5 seconds
        if text_elem.get('category') == 'call_to_action':
            marker['is_cta'] = True
            
        return marker
    
    def _process_cta_element(self, text_elem: Dict[str, Any], timestamp: float) -> Optional[Dict[str, Any]]:
        """Process a CTA text element."""
        text = text_elem.get('text', '')
        if not text:
            return None
            
        # Truncate and clean text
        text = TemporalMarkerSafety.truncate_text(text)
        
        # Determine CTA type
        cta_type = 'text_overlay' if text_elem.get('category') == 'overlay_text' else 'caption'
        
        # Extract size
        bbox = text_elem.get('bbox', {})
        size = TemporalMarkerSafety.classify_text_size(bbox)
        
        return {
            'time': round(timestamp, 2),
            'text': text,
            'type': cta_type,
            'size': size,
            'confidence': round(text_elem.get('confidence', 0.5), 2)
        }
    
    def _determine_text_position(self, bbox: Dict[str, float]) -> str:
        """Determine text position (center, top, bottom) from bbox."""
        if not bbox or not all(k in bbox for k in ['y1', 'y2']):
            return 'center'
            
        # Assuming normalized coordinates or we'd need image height
        y_center = (bbox['y1'] + bbox['y2']) / 2
        
        # This is simplified - in real implementation we'd normalize by image height
        if y_center < 200:  # Top third
            return 'top'
        elif y_center > 600:  # Bottom third
            return 'bottom'
        else:
            return 'center'
    
    def _get_cta_time_range(self) -> str:
        """Get CTA window time range as string."""
        cta_start = max(0, self.video_duration * 0.85)
        return f"{cta_start:.1f}-{self.video_duration:.1f}s"
    
    def _get_cta_bounds(self) -> Tuple[float, float]:
        """Get CTA window bounds in seconds."""
        cta_start = max(0, self.video_duration * 0.85)
        return cta_start, self.video_duration
    
    def _apply_safety_measures(self, markers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety limits and text standardization."""
        # Sort text moments by time
        if 'text_moments' in markers['first_5_seconds']:
            markers['first_5_seconds']['text_moments'].sort(key=lambda x: x['time'])
            
            # Apply text event limit before size check
            if len(markers['first_5_seconds']['text_moments']) > TemporalMarkerSafety.MAX_TEXT_EVENTS_FIRST_5S:
                markers['first_5_seconds']['text_moments'] = \
                    markers['first_5_seconds']['text_moments'][:TemporalMarkerSafety.MAX_TEXT_EVENTS_FIRST_5S]
            
        # Sort CTA appearances by time  
        if 'cta_appearances' in markers['cta_window']:
            markers['cta_window']['cta_appearances'].sort(key=lambda x: x['time'])
            
            # Apply CTA event limit
            if len(markers['cta_window']['cta_appearances']) > TemporalMarkerSafety.MAX_CTA_EVENTS:
                markers['cta_window']['cta_appearances'] = \
                    markers['cta_window']['cta_appearances'][:TemporalMarkerSafety.MAX_CTA_EVENTS]
            
        # Apply additional size limits if needed
        markers = TemporalMarkerSafety.check_and_reduce_size(markers)
        
        return markers


class YOLOTemporalExtractor:
    """
    Extracts temporal markers from YOLO object detection results.
    Focuses on object appearances, persistence, and transitions.
    """
    
    def __init__(self, video_metadata: Dict[str, Any]):
        """Initialize with video metadata."""
        self.normalizer = TimestampNormalizer(video_metadata)
        self.video_duration = video_metadata.get('duration', 60.0)
        
    def extract_temporal_markers(self, tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract temporal markers from YOLO tracking data.
        
        Args:
            tracking_data: Object tracking results from object_tracking.py
            
        Returns:
            Dictionary with object appearance markers
        """
        markers = {
            'first_5_seconds': {
                'object_appearances': [],
                'density_progression': [0, 0, 0, 0, 0]
            },
            'cta_window': {
                'time_range': self._get_cta_time_range(),
                'object_focus': []  # Objects that appear/emphasized in CTA
            }
        }
        
        # Process tracks
        tracks = tracking_data.get('tracks', [])
        
        # Group detections by timestamp
        detections_by_time = defaultdict(list)
        
        for track in tracks:
            for detection in track.get('detections', []):
                # Normalize timestamp
                frame_idx = detection.get('frame', 0)
                timestamp = self.normalizer.normalize_to_seconds(frame_idx, 'frame_index')
                
                if timestamp is None:
                    continue
                    
                obj_class = detection.get('class', 'unknown')
                confidence = detection.get('confidence', 0.5)
                
                detections_by_time[timestamp].append({
                    'object': obj_class,
                    'confidence': confidence,
                    'track_id': track.get('track_id', -1)
                })
        
        # Process first 5 seconds
        for timestamp, detections in detections_by_time.items():
            if timestamp <= 5.0:
                # Create object appearance marker
                objects = []
                confidences = []
                
                for det in detections:
                    if det['object'] not in objects:  # Avoid duplicates
                        objects.append(det['object'])
                        confidences.append(round(det['confidence'], 2))
                
                if objects:
                    markers['first_5_seconds']['object_appearances'].append({
                        'time': round(timestamp, 2),
                        'objects': objects[:5],  # Limit to 5 most confident
                        'confidence': confidences[:5]
                    })
                    
                    # Update density
                    second_idx = int(timestamp)
                    if second_idx < 5:
                        markers['first_5_seconds']['density_progression'][second_idx] += len(objects)
            
            # Process CTA window
            cta_start = self.video_duration * 0.85
            if timestamp >= cta_start:
                for det in detections:
                    if det['object'] in ['person', 'hand', 'product']:  # Focus on key objects
                        markers['cta_window']['object_focus'].append({
                            'time': round(timestamp, 2),
                            'object': det['object'],
                            'confidence': round(det['confidence'], 2)
                        })
        
        # Sort by time and apply limits
        markers['first_5_seconds']['object_appearances'].sort(key=lambda x: x['time'])
        markers['cta_window']['object_focus'].sort(key=lambda x: x['time'])
        
        # Limit object appearances
        if len(markers['first_5_seconds']['object_appearances']) > 10:
            markers['first_5_seconds']['object_appearances'] = markers['first_5_seconds']['object_appearances'][:10]
            
        if len(markers['cta_window']['object_focus']) > 5:
            markers['cta_window']['object_focus'] = markers['cta_window']['object_focus'][:5]
            
        return markers
    
    def _get_cta_time_range(self) -> str:
        """Get CTA window time range."""
        cta_start = max(0, self.video_duration * 0.85)
        return f"{cta_start:.1f}-{self.video_duration:.1f}s"


class MediaPipeTemporalExtractor:
    """
    Extracts temporal markers from MediaPipe human analysis.
    Focuses on emotions, gestures, and human presence patterns.
    """
    
    def __init__(self, video_metadata: Dict[str, Any]):
        """Initialize with video metadata."""
        self.normalizer = TimestampNormalizer(video_metadata)
        self.video_duration = video_metadata.get('duration', 60.0)
        
    def extract_temporal_markers(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract temporal markers from MediaPipe analysis.
        
        Args:
            analysis_data: Human analysis results with emotions and gestures
            
        Returns:
            Dictionary with emotion and gesture markers
        """
        markers = {
            'first_5_seconds': {
                'emotion_sequence': ['neutral'] * 5,  # One per second
                'gesture_moments': []
            },
            'cta_window': {
                'time_range': self._get_cta_time_range(),
                'gesture_sync': []  # Gestures that align with CTA
            }
        }
        
        # Process timeline data
        timeline = analysis_data.get('timeline', {})
        
        # Extract emotions for first 5 seconds
        expressions = timeline.get('expressions', [])
        for expr_data in expressions:
            # Normalize timestamp
            frame_idx = expr_data.get('frame', 0)
            timestamp = self.normalizer.normalize_to_seconds(frame_idx, 'extracted_frame_index')
            
            if timestamp is None:
                continue
                
            if timestamp <= 5.0:
                # Map to second index
                second_idx = int(timestamp)
                if second_idx < 5:
                    emotion = expr_data.get('expression', 'neutral')
                    # Standardize emotion
                    emotion = TemporalMarkerSafety.standardize_emotion(emotion)
                    markers['first_5_seconds']['emotion_sequence'][second_idx] = emotion
        
        # Extract gestures
        gestures = timeline.get('gestures', [])
        cta_start = self.video_duration * 0.85
        
        for gesture_data in gestures:
            # Normalize timestamp
            frame_idx = gesture_data.get('frame', 0)
            timestamp = self.normalizer.normalize_to_seconds(frame_idx, 'extracted_frame_index')
            
            if timestamp is None:
                continue
                
            gesture = gesture_data.get('gesture', 'unknown')
            gesture = TemporalMarkerSafety.standardize_gesture(gesture)
            
            if timestamp <= 5.0:
                # First 5 seconds gesture
                gesture_moment = {
                    'time': round(timestamp, 2),
                    'gesture': gesture,
                    'confidence': round(gesture_data.get('confidence', 0.8), 2)
                }
                
                # Add target if available
                if 'target' in gesture_data:
                    gesture_moment['target'] = gesture_data['target']
                    
                markers['first_5_seconds']['gesture_moments'].append(gesture_moment)
                
            elif timestamp >= cta_start:
                # CTA window gesture - include all standardized gestures except 'unknown'
                if gesture != 'unknown':
                    markers['cta_window']['gesture_sync'].append({
                        'time': round(timestamp, 2),
                        'gesture': gesture,
                        'aligns_with_cta': True,
                        'confidence': round(gesture_data.get('confidence', 0.8), 2)
                    })
        
        # Sort and limit gestures
        markers['first_5_seconds']['gesture_moments'].sort(key=lambda x: x['time'])
        markers['cta_window']['gesture_sync'].sort(key=lambda x: x['time'])
        
        # Apply limits
        if len(markers['first_5_seconds']['gesture_moments']) > 8:
            markers['first_5_seconds']['gesture_moments'] = markers['first_5_seconds']['gesture_moments'][:8]
            
        if len(markers['cta_window']['gesture_sync']) > 5:
            markers['cta_window']['gesture_sync'] = markers['cta_window']['gesture_sync'][:5]
            
        return markers
    
    def _get_cta_time_range(self) -> str:
        """Get CTA window time range."""
        cta_start = max(0, self.video_duration * 0.85)
        return f"{cta_start:.1f}-{self.video_duration:.1f}s"


class TemporalMarkerIntegrator:
    """
    Integrates temporal markers from all analyzers into a unified structure.
    Handles merging, deduplication, and final safety checks.
    """
    
    def __init__(self, video_metadata: Dict[str, Any]):
        """Initialize with video metadata."""
        self.video_metadata = video_metadata
        self.video_duration = video_metadata.get('duration', 60.0)
        
    def integrate_markers(self, 
                         ocr_markers: Optional[Dict[str, Any]] = None,
                         yolo_markers: Optional[Dict[str, Any]] = None,
                         mediapipe_markers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Integrate markers from all sources into unified structure.
        
        Args:
            ocr_markers: Markers from OCR extractor
            yolo_markers: Markers from YOLO extractor
            mediapipe_markers: Markers from MediaPipe extractor
            
        Returns:
            Unified temporal markers dictionary
        """
        # Initialize unified structure
        unified = {
            'first_5_seconds': {
                'density_progression': [0, 0, 0, 0, 0],
                'text_moments': [],
                'emotion_sequence': ['neutral'] * 5,
                'gesture_moments': [],
                'object_appearances': []
            },
            'cta_window': {
                'time_range': f"{max(0, self.video_duration * 0.85):.1f}-{self.video_duration:.1f}s",
                'cta_appearances': [],
                'gesture_sync': [],
                'object_focus': []
            }
        }
        
        # Merge OCR markers
        if ocr_markers:
            first_5 = ocr_markers.get('first_5_seconds', {})
            unified['first_5_seconds']['text_moments'] = first_5.get('text_moments', [])
            
            # Update density with text density
            text_density = first_5.get('density_progression', [0] * 5)
            for i in range(5):
                unified['first_5_seconds']['density_progression'][i] += text_density[i]
                
            # CTA appearances
            cta = ocr_markers.get('cta_window', {})
            unified['cta_window']['cta_appearances'] = cta.get('cta_appearances', [])
        
        # Merge YOLO markers
        if yolo_markers:
            first_5 = yolo_markers.get('first_5_seconds', {})
            unified['first_5_seconds']['object_appearances'] = first_5.get('object_appearances', [])
            
            # Update density with object density
            obj_density = first_5.get('density_progression', [0] * 5)
            for i in range(5):
                unified['first_5_seconds']['density_progression'][i] += obj_density[i]
                
            # Object focus in CTA
            cta = yolo_markers.get('cta_window', {})
            unified['cta_window']['object_focus'] = cta.get('object_focus', [])
        
        # Merge MediaPipe markers
        if mediapipe_markers:
            first_5 = mediapipe_markers.get('first_5_seconds', {})
            
            # Emotion sequence (replace, don't merge)
            emotion_seq = first_5.get('emotion_sequence', ['neutral'] * 5)
            unified['first_5_seconds']['emotion_sequence'] = emotion_seq
            
            # Gesture moments
            unified['first_5_seconds']['gesture_moments'] = first_5.get('gesture_moments', [])
            
            # Gesture sync in CTA
            cta = mediapipe_markers.get('cta_window', {})
            unified['cta_window']['gesture_sync'] = cta.get('gesture_sync', [])
        
        # Calculate average density per second
        for i in range(5):
            unified['first_5_seconds']['density_progression'][i] = min(
                unified['first_5_seconds']['density_progression'][i],
                10  # Cap at 10 events per second
            )
        
        # Final safety check and size reduction
        unified = TemporalMarkerSafety.check_and_reduce_size(unified)
        
        # Validate structure
        errors = TemporalMarkerSafety.validate_markers(unified)
        if errors:
            logger.warning(f"Validation errors in unified markers: {errors}")
            
        return unified