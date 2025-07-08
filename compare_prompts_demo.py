#!/usr/bin/env python3
"""
Demonstrate the difference between regular and temporal-aware prompts
Shows how temporal markers enable more specific, actionable insights
"""

import json
from pathlib import Path
from prompts.temporal_aware_prompts import TemporalAwarePrompts, TEMPORAL_PROMPT_TEMPLATES


def show_prompt_comparison():
    """Show side-by-side comparison of prompts"""
    
    print("\n" + "="*80)
    print("🔍 PROMPT COMPARISON: Regular vs Temporal-Aware")
    print("="*80)
    
    # Example 1: Hook Analysis
    print("\n📌 HOOK ANALYSIS COMPARISON")
    print("-"*40)
    
    print("\n❌ WITHOUT Temporal Markers (Traditional Prompt):")
    print("""
Analyze the hook effectiveness in the first 3 seconds of this TikTok video.
Consider what elements appear early to grab attention and how well they work.
Look at text overlays, visual elements, and any surprise factors.
""")
    
    print("\n✅ WITH Temporal Markers (Temporal-Aware Prompt):")
    print(TemporalAwarePrompts.hook_effectiveness()[:600] + "...")
    
    # Example 2: What Claude can see
    print("\n\n📊 WHAT CLAUDE SEES:")
    print("-"*40)
    
    print("\n❌ WITHOUT Temporal Markers:")
    print("""
CONTEXT DATA:
{
  "video_stats": {"views": 1000000, "likes": 150000},
  "duration": 15,
  "captions": "Wait for the incredible transformation! 🤯"
}

ANALYSIS REQUEST:
Analyze the hook effectiveness...
""")
    
    print("\n✅ WITH Temporal Markers:")
    print("""
CONTEXT DATA:
{
  "video_stats": {"views": 1000000, "likes": 150000},
  "duration": 15,
  "captions": "Wait for the incredible transformation! 🤯"
}

TEMPORAL PATTERN DATA:
=== FIRST 5 SECONDS (Hook Window) ===
Activity Density by Second:
  Second 0: ████ (4 events)
  Second 1: ███ (3 events)
  Second 2: █████ (5 events) 
  Second 3: ██ (2 events)
  Second 4: ███ (3 events)

Text Overlays:
  0.5s: "You won't believe" (size: L, pos: center)
  2.0s: "WAIT FOR IT" (size: XL, pos: center)
  4.5s: "Ready?" (size: M, pos: bottom)

Emotion Flow: neutral → curious → excited → surprise → happy (4 changes)

Key Gestures: 3 detected
  1.0s: pointing at object
  2.5s: hands_up (excitement)
  4.0s: beckoning

=== CTA WINDOW (12.75-15.0s) ===
Call-to-Actions: 2 detected
  13.0s: "Follow for more!" (type: overlay)
  14.5s: "Try this yourself →" (type: gesture+text)

Gesture-CTA Sync: 1 aligned gestures
  14.5s: pointing gesture

KEY TEMPORAL INSIGHTS:
- HIGH HOOK DENSITY: First 5s packed with activity (viral pattern)
- EARLY CTA: Call-to-action in first 5 seconds (urgency pattern)
- GESTURE-CTA SYNC: Physical gestures aligned with CTAs

ANALYSIS REQUEST:
Analyze the hook effectiveness...
""")


def show_insight_differences():
    """Show how insights differ with temporal markers"""
    
    print("\n\n" + "="*80)
    print("💡 INSIGHT QUALITY COMPARISON")
    print("="*80)
    
    print("\n🎯 Question: 'When does the video grab attention?'")
    print("-"*40)
    
    print("\n❌ WITHOUT Temporal Markers (Claude's response):")
    print("""
"The video appears to grab attention early with its caption mentioning a 
transformation. Based on the high view count, the hook seems effective, 
likely using visual or text elements in the opening moments."

⚠️ LIMITATIONS:
- No specific timestamps
- Guessing about "likely" elements
- Cannot identify exact pattern
- Generic advice
""")
    
    print("\n✅ WITH Temporal Markers (Claude's response):")
    print("""
"The video grabs attention through a carefully orchestrated sequence:

1. **0.5s**: Large text 'You won't believe' creates immediate curiosity
2. **1.0s**: Pointing gesture directs attention to key element  
3. **2.0s**: 'WAIT FOR IT' in XL text - classic viral pattern
4. **2.5s**: Hands_up gesture + emotion shift to excitement
5. **Peak at 2s**: 5 simultaneous events create maximum stimulation

This follows the viral 'curiosity gap' formula with peak density at the 
2-second mark, exactly when viewers typically decide to keep watching."

✅ ADVANTAGES:
- Exact timestamps for every element
- Identifies specific viral patterns
- Explains WHY timing works
- Actionable for replication
""")


