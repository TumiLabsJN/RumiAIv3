"""
Claude Temporal Integration Module
Handles integration of temporal markers into Claude API prompts
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ClaudeTemporalIntegration:
    """Integrates temporal markers into Claude prompts with feature flags"""
    
    def __init__(self, enable_temporal_markers: bool = True, 
                 rollout_percentage: float = 100.0,
                 config_path: Optional[str] = None):
        """
        Initialize temporal integration with feature flags
        
        Args:
            enable_temporal_markers: Master switch for temporal markers
            rollout_percentage: Percentage of prompts to include markers (0-100)
            config_path: Path to config file for feature flags
        """
        self.enable_temporal_markers = enable_temporal_markers
        self.rollout_percentage = rollout_percentage
        
        # Load config if provided
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
        
        # Temporal marker formatting options
        self.format_options = {
            'include_density': True,
            'include_emotions': True,
            'include_gestures': True,
            'include_objects': True,
            'include_cta': True,
            'compact_mode': False  # For smaller payloads
        }
        
    def _load_config(self, config_path: str):
        """Load feature flags from config file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            self.enable_temporal_markers = config.get('enable_temporal_markers', True)
            self.rollout_percentage = config.get('rollout_percentage', 100.0)
            self.format_options.update(config.get('format_options', {}))
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    def should_include_temporal_markers(self, video_id: str) -> bool:
        """
        Determine if temporal markers should be included for this video
        
        Args:
            video_id: Video ID for deterministic rollout
            
        Returns:
            bool: Whether to include temporal markers
        """
        if not self.enable_temporal_markers:
            return False
        
        # Use video_id hash for deterministic rollout
        hash_value = int(hash(video_id) & 0x7FFFFFFF)
        percentage_threshold = hash_value % 100
        
        return percentage_threshold < self.rollout_percentage
    
    def format_temporal_markers_for_claude(self, temporal_markers: Dict[str, Any],
                                         compact: Optional[bool] = None) -> str:
        """
        Format temporal markers for Claude's context window
        
        Args:
            temporal_markers: Raw temporal marker data
            compact: Override compact mode setting
            
        Returns:
            Formatted string for Claude prompt
        """
        if not temporal_markers:
            return ""
        
        compact_mode = compact if compact is not None else self.format_options['compact_mode']
        
        sections = []
        
        # Header
        sections.append("TEMPORAL PATTERN DATA:")
        sections.append("This data captures WHEN events happen in the video and their patterns over time.")
        sections.append("")
        
        # First 5 seconds analysis
        if 'first_5_seconds' in temporal_markers:
            sections.extend(self._format_first_5_seconds(
                temporal_markers['first_5_seconds'], 
                compact_mode
            ))
            sections.append("")
        
        # CTA window analysis
        if 'cta_window' in temporal_markers:
            sections.extend(self._format_cta_window(
                temporal_markers['cta_window'],
                compact_mode
            ))
            sections.append("")
        
        # Summary insights
        sections.append("KEY TEMPORAL INSIGHTS:")
        sections.extend(self._generate_temporal_insights(temporal_markers))
        
        return "\n".join(sections)
    
    def _format_first_5_seconds(self, first_5_data: Dict[str, Any], 
                                compact: bool = False) -> list:
        """Format first 5 seconds data"""
        lines = []
        lines.append("=== FIRST 5 SECONDS (Hook Window) ===")
        
        # Density progression
        if self.format_options['include_density'] and 'density_progression' in first_5_data:
            density = first_5_data['density_progression']
            if compact:
                lines.append(f"Activity Density: {density}")
            else:
                lines.append("Activity Density by Second:")
                for i, d in enumerate(density):
                    bar = "█" * int(d)
                    lines.append(f"  Second {i}: {bar} ({d} events)")
        
        # Text moments
        if 'text_moments' in first_5_data and first_5_data['text_moments']:
            lines.append("\nText Overlays:")
            for moment in first_5_data['text_moments'][:5]:  # Limit to top 5
                if compact:
                    lines.append(f"  {moment['time']}s: \"{moment['text']}\"")
                else:
                    size = moment.get('size', 'M')
                    pos = moment.get('position', 'center')
                    lines.append(f"  {moment['time']}s: \"{moment['text']}\" (size: {size}, pos: {pos})")
        
        # Emotions
        if self.format_options['include_emotions'] and 'emotion_sequence' in first_5_data:
            emotions = first_5_data['emotion_sequence']
            unique_emotions = len(set(emotions)) - 1  # Subtract 1 for neutral
            lines.append(f"\nEmotion Flow: {' → '.join(emotions)} ({unique_emotions} changes)")
        
        # Gestures
        if self.format_options['include_gestures'] and 'gesture_moments' in first_5_data:
            gestures = first_5_data['gesture_moments']
            if gestures:
                lines.append(f"\nKey Gestures: {len(gestures)} detected")
                for g in gestures[:3]:  # Top 3
                    target = f" at {g['target']}" if 'target' in g else ""
                    lines.append(f"  {g['time']}s: {g['gesture']}{target}")
        
        # Objects
        if self.format_options['include_objects'] and 'object_appearances' in first_5_data:
            objects = first_5_data['object_appearances']
            if objects:
                unique_objects = set()
                for obj_data in objects:
                    unique_objects.update(obj_data.get('objects', []))
                lines.append(f"\nObjects Shown: {', '.join(sorted(unique_objects))}")
        
        return lines
    
    def _format_cta_window(self, cta_data: Dict[str, Any], 
                          compact: bool = False) -> list:
        """Format CTA window data"""
        lines = []
        time_range = cta_data.get('time_range', 'last 15%')
        lines.append(f"=== CTA WINDOW ({time_range}) ===")
        
        # CTA appearances
        if self.format_options['include_cta'] and 'cta_appearances' in cta_data:
            ctas = cta_data['cta_appearances']
            if ctas:
                lines.append(f"\nCall-to-Actions: {len(ctas)} detected")
                for cta in ctas:
                    if compact:
                        lines.append(f"  {cta['time']}s: \"{cta['text']}\"")
                    else:
                        cta_type = cta.get('type', 'overlay')
                        lines.append(f"  {cta['time']}s: \"{cta['text']}\" (type: {cta_type})")
        
        # Gesture synchronization
        if 'gesture_sync' in cta_data and cta_data['gesture_sync']:
            lines.append(f"\nGesture-CTA Sync: {len(cta_data['gesture_sync'])} aligned gestures")
            for sync in cta_data['gesture_sync'][:2]:
                lines.append(f"  {sync['time']}s: {sync['gesture']} gesture")
        
        # Object focus
        if 'object_focus' in cta_data and cta_data['object_focus']:
            focus_objects = [f['object'] for f in cta_data['object_focus']]
            unique_focus = list(dict.fromkeys(focus_objects))  # Preserve order, remove dupes
            lines.append(f"\nFocus Objects: {', '.join(unique_focus[:3])}")
        
        return lines
    
    def _generate_temporal_insights(self, temporal_markers: Dict[str, Any]) -> list:
        """Generate high-level insights from temporal patterns"""
        insights = []
        
        # First 5 seconds insights
        if 'first_5_seconds' in temporal_markers:
            first_5 = temporal_markers['first_5_seconds']
            
            # Density insight
            density = first_5.get('density_progression', [])
            if density:
                avg_density = sum(density) / len(density)
                if avg_density > 3:
                    insights.append("- HIGH HOOK DENSITY: First 5s packed with activity (viral pattern)")
                elif avg_density >= 2:
                    insights.append("- MODERATE HOOK DENSITY: Good activity level in opening")
                elif avg_density < 1:
                    insights.append("- LOW HOOK DENSITY: Minimal activity in first 5s")
            
            # Early CTA detection
            text_moments = first_5.get('text_moments', [])
            has_early_cta = any(t.get('is_cta', False) for t in text_moments)
            # Also check for common CTA keywords
            for moment in text_moments:
                text_lower = moment.get('text', '').lower()
                if any(cta in text_lower for cta in ['follow', 'like', 'subscribe', 'buy', 'get', 'click', 'tap']):
                    has_early_cta = True
                    break
            if has_early_cta:
                insights.append("- EARLY CTA: Call-to-action in first 5 seconds (urgency pattern)")
            
            # Emotion changes
            emotions = first_5.get('emotion_sequence', [])
            emotion_changes = len(set(emotions)) - 1
            if emotion_changes >= 3:
                insights.append(f"- EMOTIONAL JOURNEY: {emotion_changes} emotion changes in first 5s")
        
        # CTA window insights
        if 'cta_window' in temporal_markers:
            cta = temporal_markers['cta_window']
            
            # CTA density
            cta_count = len(cta.get('cta_appearances', []))
            if cta_count > 2:
                insights.append(f"- MULTIPLE CTAS: {cta_count} CTAs in closing (high conversion focus)")
            
            # Gesture sync
            if cta.get('gesture_sync'):
                insights.append("- GESTURE-CTA SYNC: Physical gestures aligned with CTAs")
        
        if not insights:
            insights.append("- No significant temporal patterns detected")
        
        return insights
    
    def build_context_with_temporal_markers(self, 
                                          existing_context: Union[str, Dict[str, Any]],
                                          temporal_markers: Dict[str, Any],
                                          video_id: str) -> str:
        """
        Build complete context including temporal markers
        
        Args:
            existing_context: Original context data (string or dict)
            temporal_markers: Temporal marker data to include
            video_id: Video ID for rollout decision
            
        Returns:
            Complete context string for Claude
        """
        # Check if temporal markers should be included
        if not self.should_include_temporal_markers(video_id):
            # Return existing context as-is
            if isinstance(existing_context, dict):
                return f"CONTEXT DATA:\n{json.dumps(existing_context, indent=2)}"
            return existing_context
        
        # Format existing context
        if isinstance(existing_context, dict):
            context_str = f"CONTEXT DATA:\n{json.dumps(existing_context, indent=2)}"
        else:
            context_str = str(existing_context)
        
        # Format temporal markers
        temporal_str = self.format_temporal_markers_for_claude(temporal_markers)
        
        # Combine contexts
        if temporal_str:
            return f"{context_str}\n\n{temporal_str}"
        
        return context_str
    
    def get_prompt_size_estimate(self, context: str, prompt: str) -> Dict[str, Any]:
        """
        Estimate prompt size and provide warnings
        
        Returns:
            Dict with size info and warnings
        """
        total_size = len(context) + len(prompt)
        size_kb = total_size / 1024
        
        result = {
            'total_chars': total_size,
            'size_kb': size_kb,
            'warnings': []
        }
        
        if size_kb > 180:
            result['warnings'].append("Prompt exceeds 180KB - may cause API errors")
        elif size_kb > 150:
            result['warnings'].append("Prompt is large (>150KB) - consider compact mode")
        
        return result
    
    def save_rollout_config(self, config_path: str):
        """Save current rollout configuration"""
        config = {
            'enable_temporal_markers': self.enable_temporal_markers,
            'rollout_percentage': self.rollout_percentage,
            'format_options': self.format_options
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Saved temporal marker config to: {config_path}")


# Convenience functions for easy integration
def format_context_with_temporal_markers(existing_context: Union[str, Dict[str, Any]],
                                       temporal_markers: Dict[str, Any],
                                       video_id: str,
                                       enable: bool = True,
                                       rollout_percentage: float = 100.0) -> str:
    """
    Quick function to add temporal markers to existing context
    
    Args:
        existing_context: Original context
        temporal_markers: Temporal marker data
        video_id: Video ID for rollout
        enable: Whether to enable temporal markers
        rollout_percentage: Rollout percentage (0-100)
        
    Returns:
        Formatted context string
    """
    integrator = ClaudeTemporalIntegration(
        enable_temporal_markers=enable,
        rollout_percentage=rollout_percentage
    )
    
    return integrator.build_context_with_temporal_markers(
        existing_context, 
        temporal_markers, 
        video_id
    )