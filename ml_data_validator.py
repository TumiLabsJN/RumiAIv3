#!/usr/bin/env python3
"""
ML Data Validation Module
Ensures only real ML detection data is sent to Claude for analysis
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLDataValidator:
    """Validates ML data to prevent fabricated content"""
    
    # Suspicious patterns that indicate fabricated data
    SUSPICIOUS_PATTERNS = [
        "link in bio",
        "swipe up", 
        "tap here",
        "click link",
        "check bio",
        "see bio",
        "dm me",
        "follow me",
        "subscribe",
        "like and share"
    ]
    
    # Confidence thresholds for different ML models
    CONFIDENCE_THRESHOLDS = {
        'text_detection': 0.6,
        'object_detection': 0.5,
        'pose_detection': 0.4,
        'face_detection': 0.5
    }
    
    def __init__(self):
        self.validation_log = []
        
    def log_validation(self, level: str, message: str, data: Dict = None):
        """Log validation events"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }
        self.validation_log.append(entry)
        
        if level == 'WARNING':
            logger.warning(message)
        elif level == 'ERROR':
            logger.error(message)
        else:
            logger.info(message)
    
    def validate_text_detection(self, text_data: Dict) -> Dict:
        """Validate text detection data"""
        validated_data = {}
        total_detections = 0
        suspicious_count = 0
        
        for timestamp, data in text_data.items():
            validated_entry = {}
            
            if isinstance(data, dict):
                # Check for texts array
                if 'texts' in data and isinstance(data['texts'], list):
                    valid_texts = []
                    for text_item in data['texts']:
                        if isinstance(text_item, dict) and 'text' in text_item:
                            text_content = text_item['text'].lower()
                            
                            # Check for suspicious patterns
                            is_suspicious = any(pattern in text_content for pattern in self.SUSPICIOUS_PATTERNS)
                            
                            if is_suspicious:
                                suspicious_count += 1
                                self.log_validation('WARNING', 
                                    f"Suspicious text pattern detected: '{text_item['text']}' at {timestamp}",
                                    {'timestamp': timestamp, 'text': text_item['text']})
                            
                            # Check confidence if available
                            confidence = text_item.get('confidence', 1.0)
                            if confidence >= self.CONFIDENCE_THRESHOLDS['text_detection']:
                                valid_texts.append(text_item)
                                total_detections += 1
                            else:
                                self.log_validation('INFO', 
                                    f"Text detection below confidence threshold: {confidence} at {timestamp}")
                    
                    if valid_texts:
                        validated_entry['texts'] = valid_texts
                
                # Preserve other validated fields
                if 'bbox' in data:
                    validated_entry['bbox'] = data['bbox']
                if 'confidence' in data:
                    validated_entry['confidence'] = data['confidence']
            
            if validated_entry:
                validated_data[timestamp] = validated_entry
        
        self.log_validation('INFO', 
            f"Text validation complete: {total_detections} valid detections, {suspicious_count} suspicious")
        
        return validated_data
    
    def validate_object_detection(self, object_data: Dict) -> Dict:
        """Validate object detection data"""
        validated_data = {}
        total_detections = 0
        
        for timestamp, data in object_data.items():
            validated_entry = {}
            
            if isinstance(data, dict):
                # Check for objects array
                if 'objects' in data and isinstance(data['objects'], list):
                    valid_objects = []
                    for obj in data['objects']:
                        if isinstance(obj, dict) and 'class' in obj:
                            confidence = obj.get('confidence', 1.0)
                            if confidence >= self.CONFIDENCE_THRESHOLDS['object_detection']:
                                valid_objects.append(obj)
                                total_detections += 1
                    
                    if valid_objects:
                        validated_entry['objects'] = valid_objects
                
                # Preserve other fields
                if 'total_objects' in data:
                    validated_entry['total_objects'] = data['total_objects']
            
            if validated_entry:
                validated_data[timestamp] = validated_entry
        
        self.log_validation('INFO', f"Object validation complete: {total_detections} valid detections")
        return validated_data
    
    def validate_timeline_consistency(self, timeline_data: Dict, video_duration: float) -> bool:
        """Check if timeline data is consistent with video duration"""
        max_timestamp = 0
        
        for timestamp in timeline_data.keys():
            try:
                # Parse timestamp (e.g., "5-6s" -> 6)
                if '-' in timestamp:
                    end_time = float(timestamp.split('-')[1].replace('s', ''))
                    max_timestamp = max(max_timestamp, end_time)
                else:
                    time_val = float(timestamp.replace('s', ''))
                    max_timestamp = max(max_timestamp, time_val)
            except:
                continue
        
        if max_timestamp > video_duration + 2:  # Allow 2 second buffer
            self.log_validation('WARNING', 
                f"Timeline extends beyond video duration: {max_timestamp}s > {video_duration}s")
            return False
        
        return True
    
    def extract_real_ml_data(self, unified_data: Dict, prompt_type: str) -> Dict:
        """Extract only real ML detection data for a specific prompt type"""
        extracted_data = {
            '_validation': {
                'extracted_at': datetime.now().isoformat(),
                'prompt_type': prompt_type,
                'data_source': 'unified_analysis',
                'validator_version': '1.0'
            }
        }
        
        timelines = unified_data.get('timelines', {})
        video_duration = unified_data.get('duration_seconds', 30)
        
        # Extract based on prompt type
        if prompt_type == 'hook_analysis':
            # Only first 5 seconds for hook analysis
            extracted_data.update(self._extract_hook_data(timelines, video_duration))
            
        elif prompt_type == 'cta_alignment':
            # CTA-specific extractions
            extracted_data.update(self._extract_cta_data(timelines, video_duration))
            
        elif prompt_type == 'creative_density':
            # Creative density metrics
            extracted_data.update(self._extract_density_data(timelines, video_duration))
            
        elif prompt_type == 'emotional_journey':
            # Emotional analysis data
            extracted_data.update(self._extract_emotional_data(timelines, video_duration))
            
        else:
            # General extraction for other prompt types
            extracted_data.update(self._extract_general_data(timelines, video_duration))
        
        # Add validation summary
        extracted_data['_validation']['summary'] = {
            'warnings': len([log for log in self.validation_log if log['level'] == 'WARNING']),
            'errors': len([log for log in self.validation_log if log['level'] == 'ERROR']),
            'total_validations': len(self.validation_log)
        }
        
        return extracted_data
    
    def _extract_hook_data(self, timelines: Dict, duration: float) -> Dict:
        """Extract data for hook analysis (first 5 seconds only)"""
        hook_data = {}
        
        # Text overlays in first 5 seconds
        text_timeline = timelines.get('textOverlayTimeline', {})
        hook_text = {}
        for timestamp, data in text_timeline.items():
            try:
                start_time = float(timestamp.split('-')[0])
                if start_time <= 5.0:
                    hook_text[timestamp] = data
            except:
                continue
        
        hook_data['text_timeline'] = self.validate_text_detection(hook_text)
        
        # Object detections in first 5 seconds
        object_timeline = timelines.get('objectTimeline', {})
        hook_objects = {}
        for timestamp, data in object_timeline.items():
            try:
                start_time = float(timestamp.split('-')[0])
                if start_time <= 5.0:
                    hook_objects[timestamp] = data
            except:
                continue
        
        hook_data['object_timeline'] = self.validate_object_detection(hook_objects)
        
        # Pose data in first 5 seconds
        gesture_timeline = timelines.get('gestureTimeline', {})
        hook_gestures = {}
        for timestamp, data in gesture_timeline.items():
            try:
                start_time = float(timestamp.split('-')[0])
                if start_time <= 5.0:
                    hook_gestures[timestamp] = data
            except:
                continue
        
        hook_data['gesture_timeline'] = hook_gestures
        
        self.log_validation('INFO', f"Hook analysis: extracted data for first 5 seconds")
        return hook_data
    
    def _extract_cta_data(self, timelines: Dict, duration: float) -> Dict:
        """Extract data for CTA alignment analysis"""
        cta_data = {}
        
        # All text detections (no fabrication allowed)
        text_timeline = timelines.get('textOverlayTimeline', {})
        cta_data['text_timeline'] = self.validate_text_detection(text_timeline)
        
        # Speech timeline if available
        speech_timeline = timelines.get('speechTimeline', {})
        cta_data['speech_timeline'] = speech_timeline  # Speech is usually from Whisper, trusted
        
        # Object detections that might be clickable
        object_timeline = timelines.get('objectTimeline', {})
        cta_data['object_timeline'] = self.validate_object_detection(object_timeline)
        
        self.log_validation('INFO', "CTA analysis: extracted text, speech, and object data")
        return cta_data
    
    def _extract_density_data(self, timelines: Dict, duration: float) -> Dict:
        """Extract data for creative density analysis"""
        density_data = {}
        
        # All timeline data for density calculation
        density_data['text_timeline'] = self.validate_text_detection(timelines.get('textOverlayTimeline', {}))
        density_data['sticker_timeline'] = timelines.get('stickerTimeline', {})
        density_data['gesture_timeline'] = timelines.get('gestureTimeline', {})
        density_data['object_timeline'] = self.validate_object_detection(timelines.get('objectTimeline', {}))
        
        # Timeline statistics
        density_data['timeline_stats'] = {
            'total_text_detections': len(density_data['text_timeline']),
            'total_sticker_detections': len(density_data['sticker_timeline']),
            'total_gesture_detections': len(density_data['gesture_timeline']),
            'total_object_detections': len(density_data['object_timeline']),
            'video_duration': duration
        }
        
        self.log_validation('INFO', "Density analysis: extracted all timeline data")
        return density_data
    
    def _extract_emotional_data(self, timelines: Dict, duration: float) -> Dict:
        """Extract data for emotional journey analysis"""
        emotional_data = {}
        
        # Expression timeline
        expression_timeline = timelines.get('expressionTimeline', {})
        emotional_data['expression_timeline'] = expression_timeline
        
        # Speech timeline for emotional cues
        speech_timeline = timelines.get('speechTimeline', {})
        emotional_data['speech_timeline'] = speech_timeline
        
        # Gesture timeline for emotional expressions
        gesture_timeline = timelines.get('gestureTimeline', {})
        emotional_data['gesture_timeline'] = gesture_timeline
        
        self.log_validation('INFO', "Emotional analysis: extracted expression, speech, and gesture data")
        return emotional_data
    
    def _extract_general_data(self, timelines: Dict, duration: float) -> Dict:
        """Extract general data for other prompt types"""
        general_data = {}
        
        # Extract all timelines with validation
        general_data['text_timeline'] = self.validate_text_detection(timelines.get('textOverlayTimeline', {}))
        general_data['object_timeline'] = self.validate_object_detection(timelines.get('objectTimeline', {}))
        general_data['gesture_timeline'] = timelines.get('gestureTimeline', {})
        general_data['expression_timeline'] = timelines.get('expressionTimeline', {})
        general_data['speech_timeline'] = timelines.get('speechTimeline', {})
        
        self.log_validation('INFO', "General analysis: extracted all available timeline data")
        return general_data
    
    def get_validation_report(self) -> Dict:
        """Get a summary of all validation activities"""
        return {
            'validation_log': self.validation_log,
            'summary': {
                'total_entries': len(self.validation_log),
                'warnings': len([log for log in self.validation_log if log['level'] == 'WARNING']),
                'errors': len([log for log in self.validation_log if log['level'] == 'ERROR']),
                'info': len([log for log in self.validation_log if log['level'] == 'INFO'])
            }
        }

# Convenience function for easy import
def validate_ml_data(unified_data: Dict, prompt_type: str) -> Dict:
    """Main function to validate ML data for a specific prompt type"""
    validator = MLDataValidator()
    return validator.extract_real_ml_data(unified_data, prompt_type)