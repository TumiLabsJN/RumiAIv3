#!/usr/bin/env python3
"""
Update existing prompts to leverage temporal markers
Shows before/after examples and provides updated versions
"""

import json
from pathlib import Path
from prompts.temporal_aware_prompts import TemporalAwarePrompts


# Example existing prompts that could be enhanced
EXISTING_PROMPTS = {
    'hook_analysis': {
        'original': """Analyze the hook effectiveness in the first 3 seconds of this TikTok video. 
Consider what elements appear early to grab attention and how well they work.""",
        
        'enhanced': TemporalAwarePrompts.hook_effectiveness(),
        
        'key_improvements': [
            "Now references specific density progression data",
            "Asks for exact timestamps of elements",
            "Includes viral pattern matching",
            "Requests synchronization analysis"
        ]
    },
    
    'engagement_analysis': {
        'original': """Identify all engagement tactics used in this TikTok video. 
Focus on psychological triggers, visual techniques, and viewer retention strategies.""",
        
        'enhanced': TemporalAwarePrompts.engagement_tactics(),
        
        'key_improvements': [
            "Analyzes pacing through density patterns",
            "Tracks emotional journey with timestamps", 
            "Identifies CTA timing strategies",
            "Examines gesture-emotion synchronization"
        ]
    },
    
    'creative_density': {
        'original': """Analyze the creative density of this video. How many different creative 
elements are used and how frequently do they appear?""",
        
        'enhanced': """Analyze creative density using temporal density progression data.

Examine:
1. **Density Progression**: {density_progression}
   - Calculate average events per second
   - Identify peak density moments and their timestamps
   - Compare to viral video baselines (3+ events/sec)

2. **Density Distribution**:
   - First 5 seconds: How front-loaded is creativity?
   - Middle section: Sustained or dropping density?
   - CTA window: Final push density level?

3. **Element Stacking**:
   - When do multiple elements appear simultaneously?
   - Power moments: 3+ events at same timestamp
   - Synchronization patterns between elements

4. **Pacing Strategy**:
   - Constant high density vs rhythmic variation
   - Strategic "breathing room" (low density moments)
   - How density guides viewer attention

Provide specific density values and timestamps for all findings.""",
        
        'key_improvements': [
            "Uses actual density_progression data",
            "Provides quantitative density analysis",
            "Identifies temporal stacking patterns",
            "Analyzes pacing through density rhythm"
        ]
    },
    
    'emotional_journey': {
        'original': """Describe the emotional journey of the video and how it engages viewers 
emotionally throughout its duration.""",
        
        'enhanced': TemporalAwarePrompts.emotional_journey_mapping(),
        
        'key_improvements': [
            "Tracks exact emotion sequence with timestamps",
            "Calculates emotional velocity (changes/second)",
            "Correlates emotions with other events",
            "Maps emotion-to-conversion path"
        ]
    },
    
    'cta_effectiveness': {
        'original': """Analyze the calls-to-action in this video. Are they effective? 
How could they be improved?""",
        
        'enhanced': """Analyze CTA effectiveness using temporal CTA window data.

Focus on:
1. **CTA Timing Analysis**:
   - Early CTAs (first 5s): {list with timestamps}
   - CTA window CTAs (last 15%): {list with timestamps}
   - Total CTA density: CTAs per second

2. **Gesture-CTA Synchronization**:
   - Which CTAs have gesture alignment? (timestamp match)
   - Types of gestures used (pointing, beckoning, etc.)
   - Effectiveness of gesture-enhanced CTAs

3. **CTA Context**:
   - Emotion state during each CTA
   - Object focus during CTA delivery
   - Density level (high/low activity)

4. **CTA Progression**:
   - Soft → Hard ask progression?
   - Multiple action types? (Follow → Like → Share)
   - Timing between CTAs (avoiding fatigue)

5. **Optimization Opportunities**:
   - Missing CTA moments (emotion peaks without CTA)
   - Better gesture synchronization timing
   - Optimal CTA density based on patterns

Rate current CTA strategy (1-10) with specific timestamp-based improvements.""",
        
        'key_improvements': [
            "Analyzes exact CTA timestamps",
            "Measures gesture synchronization",
            "Tracks CTA context (emotion/objects)",
            "Provides timing-based optimizations"
        ]
    }
}


def show_prompt_evolution():
    """Show how prompts evolve with temporal awareness"""
    
    print("\n" + "="*80)
    print("📝 PROMPT EVOLUTION: From Basic to Temporal-Aware")
    print("="*80)
    
    for prompt_name, prompt_data in EXISTING_PROMPTS.items():
        print(f"\n\n🔄 {prompt_name.upper()}")
        print("-"*60)
        
        print("\n❌ ORIGINAL PROMPT:")
        print(prompt_data['original'])
        
        print("\n✅ ENHANCED TEMPORAL PROMPT:")
        # Show first 400 chars for brevity
        enhanced = prompt_data['enhanced']
        if len(enhanced) > 400:
            print(enhanced[:400] + "...\n[Full prompt contains detailed temporal analysis instructions]")
        else:
            print(enhanced)
        
        print("\n🎯 KEY IMPROVEMENTS:")
        for improvement in prompt_data['key_improvements']:
            print(f"  • {improvement}")


