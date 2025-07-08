"""
Temporal Marker Safety Controls for RumiAI
Ensures temporal markers stay within size limits and use standardized vocabularies
Prevents payload explosion and API failures
"""

import json
import copy
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class TemporalMarkerSafety:
    """
    Size limits and content sanitization for temporal markers.
    Prevents payload explosion and ensures data quality.
    """
    
    # Size limits
    MAX_TEXT_LENGTH = 50
    MAX_TEXT_EVENTS_FIRST_5S = 10
    MAX_GESTURE_EVENTS_FIRST_5S = 8
    MAX_CTA_EVENTS = 8
    MAX_MARKER_SIZE_KB = 50
    HARD_PAYLOAD_LIMIT_KB = 180  # Leave 20KB buffer for 200KB API limit
    
    # Standardized vocabularies
    STANDARD_GESTURE_VOCAB = {
        # Pointing variations
        "pointing": "pointing",
        "pointing_up": "pointing",
        "pointing_down": "pointing",
        "finger_point": "pointing",
        "finger_point_up": "pointing",
        "finger_point_down": "pointing",
        "point": "pointing",
        
        # Wave variations
        "wave": "wave",
        "hand_wave": "wave",
        "waving": "wave",
        "wave_hand": "wave",
        
        # Approval gestures
        "approval": "approval",
        "thumbs_up": "approval",
        "thumb_up": "approval",
        "ok_sign": "approval",
        "okay": "approval",
        
        # Peace/Victory
        "peace_sign": "peace",
        "peace": "peace",
        "victory": "peace",
        "v_sign": "peace",
        
        # Hand gestures
        "open_palm": "open_hand",
        "open_hand": "open_hand",
        "stop_sign": "open_hand",
        "high_five": "open_hand",
        
        # Clapping
        "clapping": "clap",
        "clap": "clap",
        "applause": "clap",
        "hands_up": "hands_up",
        
        # Other common gestures
        "fist": "fist",
        "fist_bump": "fist",
        "heart": "heart",
        "heart_hands": "heart",
        "crossed_arms": "crossed_arms",
        "arms_crossed": "crossed_arms",
        
        # Default
        "unknown": "unknown",
        "none": "unknown",
        "": "unknown"
    }
    
    STANDARD_EMOTION_VOCAB = {
        # Positive emotions
        "happy": "happy",
        "happiness": "happy",
        "joy": "happy",
        "joyful": "happy",
        "smile": "happy",
        "smiling": "happy",
        
        # Surprise
        "surprise": "surprise",
        "surprised": "surprise",
        "shock": "surprise",
        "shocked": "surprise",
        "amazed": "surprise",
        
        # Neutral
        "neutral": "neutral",
        "calm": "neutral",
        "normal": "neutral",
        "default": "neutral",
        
        # Negative emotions
        "sad": "sad",
        "sadness": "sad",
        "unhappy": "sad",
        "angry": "angry",
        "anger": "angry",
        "mad": "angry",
        "fear": "fear",
        "scared": "fear",
        "afraid": "fear",
        
        # Default
        "unknown": "unknown",
        "none": "unknown",
        "": "unknown"
    }
    
    @staticmethod
    def truncate_text(text: Any) -> str:
        """
        Safely truncate text with ellipsis.
        
        Args:
            text: Text to truncate (any type)
            
        Returns:
            Truncated string, max 50 characters
        """
        if not text:
            return ""
        
        # Convert to string and clean
        text_str = str(text).strip()
        
        # Remove excessive whitespace
        text_str = ' '.join(text_str.split())
        
        # Truncate if needed
        if len(text_str) > TemporalMarkerSafety.MAX_TEXT_LENGTH:
            return text_str[:47] + "..."
        
        return text_str
    
    @staticmethod
    def standardize_gesture(gesture: Any) -> str:
        """
        Map gesture to standard vocabulary.
        
        Args:
            gesture: Raw gesture string
            
        Returns:
            Standardized gesture string
        """
        if not gesture:
            return "unknown"
        
        gesture_str = str(gesture).lower().strip()
        return TemporalMarkerSafety.STANDARD_GESTURE_VOCAB.get(gesture_str, "unknown")
    
    @staticmethod
    def standardize_emotion(emotion: Any) -> str:
        """
        Map emotion to standard vocabulary.
        
        Args:
            emotion: Raw emotion string
            
        Returns:
            Standardized emotion string
        """
        if not emotion:
            return "unknown"
        
        emotion_str = str(emotion).lower().strip()
        return TemporalMarkerSafety.STANDARD_EMOTION_VOCAB.get(emotion_str, "unknown")
    
    @staticmethod
    def classify_text_size(bbox: Optional[Dict[str, float]]) -> str:
        """
        Classify text size based on bounding box.
        
        Args:
            bbox: Bounding box with x1, y1, x2, y2
            
        Returns:
            Size classification: S, M, or L
        """
        if not bbox or not isinstance(bbox, dict):
            return "M"
        
        try:
            width = abs(bbox.get('x2', 0) - bbox.get('x1', 0))
            height = abs(bbox.get('y2', 0) - bbox.get('y1', 0))
            area = width * height
            
            # Classify based on area
            if area > 10000:
                return "L"
            elif area > 1000:
                return "M"
            else:
                return "S"
        except:
            return "M"
    
    @staticmethod
    def check_and_reduce_size(markers: Dict[str, Any], target_kb: float = MAX_MARKER_SIZE_KB) -> Dict[str, Any]:
        """
        Progressive size reduction if over limits.
        
        Args:
            markers: Temporal markers dictionary
            target_kb: Target size in KB
            
        Returns:
            Reduced markers dictionary
        """
        # Calculate current size
        current_size_kb = len(json.dumps(markers)) / 1024
        
        if current_size_kb <= target_kb:
            logger.info(f"Markers size {current_size_kb:.1f}KB is within limit")
            return markers
        
        logger.warning(f"Markers size {current_size_kb:.1f}KB exceeds {target_kb}KB limit, reducing...")
        
        # Deep copy to avoid modifying original
        reduced = copy.deepcopy(markers)
        
        # Progressive reduction steps
        reduction_steps = [
            TemporalMarkerSafety._reduce_text_events,
            TemporalMarkerSafety._reduce_gesture_events,
            TemporalMarkerSafety._reduce_cta_events,
            TemporalMarkerSafety._remove_optional_fields,
            TemporalMarkerSafety._aggressive_reduction
        ]
        
        for step in reduction_steps:
            reduced = step(reduced)
            new_size_kb = len(json.dumps(reduced)) / 1024
            
            if new_size_kb <= target_kb:
                logger.info(f"Reduced markers to {new_size_kb:.1f}KB")
                return reduced
        
        # Final check
        final_size_kb = len(json.dumps(reduced)) / 1024
        if final_size_kb > target_kb:
            logger.error(f"Could not reduce markers below {final_size_kb:.1f}KB")
        
        return reduced
    
    @staticmethod
    def _reduce_text_events(markers: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Limit text events to maximum allowed."""
        if 'first_5_seconds' in markers and 'text_moments' in markers['first_5_seconds']:
            original_count = len(markers['first_5_seconds']['text_moments'])
            markers['first_5_seconds']['text_moments'] = \
                markers['first_5_seconds']['text_moments'][:TemporalMarkerSafety.MAX_TEXT_EVENTS_FIRST_5S]
            
            if original_count > TemporalMarkerSafety.MAX_TEXT_EVENTS_FIRST_5S:
                logger.info(f"Reduced text events from {original_count} to {TemporalMarkerSafety.MAX_TEXT_EVENTS_FIRST_5S}")
        
        return markers
    
    @staticmethod
    def _reduce_gesture_events(markers: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Limit gesture events."""
        if 'first_5_seconds' in markers and 'gesture_moments' in markers['first_5_seconds']:
            original_count = len(markers['first_5_seconds']['gesture_moments'])
            markers['first_5_seconds']['gesture_moments'] = \
                markers['first_5_seconds']['gesture_moments'][:TemporalMarkerSafety.MAX_GESTURE_EVENTS_FIRST_5S]
            
            if original_count > TemporalMarkerSafety.MAX_GESTURE_EVENTS_FIRST_5S:
                logger.info(f"Reduced gesture events from {original_count} to {TemporalMarkerSafety.MAX_GESTURE_EVENTS_FIRST_5S}")
        
        return markers
    
    @staticmethod
    def _reduce_cta_events(markers: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Limit CTA events."""
        if 'cta_window' in markers and 'cta_appearances' in markers['cta_window']:
            original_count = len(markers['cta_window']['cta_appearances'])
            markers['cta_window']['cta_appearances'] = \
                markers['cta_window']['cta_appearances'][:TemporalMarkerSafety.MAX_CTA_EVENTS]
            
            if original_count > TemporalMarkerSafety.MAX_CTA_EVENTS:
                logger.info(f"Reduced CTA events from {original_count} to {TemporalMarkerSafety.MAX_CTA_EVENTS}")
        
        return markers
    
    @staticmethod
    def _remove_optional_fields(markers: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Remove optional fields like confidence scores, positions."""
        optional_fields = ['confidence', 'position', 'intensity', 'target', 'bbox']
        
        def remove_fields(obj):
            if isinstance(obj, dict):
                # Remove optional fields
                for field in optional_fields:
                    obj.pop(field, None)
                # Recurse into nested objects
                for value in obj.values():
                    remove_fields(value)
            elif isinstance(obj, list):
                for item in obj:
                    remove_fields(item)
        
        remove_fields(markers)
        logger.info("Removed optional fields")
        return markers
    
    @staticmethod
    def _aggressive_reduction(markers: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Aggressive reduction - keep only essential data."""
        logger.warning("Applying aggressive reduction")
        
        # Keep only the most essential events
        if 'first_5_seconds' in markers:
            if 'text_moments' in markers['first_5_seconds']:
                markers['first_5_seconds']['text_moments'] = markers['first_5_seconds']['text_moments'][:5]
            if 'gesture_moments' in markers['first_5_seconds']:
                markers['first_5_seconds']['gesture_moments'] = markers['first_5_seconds']['gesture_moments'][:3]
            if 'object_appearances' in markers['first_5_seconds']:
                markers['first_5_seconds']['object_appearances'] = markers['first_5_seconds']['object_appearances'][:5]
        
        if 'cta_window' in markers:
            if 'cta_appearances' in markers['cta_window']:
                markers['cta_window']['cta_appearances'] = markers['cta_window']['cta_appearances'][:3]
            # Remove less critical CTA data
            markers['cta_window'].pop('gesture_sync', None)
            markers['cta_window'].pop('ui_emphasis', None)
        
        return markers
    
    @staticmethod
    def validate_markers(markers: Dict[str, Any]) -> List[str]:
        """
        Validate temporal markers structure and content.
        
        Args:
            markers: Temporal markers to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check overall structure
        if not isinstance(markers, dict):
            errors.append("Markers must be a dictionary")
            return errors
        
        # Validate first_5_seconds
        if 'first_5_seconds' in markers:
            first_5 = markers['first_5_seconds']
            
            # Check text moments
            if 'text_moments' in first_5:
                for i, text_moment in enumerate(first_5['text_moments']):
                    if not isinstance(text_moment.get('time'), (int, float)):
                        errors.append(f"Text moment {i} missing valid time")
                    if not isinstance(text_moment.get('text'), str):
                        errors.append(f"Text moment {i} missing valid text")
                    if text_moment.get('time', 0) > 5.0:
                        errors.append(f"Text moment {i} time {text_moment.get('time')} exceeds 5 seconds")
            
            # Check emotion sequence
            if 'emotion_sequence' in first_5:
                if not isinstance(first_5['emotion_sequence'], list):
                    errors.append("Emotion sequence must be a list")
                elif len(first_5['emotion_sequence']) != 5:
                    errors.append(f"Emotion sequence should have 5 items, got {len(first_5['emotion_sequence'])}")
        
        # Validate CTA window
        if 'cta_window' in markers:
            cta = markers['cta_window']
            
            # Check time range
            if 'time_range' not in cta:
                errors.append("CTA window missing time_range")
            
            # Check CTA appearances
            if 'cta_appearances' in cta:
                for i, cta_item in enumerate(cta['cta_appearances']):
                    if not isinstance(cta_item.get('time'), (int, float)):
                        errors.append(f"CTA {i} missing valid time")
                    if not isinstance(cta_item.get('text'), str):
                        errors.append(f"CTA {i} missing valid text")
        
        # Check size
        size_kb = len(json.dumps(markers)) / 1024
        if size_kb > TemporalMarkerSafety.MAX_MARKER_SIZE_KB:
            errors.append(f"Markers size {size_kb:.1f}KB exceeds limit of {TemporalMarkerSafety.MAX_MARKER_SIZE_KB}KB")
        
        return errors
    
    @staticmethod
    def sanitize_for_json(obj: Any) -> Any:
        """
        Ensure object is JSON serializable.
        Converts numpy types, handles None values, etc.
        """
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {k: TemporalMarkerSafety.sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [TemporalMarkerSafety.sanitize_for_json(item) for item in obj]
        else:
            # Try to convert numpy/other types
            try:
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
            except ImportError:
                pass
            
            # Fallback to string representation
            return str(obj)