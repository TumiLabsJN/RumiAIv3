"""
Temporal Marker Integration for RumiAI
Main integration module that collects temporal markers from all analyzers
and prepares them for Claude API consumption
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import all the extractors and utilities
from python.temporal_marker_extractors import (
    OCRTemporalExtractor,
    YOLOTemporalExtractor,
    MediaPipeTemporalExtractor,
    TemporalMarkerIntegrator
)
from python.timestamp_normalizer import TimestampNormalizer, create_from_video_path
from python.temporal_marker_safety import TemporalMarkerSafety

# Try to import monitoring
try:
    from python.temporal_monitoring import record_extraction
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


class TemporalMarkerPipeline:
    """
    Main pipeline for extracting and integrating temporal markers from all analyzers.
    This is the primary entry point for the temporal marker system.
    """
    
    def __init__(self, video_id: str, base_dir: str = '.'):
        """
        Initialize the temporal marker pipeline.
        
        Args:
            video_id: Video identifier
            base_dir: Base directory for finding analysis outputs
        """
        self.video_id = video_id
        self.base_dir = Path(base_dir)
        self.video_metadata = None
        
    def extract_all_markers(self) -> Dict[str, Any]:
        """
        Extract temporal markers from all available analyzer outputs.
        
        Returns:
            Integrated temporal markers ready for Claude
        """
        logger.info(f"Starting temporal marker extraction for video {self.video_id}")
        start_time = time.time()
        
        # 1. Get video metadata
        self.video_metadata = self._get_video_metadata()
        if not self.video_metadata:
            logger.warning("Could not determine video metadata, using defaults")
            self.video_metadata = {
                'fps': 30.0,
                'extraction_fps': 2.0,
                'duration': 60.0,
                'frame_count': 1800
            }
        
        # 2. Extract markers from each analyzer
        ocr_markers = self._extract_ocr_markers()
        yolo_markers = self._extract_yolo_markers()
        mediapipe_markers = self._extract_mediapipe_markers()
        
        # 3. Integrate all markers
        integrator = TemporalMarkerIntegrator(self.video_metadata)
        integrated_markers = integrator.integrate_markers(
            ocr_markers=ocr_markers,
            yolo_markers=yolo_markers,
            mediapipe_markers=mediapipe_markers
        )
        
        # 4. Add metadata
        integrated_markers['metadata'] = {
            'video_id': self.video_id,
            'video_duration': self.video_metadata['duration'],
            'extraction_fps': self.video_metadata['extraction_fps'],
            'markers_version': '1.0'
        }
        
        # 5. Final validation
        errors = TemporalMarkerSafety.validate_markers(integrated_markers)
        if errors:
            logger.warning(f"Validation warnings: {errors}")
        
        # 6. Record metrics if monitoring is available
        extraction_time = time.time() - start_time
        marker_size_kb = len(json.dumps(integrated_markers)) / 1024
        
        if MONITORING_AVAILABLE:
            try:
                record_extraction(
                    video_id=self.video_id,
                    success=True,
                    extraction_time=extraction_time,
                    marker_size_kb=marker_size_kb,
                    error=None
                )
            except Exception as e:
                logger.warning(f"Failed to record extraction metrics: {e}")
        
        logger.info(f"Extraction complete in {extraction_time:.2f}s, size: {marker_size_kb:.1f}KB")
            
        return integrated_markers
    
    def _get_video_metadata(self) -> Optional[Dict[str, Any]]:
        """Get video metadata from various sources."""
        # Try frame metadata
        frame_metadata_path = self.base_dir / 'frame_outputs' / self.video_id / 'metadata.json'
        if frame_metadata_path.exists():
            try:
                with open(frame_metadata_path, 'r') as f:
                    metadata = json.load(f)
                    return {
                        'fps': metadata.get('fps', 30.0),
                        'extraction_fps': metadata.get('extraction_fps', 2.0),
                        'duration': metadata.get('duration', 60.0),
                        'frame_count': metadata.get('frame_count', 1800)
                    }
            except Exception as e:
                logger.error(f"Error reading frame metadata: {e}")
        
        # Try video file directly
        video_paths = [
            self.base_dir / 'downloads' / 'videos' / f'{self.video_id}.mp4',
            self.base_dir / 'temp' / 'videos' / f'{self.video_id}.mp4'
        ]
        
        for video_path in video_paths:
            if video_path.exists():
                normalizer = create_from_video_path(str(video_path))
                if normalizer:
                    return {
                        'fps': normalizer.fps,
                        'extraction_fps': 2.0,  # Default assumption
                        'duration': normalizer.duration,
                        'frame_count': normalizer.frame_count
                    }
        
        return None
    
    def _extract_ocr_markers(self) -> Optional[Dict[str, Any]]:
        """Extract temporal markers from OCR/creative elements analysis."""
        analysis_paths = [
            self.base_dir / 'creative_analysis_outputs' / self.video_id / f'{self.video_id}_creative_analysis.json',
            self.base_dir / 'downloads' / 'analysis' / self.video_id / 'creative_analysis.json'
        ]
        
        for path in analysis_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    
                    # Check if temporal markers already extracted
                    if 'temporal_markers' in data:
                        logger.info("Using pre-extracted OCR temporal markers")
                        return data['temporal_markers']
                    
                    # Extract from frame details
                    if 'frame_details' in data:
                        logger.info("Extracting OCR temporal markers from frame details")
                        extractor = OCRTemporalExtractor(self.video_metadata)
                        return extractor.extract_temporal_markers(data['frame_details'])
                        
                except Exception as e:
                    logger.error(f"Error extracting OCR markers: {e}")
                    
        logger.warning("No OCR analysis found")
        return None
    
    def _extract_yolo_markers(self) -> Optional[Dict[str, Any]]:
        """Extract temporal markers from YOLO object tracking."""
        tracking_paths = [
            self.base_dir / 'downloads' / 'videos' / f'{self.video_id}_tracking.json',
            self.base_dir / 'downloads' / 'analysis' / self.video_id / 'object_tracking.json',
            self.base_dir / 'temp' / 'tracking' / f'{self.video_id}_tracking.json'
        ]
        
        for path in tracking_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    
                    # Check if temporal markers already extracted
                    if 'temporal_markers' in data:
                        logger.info("Using pre-extracted YOLO temporal markers")
                        return data['temporal_markers']
                    
                    # Convert to expected format
                    if 'objectAnnotations' in data:
                        logger.info("Extracting YOLO temporal markers from object annotations")
                        tracking_data = self._convert_object_annotations(data['objectAnnotations'])
                        extractor = YOLOTemporalExtractor(self.video_metadata)
                        return extractor.extract_temporal_markers(tracking_data)
                        
                except Exception as e:
                    logger.error(f"Error extracting YOLO markers: {e}")
                    
        logger.warning("No YOLO tracking found")
        return None
    
    def _extract_mediapipe_markers(self) -> Optional[Dict[str, Any]]:
        """Extract temporal markers from MediaPipe enhanced human analysis."""
        analysis_paths = [
            self.base_dir / 'enhanced_human_analysis_outputs' / self.video_id / f'{self.video_id}_enhanced_human_analysis.json',
            self.base_dir / 'downloads' / 'analysis' / self.video_id / 'enhanced_human_analysis.json'
        ]
        
        for path in analysis_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    
                    # Check if temporal markers already extracted
                    if 'temporal_markers' in data:
                        logger.info("Using pre-extracted MediaPipe temporal markers")
                        return data['temporal_markers']
                    
                    # Convert frame analyses to timeline format
                    if 'frame_analyses' in data:
                        logger.info("Extracting MediaPipe temporal markers from frame analyses")
                        timeline_data = self._convert_frame_analyses_to_timeline(data['frame_analyses'])
                        extractor = MediaPipeTemporalExtractor(self.video_metadata)
                        return extractor.extract_temporal_markers(timeline_data)
                        
                except Exception as e:
                    logger.error(f"Error extracting MediaPipe markers: {e}")
                    
        logger.warning("No MediaPipe analysis found")
        return None
    
    def _convert_object_annotations(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert object annotations to tracking data format."""
        tracks = []
        
        for annotation in annotations:
            track_id = annotation.get('trackId', '').replace('object_', '')
            entity = annotation.get('entity', {})
            
            detections = []
            for frame_data in annotation.get('frames', []):
                detections.append({
                    'frame': frame_data.get('frame', 0),
                    'class': entity.get('entityId', 'unknown'),
                    'confidence': frame_data.get('confidence', annotation.get('confidence', 0.5))
                })
            
            if detections:
                tracks.append({
                    'track_id': track_id,
                    'detections': detections
                })
        
        return {'tracks': tracks}
    
    def _convert_frame_analyses_to_timeline(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert enhanced human frame analyses to timeline format."""
        timeline = {
            'timeline': {
                'expressions': [],
                'gestures': []
            }
        }
        
        for frame in frame_analyses:
            frame_idx = frame.get('frame', 0)
            
            # Extract expressions from faces
            if 'faces' in frame and frame['faces']:
                for face in frame['faces']:
                    if 'expression' in face:
                        timeline['timeline']['expressions'].append({
                            'frame': frame_idx,
                            'expression': face['expression']
                        })
                        break  # Only take primary face
            
            # Extract gestures from actions
            if 'action_recognition' in frame:
                primary_action = frame['action_recognition'].get('primary_action')
                if primary_action and primary_action != 'unknown':
                    # Map actions to gesture vocabulary
                    gesture_map = {
                        'pointing': 'pointing',
                        'dancing': 'wave',
                        'talking': None,  # Skip non-gestures
                        'walking': None,
                        'sitting': None
                    }
                    
                    gesture = gesture_map.get(primary_action)
                    if gesture:
                        timeline['timeline']['gestures'].append({
                            'frame': frame_idx,
                            'gesture': gesture,
                            'confidence': frame['action_recognition'].get('action_confidence', 0.8)
                        })
            
            # Check for hand detection as open_hand gesture
            if 'hands' in frame and frame['hands']:
                timeline['timeline']['gestures'].append({
                    'frame': frame_idx,
                    'gesture': 'open_hand',
                    'confidence': 0.9
                })
        
        return timeline
    
    def save_markers(self, markers: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Save temporal markers to file.
        
        Args:
            markers: Temporal markers to save
            output_path: Optional output path, defaults to temporal_markers/<video_id>_markers.json
            
        Returns:
            Path where markers were saved
        """
        if not output_path:
            output_dir = self.base_dir / 'temporal_markers'
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f'{self.video_id}_temporal_markers.json'
        else:
            output_path = Path(output_path)
            
        with open(output_path, 'w') as f:
            json.dump(markers, f, indent=2)
            
        logger.info(f"Saved temporal markers to {output_path}")
        return str(output_path)
    
    def get_marker_summary(self, markers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of the extracted temporal markers.
        
        Args:
            markers: Temporal markers
            
        Returns:
            Summary statistics
        """
        first_5 = markers.get('first_5_seconds', {})
        cta = markers.get('cta_window', {})
        
        summary = {
            'video_id': self.video_id,
            'duration': self.video_metadata.get('duration', 0),
            'first_5_seconds': {
                'text_moments': len(first_5.get('text_moments', [])),
                'density_avg': sum(first_5.get('density_progression', [])) / 5,
                'emotions': first_5.get('emotion_sequence', []),
                'gesture_count': len(first_5.get('gesture_moments', [])),
                'object_appearances': len(first_5.get('object_appearances', []))
            },
            'cta_window': {
                'time_range': cta.get('time_range', ''),
                'cta_count': len(cta.get('cta_appearances', [])),
                'gesture_sync_count': len(cta.get('gesture_sync', [])),
                'object_focus_count': len(cta.get('object_focus', []))
            },
            'size_kb': len(json.dumps(markers)) / 1024
        }
        
        return summary


def extract_temporal_markers(video_id: str, base_dir: str = '.') -> Dict[str, Any]:
    """
    Convenience function to extract temporal markers for a video.
    
    Args:
        video_id: Video identifier
        base_dir: Base directory for finding analysis outputs
        
    Returns:
        Integrated temporal markers
    """
    pipeline = TemporalMarkerPipeline(video_id, base_dir)
    return pipeline.extract_all_markers()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python temporal_marker_integration.py <video_id>")
        sys.exit(1)
        
    video_id = sys.argv[1]
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Extract markers
    pipeline = TemporalMarkerPipeline(video_id)
    markers = pipeline.extract_all_markers()
    
    # Save markers
    output_path = pipeline.save_markers(markers)
    
    # Print summary
    summary = pipeline.get_marker_summary(markers)
    print(f"\n✅ Temporal markers extracted for {video_id}")
    print(f"   First 5 seconds:")
    print(f"     - Text moments: {summary['first_5_seconds']['text_moments']}")
    print(f"     - Avg density: {summary['first_5_seconds']['density_avg']:.1f}")
    print(f"     - Emotions: {summary['first_5_seconds']['emotions']}")
    print(f"     - Gestures: {summary['first_5_seconds']['gesture_count']}")
    print(f"   CTA window ({summary['cta_window']['time_range']}):")
    print(f"     - CTAs: {summary['cta_window']['cta_count']}")
    print(f"     - Gesture sync: {summary['cta_window']['gesture_sync_count']}")
    print(f"   Total size: {summary['size_kb']:.1f}KB")
    print(f"   Saved to: {output_path}")