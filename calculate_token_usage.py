#!/usr/bin/env python3
"""
Calculate estimated token usage for the 66-second video analysis
"""

import json
import os

def estimate_tokens(text):
    """Rough estimation: 1 token ≈ 4 characters (conservative estimate for JSON)"""
    if isinstance(text, int):
        return text / 4
    return len(text) / 4

def analyze_prompt_sizes():
    """Analyze the data sizes sent to each prompt"""
    
    # Load the unified analysis
    video_id = "7367449043070356782"
    unified_path = f"unified_analysis/{video_id}.json"
    
    with open(unified_path, 'r') as f:
        unified_data = json.load(f)
    
    # Extract timelines
    timelines = unified_data.get('timelines', {})
    metadata_summary = unified_data.get('metadata_summary', {})
    static_metadata = unified_data.get('static_metadata', {})
    
    print(f"=== Video Analysis Token Estimation ===")
    print(f"Video ID: {video_id}")
    print(f"Duration: {unified_data.get('duration_seconds', 0)} seconds")
    print(f"Unified analysis file size: {len(json.dumps(unified_data)):,} characters")
    print(f"\nTimeline entry counts:")
    for name, timeline in timelines.items():
        if isinstance(timeline, dict):
            print(f"  {name}: {len(timeline)} entries")
    
    # Simulate what each prompt receives
    prompts_data = {}
    
    # 1. Creative Density - Receives computed metrics only
    print("\n\n1. CREATIVE DENSITY PROMPT")
    creative_data = {
        'video_id': video_id,
        'mode': 'labeling',
        # Simulated metrics (not full computation)
        'average_density': 2.5,
        'max_density': 8,
        'total_creative_elements': 975,
        'element_distribution': {'text': 9, 'sticker': 2, 'effect': 0, 'transition': 0, 'object': 662, 'gesture': 51, 'expression': 119},
        'density_curve': [{'second': i, 'density': 2, 'primary_element': 'object'} for i in range(66)],
        'peak_density_moments': [{'timestamp': f"{i}-{i+1}s", 'element_count': 5, 'surprise_score': 1.2} for i in range(10)],
        'multi_modal_peaks': [{'timestamp': f"{i}-{i+1}s", 'elements': ['text', 'object', 'gesture'], 'syncType': 'reinforcing'} for i in range(20)],
        # Add other metrics fields as computed
        'structural_patterns': {'strong_opening_hook': True, 'crescendo_pattern': False},
        'ml_tags': ['text_driven', 'multi_peak'],
        'data_completeness': 0.95,
        'overall_confidence': 0.90
    }
    creative_json = json.dumps(creative_data, separators=(',', ':'))
    prompts_data['creative_density'] = len(creative_json)
    print(f"Payload size: {len(creative_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(creative_json)):,}")
    
    # 2. Emotional Journey - Includes metrics + raw timelines
    print("\n2. EMOTIONAL JOURNEY PROMPT")
    emotional_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'emotional_metrics': {
            'dominant_emotions': ['neutral', 'contemplative'],
            'emotional_changes': 15,
            'stability_score': 0.75,
            # Simulated metrics
        },
        'expression_timeline': timelines.get('expressionTimeline', {}),
        'gesture_timeline': timelines.get('gestureTimeline', {}),
        'speech_timeline': timelines.get('speechTimeline', {}),
        'camera_distance_timeline': timelines.get('cameraDistanceTimeline', {}),
        'transcript': metadata_summary.get('transcript', '')[:1000],  # Truncated
        'speech_segments': metadata_summary.get('speechSegments', [])[:50]
    }
    emotional_json = json.dumps(emotional_data, separators=(',', ':'))
    prompts_data['emotional_journey'] = len(emotional_json)
    print(f"Payload size: {len(emotional_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(emotional_json)):,}")
    
    # 3. Speech Analysis
    print("\n3. SPEECH ANALYSIS PROMPT")
    speech_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'speech_analysis_metrics': {
            'words_per_minute': 120,
            'speech_coverage': 0.85,
            # Simulated metrics
        },
        'speech_timeline': timelines.get('speechTimeline', {}),
        'transcript': metadata_summary.get('transcript', ''),
        'word_count': metadata_summary.get('wordCount', 0),
        'speech_segments': metadata_summary.get('speechSegments', []),
        'expression_timeline': timelines.get('expressionTimeline', {}),
        'camera_distance_timeline': timelines.get('cameraDistanceTimeline', {})
    }
    speech_json = json.dumps(speech_data, separators=(',', ':'))
    prompts_data['speech_analysis'] = len(speech_json)
    print(f"Payload size: {len(speech_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(speech_json)):,}")
    
    # 4. Visual Overlay Analysis
    print("\n4. VISUAL OVERLAY ANALYSIS PROMPT")
    visual_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'visual_overlay_metrics': {
            'avg_texts_per_second': 0.14,
            'unique_text_count': 8,
            # Computed metrics
        },
        'textOverlayTimeline': timelines.get('textOverlayTimeline', {}),
        'stickerTimeline': timelines.get('stickerTimeline', {}),
        'gestureTimeline': timelines.get('gestureTimeline', {}),
        'speechTimeline': {},  # Empty for this prompt
        'frame_dimensions': {'width': 1080, 'height': 1920}
    }
    visual_json = json.dumps(visual_data, separators=(',', ':'))
    prompts_data['visual_overlay_analysis'] = len(visual_json)
    print(f"Payload size: {len(visual_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(visual_json)):,}")
    
    # 5. Metadata Analysis
    print("\n5. METADATA ANALYSIS PROMPT")
    metadata_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'metadata_metrics': {
            'hashtag_count': 8,
            'caption_length': 385,
            # Computed metrics
        },
        'static_metadata': {
            'videoId': video_id,
            'duration': 66,
            'createTime': static_metadata.get('createTime', ''),
            'captionText': static_metadata.get('captionText', '')[:500],
            'hashtags': static_metadata.get('hashtags', [])[:10]
        },
        'videoStats': static_metadata.get('stats', {}),
        'authorStats': static_metadata.get('author', {}),
        'emoji_count': 4,
        'emoji_list': ['📣', '💪'],
        'mention_count': 0,
        'link_present': False,
        'language_code': 'en',
        'video_duration': 66,
        'view_count': 3400000,
        'like_count': 319200,
        'engagement_rate': 13.07,
        'readability_score': 65.0,
        'sentiment_analysis': {'category': 'neutral', 'confidence': 0.7},
        'keyword_extraction': ['body', 'muscle', 'weight', 'training', 'healthy'],
        'entity_recognition': {'has_brand_mention': False, 'has_price_mention': False, 'has_cta': False}
    }
    metadata_json = json.dumps(metadata_data, separators=(',', ':'))
    prompts_data['metadata_analysis'] = len(metadata_json)
    print(f"Payload size: {len(metadata_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(metadata_json)):,}")
    
    # 6. Person Framing - Includes compressed object timeline
    print("\n6. PERSON FRAMING PROMPT")
    # Simulate compressed object timeline (30 entries max)
    compressed_object_timeline = {}
    object_entries = list(timelines.get('objectTimeline', {}).items())[:30]
    for timestamp, data in object_entries:
        if isinstance(data, dict):
            compressed_object_timeline[timestamp] = {
                'total_objects': data.get('total_objects', 1),
                'class_names': ['person', 'face']  # Simplified
            }
    
    person_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'person_framing_metrics': {
            'human_presence_ratio': 0.95,
            'average_face_size': 0.25,
            # Computed metrics
        },
        'camera_distance_timeline': {},
        'object_timeline': compressed_object_timeline,
        'expression_timeline': timelines.get('expressionTimeline', {}),
        'person_timeline': {},
        'timeline_summary': {
            'total_frames': 119,
            'object_detection_frames': 662,
            'expression_count': 119
        }
    }
    person_json = json.dumps(person_data, separators=(',', ':'))
    prompts_data['person_framing'] = len(person_json)
    print(f"Payload size: {len(person_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(person_json)):,}")
    print(f"Note: Object timeline compressed from {len(timelines.get('objectTimeline', {}))} to {len(compressed_object_timeline)} entries")
    
    # 7. Scene Pacing
    print("\n7. SCENE PACING PROMPT")
    scene_data = {
        'video_id': video_id,
        'mode': 'labeling',
        'scene_pacing_metrics': {
            'total_scenes': 11,
            'average_scene_duration': 6.0,
            'pacing_category': 'moderate',
            # Computed metrics
        },
        'scene_timeline': timelines.get('sceneChangeTimeline', {}),
        'object_timeline': compressed_object_timeline,  # Also compressed
        'camera_distance_timeline': {}
    }
    scene_json = json.dumps(scene_data, separators=(',', ':'))
    prompts_data['scene_pacing'] = len(scene_json)
    print(f"Payload size: {len(scene_json):,} characters")
    print(f"Estimated tokens: {int(estimate_tokens(scene_json)):,}")
    
    # Load prompt templates to get their sizes
    print("\n\n=== PROMPT TEMPLATE SIZES ===")
    prompt_templates = [
        'creative_density', 'emotional_journey', 'speech_analysis',
        'visual_overlay_analysis', 'metadata_analysis', 'person_framing', 'scene_pacing'
    ]
    
    template_sizes = {}
    for prompt_name in prompt_templates:
        template_path = f'prompt_templates/{prompt_name}.txt'
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template_text = f.read()
                template_sizes[prompt_name] = len(template_text)
                print(f"{prompt_name}: {len(template_text):,} characters ({int(estimate_tokens(template_text)):,} tokens)")
    
    # Calculate totals
    print("\n\n=== TOTAL TOKEN USAGE SUMMARY ===")
    total_data_chars = 0
    total_template_chars = 0
    total_tokens = 0
    
    print(f"{'Prompt':<25} {'Data Size':<15} {'Template Size':<15} {'Total Chars':<15} {'Est. Tokens':<15}")
    print("-" * 90)
    
    for prompt_name in prompt_templates:
        data_size = prompts_data.get(prompt_name, 0)
        template_size = template_sizes.get(prompt_name, 0)
        total_size = data_size + template_size
        tokens = int(estimate_tokens(total_size))
        
        total_data_chars += data_size
        total_template_chars += template_size
        total_tokens += tokens
        
        print(f"{prompt_name:<25} {data_size:>14,} {template_size:>14,} {total_size:>14,} {tokens:>14,}")
    
    print("-" * 90)
    print(f"{'TOTALS':<25} {total_data_chars:>14,} {total_template_chars:>14,} {total_data_chars + total_template_chars:>14,} {total_tokens:>14,}")
    
    print(f"\n\n=== FINAL ANALYSIS ===")
    print(f"Total estimated tokens sent to Claude API: {total_tokens:,}")
    print(f"Average tokens per prompt: {total_tokens // 7:,}")
    print(f"\nBreakdown:")
    print(f"  - Context data: {int(estimate_tokens(total_data_chars)):,} tokens ({total_data_chars:,} chars)")
    print(f"  - Prompt templates: {int(estimate_tokens(total_template_chars)):,} tokens ({total_template_chars:,} chars)")
    print(f"\nNotes:")
    print(f"  - This is a conservative estimate (1 token ≈ 4 characters)")
    print(f"  - Actual token count may vary based on Claude's tokenizer")
    print(f"  - The object timeline (662 entries) is compressed to ~30 entries for person_framing and scene_pacing")
    print(f"  - Each prompt also includes system messages and formatting overhead")

if __name__ == "__main__":
    analyze_prompt_sizes()