def generate_prompt_migration_plan():
    """Generate a plan for migrating existing prompts"""
    
    print("\n\n" + "="*80)
    print("📋 PROMPT MIGRATION PLAN")
    print("="*80)
    
    print("""
PHASE 1: High-Impact Prompts (Week 1)
--------------------------------------
1. hook_analysis → Temporal version
   - Most critical for viral success
   - Clear temporal patterns available
   
2. engagement_tactics → Temporal version  
   - Directly leverages density data
   - High value for optimization

3. cta_effectiveness → Temporal version
   - CTA window data is unique insight
   - Direct conversion impact

PHASE 2: Analysis Prompts (Week 2)
----------------------------------
4. creative_density → Temporal version
   - Natural fit for density progression
   - Quantitative improvements

5. emotional_journey → Temporal version
   - Emotion sequence data is powerful
   - Engagement insights

6. viral_patterns → New temporal prompt
   - Completely new capability
   - High value discovery

PHASE 3: Advanced Prompts (Week 3)
----------------------------------
7. pacing_analysis → New temporal prompt
   - Leverages density rhythms
   - Platform optimization

8. pattern_discovery → New temporal prompt
   - Cross-marker synchronization
   - Formula identification

9. Custom prompts → Temporal templates
   - Flexible prompt generation
   - Specific use cases
""")


def create_prompt_templates():
    """Create reusable prompt templates"""
    
    print("\n\n" + "="*80)
    print("🏗️ REUSABLE TEMPORAL PROMPT TEMPLATES")
    print("="*80)
    
    templates = {
        'density_analysis': """
[TASK]: Analyze [ASPECT] using density progression data.

Examine:
1. Density values: {density_progression}
2. Peak moments: When and why do spikes occur?
3. Patterns: Does this match known [PATTERN_TYPE] patterns?
4. Optimization: How could density be adjusted for [GOAL]?

Provide specific second-by-second analysis.
""",
        
        'timestamp_correlation': """
[TASK]: Identify when [EVENT_A] and [EVENT_B] occur together.

Analyze:
1. [EVENT_A] timestamps: {data_a}
2. [EVENT_B] timestamps: {data_b}  
3. Synchronization: Which events align within 0.5s?
4. Impact: What's the effect of synchronization?
5. Opportunities: Where could better alignment help?

List all correlations with exact timestamps.
""",
        
        'pattern_matching': """
[TASK]: Match this video against [PATTERN_NAME] pattern.

Pattern definition: [PATTERN_FORMULA]
Video data: {temporal_markers}

Check:
1. Does the video follow this pattern?
2. Where does it deviate? (timestamps)
3. How strong is the match? (1-10)
4. What adjustments would perfect the pattern?

Provide timestamp-specific analysis.
""",
        
        'temporal_optimization': """
[TASK]: Optimize [METRIC] using temporal data.

Current state:
- Density: {density_progression}
- Key moments: {text_moments, gesture_moments}
- Performance: [CURRENT_METRIC]

Recommend:
1. Specific timestamp adjustments
2. Element additions/removals with timing
3. Density modifications by second
4. Expected improvement: X% → Y%

Focus on actionable, timestamp-based changes.
"""
    }
    
    for template_name, template in templates.items():
        print(f"\n📄 {template_name.upper()} TEMPLATE:")
        print(template)


def show_prompt_testing_framework():
    """Show how to test temporal prompts"""
    
    print("\n\n" + "="*80)
    print("🧪 TESTING TEMPORAL PROMPTS")
    print("="*80)
    
    print("""
1. QUALITY METRICS FOR TEMPORAL PROMPTS
---------------------------------------
Track these in responses:

✓ Timestamp Density: # of specific timestamps mentioned
✓ Pattern Recognition: # of temporal patterns identified  
✓ Synchronization Insights: # of multi-marker correlations
✓ Actionability Score: # of time-specific recommendations
✓ Precision Level: Exact times vs vague references

Example Scoring:
- Non-temporal response: 2 timestamps, 0 patterns, vague
- Temporal response: 15+ timestamps, 4 patterns, precise

2. A/B TESTING FRAMEWORK
-----------------------
For each prompt type:

A. Run both versions on same video
B. Compare:
   - Insight specificity
   - Discovery count
   - Actionability
   - User value

C. Track improvement:
   - Average 40-60% more specific insights
   - 3-5x more timestamps referenced
   - 2-3x more patterns discovered

3. PROMPT EFFECTIVENESS RUBRIC
-----------------------------
Rate each temporal prompt (1-5):

□ Leverages unique temporal data
□ Requests specific timestamps  
□ Identifies patterns/formulas
□ Provides timing-based recommendations
□ Connects multiple markers

Score 20+ = Excellent temporal prompt
Score 15-19 = Good, needs refinement
Score <15 = Needs significant improvement
""")


def main():
    print("\n🚀 TEMPORAL PROMPT UPDATE SYSTEM")
    print("Transforming existing prompts to leverage temporal markers")
    
    # Show how prompts evolve
    show_prompt_evolution()
    
    # Migration planning
    generate_prompt_migration_plan()
    
    # Template library
    create_prompt_templates()
    
    # Testing framework
    show_prompt_testing_framework()
    
    print("\n\n" + "="*80)
    print("💡 NEXT STEPS")
    print("="*80)
    print("""
1. Review existing prompts in your system
2. Identify which ones analyze timing/pacing/engagement
3. Use templates to create temporal versions
4. Test with real videos containing temporal markers
5. Measure improvement in insight quality
6. Gradually migrate based on impact

Remember: Not all prompts need temporal awareness, but those analyzing
engagement, virality, pacing, or optimization will see dramatic improvements.
""")


if __name__ == "__main__":
    main()