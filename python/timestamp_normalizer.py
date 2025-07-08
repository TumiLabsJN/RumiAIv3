"""
Timestamp Normalizer for RumiAI Video Analysis
Converts various timestamp formats to consistent seconds
Critical for aligning data across different analyzers
"""

import re
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class TimestampNormalizer:
    """
    Converts all timestamp formats to consistent seconds.
    
    Different analyzers use different timestamp formats:
    - OCR: frame_0015_t0.50.jpg (filename with timestamp)
    - YOLO: 0.5 (float seconds)
    - MediaPipe: 15 (frame indices)
    - UnifiedTimeline: "0-1s" (string ranges)
    - Enhanced Human: frame number at extraction FPS
    
    This class ensures all timestamps are normalized to float seconds.
    """
    
    def __init__(self, video_metadata: Dict[str, Any]):
        """
        Initialize with video metadata.
        
        Args:
            video_metadata: Dictionary containing:
                - fps: Original video FPS (default: 30.0)
                - extraction_fps: Frame extraction FPS (default: 2.0)
                - frame_count: Total frames in video
                - duration: Video duration in seconds
        """
        self.fps = float(video_metadata.get('fps', 30.0))
        self.extraction_fps = float(video_metadata.get('extraction_fps', 2.0))
        self.frame_count = int(video_metadata.get('frame_count', 0))
        self.duration = float(video_metadata.get('duration', 0.0))
        
        # Validate metadata
        if self.fps <= 0:
            raise ValueError(f"Invalid FPS: {self.fps}")
        if self.extraction_fps <= 0:
            raise ValueError(f"Invalid extraction FPS: {self.extraction_fps}")
        
        logger.info(f"TimestampNormalizer initialized: fps={self.fps}, "
                   f"extraction_fps={self.extraction_fps}, duration={self.duration}")
    
    def normalize_to_seconds(self, value: Any, source_type: str) -> Optional[float]:
        """
        Convert any timestamp format to seconds.
        
        Args:
            value: The timestamp value to convert
            source_type: Type of timestamp format:
                - 'frame_filename': "frame_0015_t0.50.jpg"
                - 'frame_index': Frame number at original FPS
                - 'extracted_frame_index': Frame number at extraction FPS
                - 'timeline_string': "0-1s" range format
                - 'float_seconds': Already in seconds
                
        Returns:
            Float seconds or None if parsing fails
        """
        try:
            if source_type == 'frame_filename':
                return self._parse_frame_filename(value)
            elif source_type == 'frame_index':
                return self._frame_index_to_seconds(value)
            elif source_type == 'extracted_frame_index':
                return self._extracted_frame_to_seconds(value)
            elif source_type == 'timeline_string':
                return self._parse_timeline_string(value)
            elif source_type == 'float_seconds':
                return float(value)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
                
        except Exception as e:
            logger.warning(f"Failed to normalize {value} from {source_type}: {e}")
            return None
    
    def _parse_frame_filename(self, filename: str) -> Optional[float]:
        """
        Parse timestamp from frame filename.
        Expected format: frame_XXXX_tY.YY.jpg
        """
        # Try to extract timestamp from filename
        match = re.search(r't(\d+\.?\d*)', str(filename))
        if match:
            return float(match.group(1))
        
        # Fallback: try to extract frame number
        frame_match = re.search(r'frame_(\d+)', str(filename))
        if frame_match:
            frame_num = int(frame_match.group(1))
            # Assume this is extracted frame number
            return self._extracted_frame_to_seconds(frame_num)
        
        return None
    
    def _frame_index_to_seconds(self, frame_index: Any) -> float:
        """Convert frame index at original FPS to seconds."""
        return float(frame_index) / self.fps
    
    def _extracted_frame_to_seconds(self, extracted_index: Any) -> float:
        """Convert extracted frame index to seconds."""
        return float(extracted_index) / self.extraction_fps
    
    def _parse_timeline_string(self, timeline_str: str) -> Optional[float]:
        """
        Parse timeline string format like "0-1s" or "15-16s".
        Returns the start time.
        """
        try:
            # Remove 's' suffix if present
            timeline_str = str(timeline_str).replace('s', '')
            # Split by dash and take first part
            parts = timeline_str.split('-')
            if parts:
                return float(parts[0])
        except:
            pass
        return None
    
    def validate_timestamp(self, timestamp_seconds: float) -> bool:
        """
        Validate that timestamp is within video bounds.
        
        Args:
            timestamp_seconds: Timestamp in seconds
            
        Returns:
            True if valid, False otherwise
        """
        if timestamp_seconds is None:
            return False
        
        # Allow small negative values (rounding errors)
        if timestamp_seconds < -0.1:
            return False
        
        # Allow small overshoot at end (rounding errors)
        if self.duration > 0 and timestamp_seconds > self.duration + 0.1:
            return False
        
        return True
    
    def get_timeline_range(self, start_seconds: float, end_seconds: float) -> str:
        """
        Format a time range for timeline output.
        
        Args:
            start_seconds: Start time in seconds
            end_seconds: End time in seconds
            
        Returns:
            Formatted string like "0-1s"
        """
        return f"{start_seconds:.1f}-{end_seconds:.1f}s"
    
    def batch_normalize(self, values: list, source_type: str) -> list:
        """
        Normalize a batch of timestamps efficiently.
        
        Args:
            values: List of timestamp values
            source_type: Type of all timestamps
            
        Returns:
            List of normalized seconds (None for failed conversions)
        """
        return [self.normalize_to_seconds(v, source_type) for v in values]


def create_from_video_path(video_path: str) -> Optional[TimestampNormalizer]:
    """
    Convenience function to create normalizer from video file.
    Extracts metadata and creates normalizer.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        metadata = {
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'extraction_fps': 2.0  # Default, should be provided
        }
        
        return TimestampNormalizer(metadata)
        
    except Exception as e:
        logger.error(f"Failed to create normalizer from video: {e}")
        return None