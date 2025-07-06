#!/usr/bin/env python3
"""
Update unified analysis with all available data
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def update_unified_analysis(video_id):
    """Update unified analysis with all available data sources"""
    
    unified_path = Path(f'unified_analysis_{video_id}.json')
    if not unified_path.exists():
        print(f"❌ Unified analysis not found: {unified_path}")
        return False
    
    # Load existing unified analysis
    with open(unified_path, 'r') as f:
        unified = json.load(f)
    
    print(f"📋 Updating unified analysis for {video_id}")
    
    # 1. Load TikTok metadata
    metadata_paths = [
        f'temp/tiktok_profiles/{video_id}_metadata.json',
        f'outputs/tiktok_profiles/{video_id}_metadata.json'
    ]
    
    for path in metadata_paths:
        if Path(path).exists():
            with open(path, 'r') as f:
                metadata = json.load(f)
                
            # Update static metadata
            unified['static_metadata'] = {
                'captionText': metadata.get('text', ''),
                'hashtags': [h['name'] for h in metadata.get('hashtags', []) if h.get('name')],
                'duration': metadata.get('videoMeta', {}).get('duration', 0),
                'createTime': metadata.get('createTimeISO'),
                'author': metadata.get('authorMeta', {}),
                'stats': {
                    'views': metadata.get('playCount', 0),
                    'likes': metadata.get('diggCount', 0),
                    'comments': metadata.get('commentCount', 0),
                    'shares': metadata.get('shareCount', 0),
                    'saves': metadata.get('collectCount', 0),
                    'engagementRate': (metadata.get('diggCount', 0) / max(metadata.get('playCount', 1), 1)) * 100
                },
                'music': metadata.get('musicMeta', {})
            }
            
            # Update video info
            video_meta = metadata.get('videoMeta', {})
            unified['video_info'] = {
                'width': video_meta.get('width', 0),
                'height': video_meta.get('height', 0),
                'duration': video_meta.get('duration', 0),
                'format': video_meta.get('format', 'mp4')
            }
            
            print("   ✅ Updated with TikTok metadata")
            break
    
    # 2. Load local analysis
    analysis_path = Path(f'downloads/analysis/{video_id}/complete_analysis.json')
    if not analysis_path.exists():
        analysis_path = Path(f'downloads/analysis/{video_id}/basic_analysis.json')
    
    if analysis_path.exists():
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
        
        # Merge timelines
        if 'timelines' in analysis:
            for timeline_type, timeline_data in analysis['timelines'].items():
                if timeline_data:  # Only add non-empty timelines
                    unified['timelines'][timeline_type] = timeline_data
        
        # Add analysis metadata
        unified['local_analysis'] = {
            'type': analysis.get('analysis_type', 'unknown'),
            'timestamp': analysis.get('analysis_timestamp'),
            'frames_extracted': len(analysis.get('extracted_frames', [])),
            'audio_extracted': bool(analysis.get('audio_path'))
        }
        
        print("   ✅ Updated with local analysis")
    
    # 3. Load PySceneDetect results if available
    scene_path = Path(f'downloads/analysis/{video_id}/scene_detection.json')
    if scene_path.exists():
        with open(scene_path, 'r') as f:
            scenes = json.load(f)
        
        # Add scene detection timeline
        if 'scenes' in scenes:
            unified['timelines']['sceneChangeTimeline'] = process_scene_changes(scenes['scenes'])
        
        unified['scene_detection'] = {
            'analyzed': True,
            'timestamp': scenes.get('timestamp'),
            'scene_count': len(scenes.get('scenes', []))
        }
        
        print("   ✅ Updated with PySceneDetect results")
    
    # 4. Load enhanced human analyzer data if available
    enhanced_path = Path(f'downloads/analysis/{video_id}/enhanced_human_analysis.json')
    if enhanced_path.exists():
        with open(enhanced_path, 'r') as f:
            enhanced = json.load(f)
        
        # Merge enhanced timelines
        if 'timelines' in enhanced:
            for timeline_type, timeline_data in enhanced['timelines'].items():
                if timeline_data:
                    unified['timelines'][timeline_type] = timeline_data
        
        unified['enhanced_analysis'] = {
            'analyzed': True,
            'timestamp': enhanced.get('analysis_timestamp'),
            'mediapipe_version': enhanced.get('mediapipe_version'),
            'frames_processed': enhanced.get('frames_processed', 0)
        }
        
        print("   ✅ Updated with enhanced human analysis")
    
    # 5. Calculate insights
    unified['insights'] = calculate_insights(unified)
    
    # 6. Update metadata
    unified['last_updated'] = datetime.now().isoformat()
    unified['data_sources'] = {
        'tiktok_metadata': bool(unified.get('static_metadata', {}).get('author')),
        'local_analysis': 'local_analysis' in unified,
        'scene_detection': 'scene_detection' in unified,
        'enhanced_analysis': 'enhanced_analysis' in unified
    }
    
    # Save updated unified analysis
    with open(unified_path, 'w') as f:
        json.dump(unified, f, indent=2)
    
    print(f"✅ Unified analysis updated: {unified_path}")
    return True


def process_scene_changes(scenes):
    """Convert scene detection results to timeline format"""
    timeline = {}
    for i, scene in enumerate(scenes):
        start_time = scene.get('start_time', 0)
        end_time = scene.get('end_time', start_time + 1)
        time_key = f"{start_time:.1f}-{end_time:.1f}s"
        timeline[time_key] = {
            'scene_number': i + 1,
            'start_time': start_time,
            'end_time': end_time,
            'duration': scene.get('duration', end_time - start_time),
            'transition_type': scene.get('transition_type', 'cut')
        }
    return timeline


def calculate_insights(unified):
    """Calculate insights from all available data"""
    insights = {
        'primaryObjects': [],
        'dominantExpressions': [],
        'creativeDensity': 0,
        'gestureCount': 0,
        'textOverlayFrequency': 0,
        'humanPresenceRate': 0,
        'objectDiversity': 0,
        'sceneComplexity': 0,
        'engagementIndicators': [],
        'timelineStats': {}
    }
    
    timelines = unified.get('timelines', {})
    duration = unified.get('duration_seconds', 1)
    
    # Timeline statistics
    insights['timelineStats'] = {
        'textOverlayCount': len(timelines.get('textOverlayTimeline', {})),
        'objectDetectionCount': len(timelines.get('objectTimeline', {})),
        'gestureCount': len(timelines.get('gestureTimeline', {})),
        'expressionCount': len(timelines.get('expressionTimeline', {})),
        'speechSegmentCount': len(timelines.get('speechTimeline', {})),
        'stickerCount': len(timelines.get('stickerTimeline', {})),
        'sceneChangeCount': len(timelines.get('sceneChangeTimeline', {}))
    }
    
    # Count objects from object timeline
    object_counts = {}
    for timestamp, data in timelines.get('objectTimeline', {}).items():
        objects = data.get('objects', []) if isinstance(data, dict) else []
        for obj in objects:
            if isinstance(obj, dict):
                obj_name = obj.get('class', obj.get('object', 'unknown'))
                object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
    
    # Get top objects
    if object_counts:
        sorted_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        insights['primaryObjects'] = [obj[0] for obj in sorted_objects[:5]]
        insights['objectDiversity'] = len(object_counts)
    
    # Count expressions
    expression_counts = {}
    for timestamp, data in timelines.get('expressionTimeline', {}).items():
        if isinstance(data, dict) and 'expressions' in data:
            for expr in data['expressions']:
                if isinstance(expr, dict):
                    expr_name = expr.get('expression', 'neutral')
                    expression_counts[expr_name] = expression_counts.get(expr_name, 0) + 1
    
    if expression_counts:
        sorted_expressions = sorted(expression_counts.items(), key=lambda x: x[1], reverse=True)
        insights['dominantExpressions'] = [expr[0] for expr in sorted_expressions[:3]]
    
    # Calculate frequencies
    insights['textOverlayFrequency'] = insights['timelineStats']['textOverlayCount'] / max(duration, 1)
    insights['gestureCount'] = insights['timelineStats']['gestureCount']
    
    # Calculate creative density (elements per second)
    total_elements = (
        insights['timelineStats']['textOverlayCount'] +
        insights['timelineStats']['objectDetectionCount'] +
        insights['timelineStats']['gestureCount'] +
        insights['timelineStats']['stickerCount']
    )
    insights['creativeDensity'] = total_elements / max(duration, 1)
    
    # Scene complexity
    insights['sceneComplexity'] = insights['timelineStats']['sceneChangeCount'] / max(duration, 1)
    
    # Human presence rate (simplified - based on person detections and expressions)
    human_indicators = (
        insights['timelineStats']['expressionCount'] +
        object_counts.get('person', 0)
    )
    insights['humanPresenceRate'] = min(human_indicators / max(duration, 1), 1.0)
    
    # Engagement indicators based on available data
    engagement_indicators = []
    
    # High text overlay frequency might indicate engagement tactics
    if insights['textOverlayFrequency'] > 0.5:
        engagement_indicators.append('high_text_overlay_frequency')
    
    # Multiple expressions suggest emotional engagement
    if len(insights['dominantExpressions']) > 2:
        engagement_indicators.append('diverse_expressions')
    
    # Frequent scene changes might indicate dynamic content
    if insights['sceneComplexity'] > 0.3:
        engagement_indicators.append('dynamic_scene_changes')
    
    # High creative density suggests engaging content
    if insights['creativeDensity'] > 1.0:
        engagement_indicators.append('high_creative_density')
    
    insights['engagementIndicators'] = engagement_indicators
    
    return insights


def main():
    if len(sys.argv) != 2:
        print("Usage: python update_unified_analysis.py <video_id>")
        sys.exit(1)
    
    video_id = sys.argv[1]
    
    success = update_unified_analysis(video_id)
    
    if success:
        print("\n✅ Unified analysis update completed successfully")
    else:
        print("\n❌ Unified analysis update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()