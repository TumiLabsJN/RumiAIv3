"""
Temporal-Aware Prompts for Claude
Prompts optimized to leverage temporal marker data for better insights
"""

from typing import Dict, Any, Optional


class TemporalAwarePrompts:
    """Collection of prompts that leverage temporal markers"""
    
    @staticmethod
    def hook_effectiveness() -> str:
        """Analyze hook effectiveness using temporal patterns"""
        return """Analyze the hook effectiveness of this TikTok video using the temporal pattern data.

Focus on:

1. **First 2 Seconds Analysis**:
   - What specific elements appear at each timestamp?
   - How does the density progression indicate urgency or excitement?
   - Are there any "pattern interrupt" moments that grab attention?

2. **Density Patterns**:
   - Look at the density progression [Second 0: X events, Second 1: Y events, etc.]
   - Identify if this follows viral patterns (high early density = strong hook)
   - Does the density maintain viewer attention or drop off?

3. **Text-Emotion-Gesture Synchronization**:
   - When text appears (e.g., "WAIT FOR IT" at 0.5s), what emotions/gestures accompany it?
   - Are CTAs placed strategically in the first 5 seconds?
   - How do visual elements reinforce the hook message?

4. **Viral Pattern Recognition**:
   - Does this match known viral patterns like:
     * "Wait for it" at 2s → payoff at 7s
     * High density (3+ events/second) in first 3 seconds
     * Emotion change within first 2 seconds
   - Rate the hook strength (1-10) based on temporal patterns

Provide specific timestamps and explain how the timing contributes to effectiveness."""
    
    @staticmethod
    def engagement_tactics() -> str:
        """Identify engagement tactics through temporal analysis"""
        return """Identify and analyze engagement tactics in this TikTok video using temporal markers.

Examine:

1. **Pacing and Rhythm**:
   - How does the density progression create viewing rhythm?
   - Are there strategic "breathing room" moments (low density)?
   - When do activity peaks occur and why?

2. **CTA Timing Strategy**:
   - Early CTAs (first 5s): Are they present? What's their purpose?
   - CTA window CTAs: How many appear in the final 15%?
   - Is there gesture synchronization with CTAs (pointing at "Follow" button)?

3. **Emotional Journey Mapping**:
   - Track the emotion sequence: [neutral → happy → surprise → ...]
   - How many emotion changes occur? When?
   - Do emotion peaks align with key messages or CTAs?

4. **Object Focus Patterns**:
   - What objects appear when? (person at 0s, product at 2s, etc.)
   - During the CTA window, what's in focus?
   - How does object progression support the narrative?

5. **Retention Mechanics**:
   - Identify "curiosity gaps" created by temporal patterns
   - When are reveals timed? (e.g., answer to "wait for it")
   - How does pacing prevent scroll-away?

For each tactic, provide:
- Specific timestamps
- Why the timing is effective
- How it influences viewer behavior"""
    
    @staticmethod
    def viral_pattern_discovery() -> str:
        """Discover viral patterns through temporal analysis"""
        return """Analyze this video for viral content patterns using temporal marker data.

Search for:

1. **Known Viral Temporal Patterns**:
   - "Hook → Tease → Payoff" timing (e.g., tease at 2s, payoff at 7s)
   - "Rapid-fire opening" (4+ events in first 2 seconds)
   - "Emotional rollercoaster" (3+ emotion changes)
   - "CTA sandwich" (early CTA + final CTA burst)

2. **Density Signatures**:
   - Does the density progression match viral videos?
     * High start (3+ events/sec) → maintain → spike at end
     * Rhythmic pattern (high-low-high-low)
   - Calculate average density and compare to viral baseline

3. **Text Moment Patterns**:
   - Common viral text timings:
     * Challenge/question at 0-1s
     * "Wait for it" or similar at 2-3s
     * Answer/reveal at 5-8s
     * CTA cluster at 85-95% duration
   - Which patterns are present here?

4. **Gesture-Emotion Synchronization**:
   - Pointing gestures aligned with key moments?
   - Surprise emotions timed with reveals?
   - Happy emotions during CTA delivery?

5. **Unique Patterns**:
   - Identify any unusual but effective temporal patterns
   - Could these be new viral mechanics?
   - What makes the timing work?

Rate virality potential (1-10) based on temporal pattern matching.
Explain which specific patterns contribute most to viral potential."""
    
    @staticmethod
    def conversion_optimization() -> str:
        """Analyze conversion optimization through CTA timing"""
        return """Analyze conversion optimization strategies using temporal markers, focusing on the CTA window.

Investigate:

1. **CTA Window Analysis** (last 15% of video):
   - List all CTAs with exact timestamps
   - What's the CTA density? (CTAs per second)
   - Are CTAs clustered or spread out?

2. **Gesture-CTA Alignment**:
   - Which gestures appear during CTAs?
   - Is there pointing/tapping synchronized with "Follow" or "Like"?
   - How does body language reinforce the CTA?

3. **Object Focus During CTAs**:
   - What's visually prominent during each CTA?
   - Is the creator's face visible (trust building)?
   - Are products/results shown (social proof)?

4. **CTA Preparation**:
   - How does the first 85% prepare for conversion?
   - When is value demonstrated vs. CTA requested?
   - Is there an emotional peak before the CTA window?

5. **Multi-CTA Strategy**:
   - If multiple CTAs exist, what's the progression?
     * Soft ask → Hard ask?
     * Different actions requested?
   - How does timing prevent CTA fatigue?

6. **Early CTA Analysis**:
   - Any CTAs in first 5 seconds? Why?
   - How do early CTAs differ from closing CTAs?

Provide specific recommendations for improving conversion based on temporal patterns.
What timing adjustments could increase conversion rates?"""
    
    @staticmethod
    def content_pacing_analysis() -> str:
        """Analyze content pacing using density patterns"""
        return """Analyze the content pacing and rhythm using temporal density patterns.

Examine:

1. **Density Progression Analysis**:
   - Map the density curve: [3, 2, 4, 1, 2, ...]
   - Identify rhythm patterns (steady, building, alternating)
   - Where are the peaks and valleys? Why?

2. **Pacing Strategies**:
   - Fast start (high density) vs. slow build?
   - Are there "rest moments" (low density) for processing?
   - How does pacing match content type?

3. **Viewer Attention Management**:
   - When does density spike to regain attention?
   - Are there patterns like: setup (low) → payoff (high)?
   - How long are sustained high-density periods?

4. **Content Type Alignment**:
   - Tutorial: Does pacing allow learning?
   - Entertainment: Are surprises well-timed?
   - Product showcase: When are features revealed?

5. **Platform Optimization**:
   - Is pacing optimized for TikTok's swipe behavior?
   - Does first-second density prevent immediate swipe?
   - Is final-second density high to prevent early exit?

6. **Comparative Analysis**:
   - How does this pacing compare to viral videos?
   - What's unique about this pacing strategy?
   - Could pacing be improved? How?

Create a "pacing map" showing:
- Density over time
- Key moments and their timing
- Suggested optimizations"""
    
    @staticmethod
    def emotional_journey_mapping() -> str:
        """Map emotional journey using temporal emotion data"""
        return """Map the emotional journey of this video using temporal emotion markers.

Analyze:

1. **Emotion Sequence Timeline**:
   - Track emotions second by second: [neutral → happy → surprise → ...]
   - Count total emotion changes
   - Calculate "emotional velocity" (changes per second)

2. **Emotion-Content Correlation**:
   - What triggers each emotion change?
   - Do emotions align with:
     * Text reveals?
     * Visual surprises?
     * Music/sound cues?

3. **Emotional Arc Patterns**:
   - Rising action: neutral → curious → excited?
   - Rollercoaster: happy → sad → happy?
   - Climax timing: When does peak emotion occur?

4. **Engagement Through Emotion**:
   - Which emotions dominate the first 5 seconds?
   - Are negative emotions used strategically?
   - How do emotions prime viewers for CTAs?

5. **Gesture-Emotion Synchronization**:
   - Do gestures amplify emotions?
   - When do gesture and emotion peaks align?
   - Is there intentional contrast?

6. **Emotional Conversion Path**:
   - What emotion immediately precedes CTAs?
   - Is there an "optimal conversion emotion"?
   - How does the emotional journey lead to action?

Create an emotional journey visualization showing:
- Emotion timeline with changes marked
- Correlation with key content moments
- Effectiveness rating for engagement"""
    
    @staticmethod
    def pattern_discovery_advanced() -> str:
        """Advanced pattern discovery across all temporal markers"""
        return """Perform advanced pattern discovery using ALL temporal markers to identify success formulas.

Investigate:

1. **Cross-Marker Synchronization**:
   - When do text + emotion + gesture align?
   - Are there "power moments" with 3+ simultaneous events?
   - What patterns emerge from synchronization?

2. **Temporal Formulas**:
   - Identify repeatable patterns like:
     * Text(0.5s) + Gesture(1s) + Emotion_change(1.5s) = Hook
     * High_density(0-3s) + CTA(4s) + Payoff(7s) = Viral
   - Which formulas appear in this video?

3. **Micro-Pattern Analysis**:
   - Sub-second patterns (multiple events <1s apart)
   - Gesture-to-gesture transitions
   - Text appearance rhythms

4. **Comparative Pattern Matching**:
   - How do patterns compare to known viral videos?
   - What's unique about this video's patterns?
   - Are there innovative timing strategies?

5. **Predictive Patterns**:
   - Based on first 5 seconds, what patterns predict:
     * High completion rate?
     * Strong engagement?
     * Conversion likelihood?

6. **Pattern Strength Scoring**:
   - Rate each identified pattern (1-10)
   - Which patterns are strongest?
   - What's missing that could improve performance?

Deliver:
- List of all discovered patterns with timestamps
- Strength rating for each pattern
- Recommendations for pattern optimization
- Potential new patterns to test"""
    
    @staticmethod
    def get_prompt(prompt_type: str) -> Optional[str]:
        """Get a specific temporal-aware prompt"""
        prompts = {
            'hook_effectiveness': TemporalAwarePrompts.hook_effectiveness(),
            'engagement_tactics': TemporalAwarePrompts.engagement_tactics(),
            'viral_patterns': TemporalAwarePrompts.viral_pattern_discovery(),
            'conversion_optimization': TemporalAwarePrompts.conversion_optimization(),
            'content_pacing': TemporalAwarePrompts.content_pacing_analysis(),
            'emotional_journey': TemporalAwarePrompts.emotional_journey_mapping(),
            'pattern_discovery': TemporalAwarePrompts.pattern_discovery_advanced()
        }
        return prompts.get(prompt_type)
    
    @staticmethod
    def create_custom_prompt(focus_area: str, specific_patterns: list) -> str:
        """Create a custom temporal-aware prompt"""
        base = f"""Analyze this video's {focus_area} using temporal marker data.

Focus specifically on these temporal patterns:
"""
        for pattern in specific_patterns:
            base += f"- {pattern}\n"
        
        base += """
For each pattern:
1. Identify if/when it occurs (exact timestamps)
2. Evaluate its effectiveness
3. Suggest optimizations based on timing

Use the temporal marker data to provide specific, timestamp-based insights."""
        
        return base


# Prompt templates for different insight types
TEMPORAL_PROMPT_TEMPLATES = {
    'hook_analysis': {
        'description': 'Analyze hook effectiveness using temporal patterns',
        'requires_markers': ['first_5_seconds', 'density_progression'],
        'focus': 'First 5 seconds density and progression'
    },
    'cta_strategy': {
        'description': 'Analyze CTA placement and timing strategies',
        'requires_markers': ['cta_window', 'gesture_sync'],
        'focus': 'CTA timing and gesture alignment'
    },
    'viral_mechanics': {
        'description': 'Identify viral content patterns through timing',
        'requires_markers': ['density_progression', 'emotion_sequence'],
        'focus': 'Temporal patterns matching viral formulas'
    },
    'pacing_optimization': {
        'description': 'Optimize content pacing using density data',
        'requires_markers': ['density_progression'],
        'focus': 'Rhythm and viewer attention management'
    },
    'emotional_engagement': {
        'description': 'Map emotional journey for maximum engagement',
        'requires_markers': ['emotion_sequence', 'gesture_moments'],
        'focus': 'Emotion timing and transitions'
    }
}