def show_pattern_discovery():
    """Show pattern discovery capabilities"""
    
    print("\n\n" + "="*80)
    print("🔬 PATTERN DISCOVERY COMPARISON")
    print("="*80)
    
    print("\n❓ Task: 'Identify viral content patterns'")
    print("-"*40)
    
    print("\n❌ WITHOUT Temporal Markers:")
    print("""
Patterns Claude might identify:
- Uses transformation content (based on caption)
- Has high engagement rate (15% like ratio)
- Short format (15 seconds)
- Includes emoji in caption

⚠️ Cannot identify:
- Timing patterns
- Density signatures  
- Emotion progressions
- Gesture synchronization
""")
    
    print("\n✅ WITH Temporal Markers:")
    print("""
Viral patterns Claude can now identify:

1. **"Wait For It" Pattern** (2s tease → 7s reveal):
   - Text "WAIT FOR IT" at exactly 2.0s
   - Density drops 3→2 creating anticipation
   - Reveal spike at 7s with emotion change

2. **High-Density Hook** (4+ events in first 2s):
   - Second 0: 4 events
   - Second 2: 5 events (peak)
   - Matches top 10% viral videos

3. **Emotional Rollercoaster** (4 changes in 15s):
   - neutral → curious (0.5s) 
   - curious → excited (2.5s)
   - excited → surprise (7s)
   - surprise → happy (13s)

4. **CTA-Gesture Sync** (14.5s):
   - "Try this yourself" + pointing gesture
   - Increases conversion by ~40% based on patterns

Success Formula Discovered:
High_Density_Open(0-2s) + Wait_Pattern(2s) + Emotion_Peak(7s) + 
Gesture_CTA(14.5s) = Viral_Potential_Score: 8.7/10
""")


def show_actionable_insights():
    """Show how temporal markers make insights actionable"""
    
    print("\n\n" + "="*80)
    print("🎬 ACTIONABLE INSIGHTS COMPARISON")
    print("="*80)
    
    print("\n📝 Task: 'How to improve this video?'")
    print("-"*40)
    
    print("\n❌ WITHOUT Temporal Markers:")
    print("""
Suggestions:
- Add more engaging text in the beginning
- Include a stronger call-to-action
- Create more surprise moments
- Improve pacing

⚠️ Problems:
- When exactly to add text?
- Where to place the CTA?
- When should surprises occur?
- How to improve pacing specifically?
""")
    
    print("\n✅ WITH Temporal Markers:")
    print("""
Specific improvements based on temporal analysis:

1. **Optimize Second 3** (Currently only 2 events):
   - Add emotion change here (excited → anticipation)
   - Include progress indicator text "3...2...1..."
   - Target: Increase to 4 events matching seconds 0 and 2

2. **Add Early Soft CTA** (Gap at 4-5s):
   - Place "Follow to see result" at 4.5s
   - Sync with beckoning gesture
   - Maintains 15% early-CTA viral pattern

3. **Enhance CTA Window** (Currently 2 CTAs):
   - Add third CTA at 13.5s: "Save to try later"
   - Create CTA cascade: Follow → Save → Try
   - Add object focus on result during CTAs

4. **Smooth Density Valley** (Second 3):
   - Current: [4,3,5,2,3] - jarring drop
   - Target: [4,3,5,3,3] - smoother flow
   - Prevents attention loss at critical moment

Expected improvements:
- Completion rate: +12-15% (smoother density)
- Conversion rate: +20-25% (optimized CTAs)
- Viral potential: 8.7 → 9.2/10
""")


def list_available_prompts():
    """List all available temporal-aware prompts"""
    
    print("\n\n" + "="*80)
    print("📚 AVAILABLE TEMPORAL-AWARE PROMPTS")
    print("="*80)
    
    prompts = {
        'hook_effectiveness': 'Analyze hook effectiveness using temporal patterns',
        'engagement_tactics': 'Identify engagement tactics through temporal analysis',
        'viral_patterns': 'Discover viral patterns through temporal analysis',
        'conversion_optimization': 'Analyze conversion optimization through CTA timing',
        'content_pacing': 'Analyze content pacing using density patterns',
        'emotional_journey': 'Map emotional journey using temporal emotion data',
        'pattern_discovery': 'Advanced pattern discovery across all temporal markers'
    }
    
    for key, description in prompts.items():
        print(f"\n{key}:")
        print(f"  {description}")
        if key in TEMPORAL_PROMPT_TEMPLATES:
            template = TEMPORAL_PROMPT_TEMPLATES[key]
            print(f"  Requires: {', '.join(template['requires_markers'])}")
            print(f"  Focus: {template['focus']}")


def main():
    print("\n🚀 TEMPORAL-AWARE PROMPTS DEMONSTRATION")
    print("This shows how temporal markers transform Claude's analysis capabilities")
    
    # Show comparisons
    show_prompt_comparison()
    show_insight_differences()
    show_pattern_discovery()
    show_actionable_insights()
    list_available_prompts()
    
    print("\n\n" + "="*80)
    print("🎯 KEY BENEFITS OF TEMPORAL-AWARE PROMPTS")
    print("="*80)
    print("""
1. **Specificity**: Exact timestamps instead of vague timing
2. **Pattern Recognition**: Identifies complex temporal formulas
3. **Actionability**: Precise recommendations with timing
4. **Virality Analysis**: Matches against known viral patterns
5. **Optimization**: Data-driven improvements based on density
6. **Synchronization**: Detects multi-modal alignment (text+gesture+emotion)
7. **Predictive Power**: First 5s patterns predict video success

With temporal markers, Claude transforms from a general advisor to a
precision analyst who can reverse-engineer viral mechanics and provide
timestamp-specific optimization strategies.
""")


if __name__ == "__main__":
    main()