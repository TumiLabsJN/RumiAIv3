# Temporal Prompt Update Guide

## How to Write Effective Temporal-Aware Prompts

### 1. Understanding What's Available

With temporal markers, Claude now has access to:

```
TEMPORAL PATTERN DATA:
├── first_5_seconds/
│   ├── density_progression: [3, 2, 4, 1, 2]  # Events per second
│   ├── text_moments: [{time, text, size, position}]
│   ├── emotion_sequence: ['neutral', 'happy', 'surprise', ...]
│   ├── gesture_moments: [{time, gesture, target, confidence}]
│   └── object_appearances: [{time, objects, confidence}]
└── cta_window/
    ├── time_range: "12.75-15.0s"
    ├── cta_appearances: [{time, text, type}]
    ├── gesture_sync: [{time, gesture, aligns_with_cta}]
    └── object_focus: [{time, object, confidence}]
```

### 2. Key Principles for Temporal Prompts

#### A. Be Specific About Timing
❌ **Bad**: "Analyze what happens at the beginning"
✅ **Good**: "Analyze the density progression in the first 5 seconds and identify which specific seconds have the highest activity"

#### B. Reference Temporal Patterns
❌ **Bad**: "Look for engaging moments"
✅ **Good**: "Identify moments where density spikes (3+ events/second) and correlate with emotion changes"

#### C. Ask for Timestamp-Based Insights
❌ **Bad**: "When do CTAs appear?"
✅ **Good**: "List all CTAs with exact timestamps and analyze if they align with gesture moments"

#### D. Connect Multiple Markers
❌ **Bad**: "Analyze the emotions"
✅ **Good**: "Track how emotions change in relation to text appearances and identify synchronization patterns"

### 3. Prompt Templates by Use Case

#### Hook Analysis Template
```python
"""Analyze hook effectiveness using temporal density patterns.

Examine:
1. Density progression [X, Y, Z...] in first 5 seconds
2. Peak density moments and what causes them
3. Text appearances at specific timestamps (e.g., "WAIT" at 2.0s)
4. Emotion changes and their timing
5. How these patterns match known viral formulas

Provide specific timestamps and density values."""
```

#### Viral Pattern Discovery Template
```python
"""Identify viral patterns using temporal markers.

Look for:
1. "Wait for it" pattern: Text at ~2s → Reveal at ~7s
2. High-density openings: 4+ events in first 2 seconds
3. Emotional rollercoasters: 3+ emotion changes
4. CTA timing patterns: Early + Late combination

Rate viral potential based on pattern matches."""
```

#### Conversion Optimization Template
```python
"""Analyze CTA effectiveness through temporal data.

Focus on:
1. CTA window ({time_range}): List all CTAs with timestamps
2. Gesture synchronization: Which gestures align with CTAs?
3. Object focus during CTAs: What's visually prominent?
4. Density during CTA delivery: High or low activity?

Recommend timing optimizations for better conversion."""
```

### 4. Advanced Prompt Techniques

#### A. Pattern Matching Prompts
```python
"Compare this video's density progression {density_data} against these known viral patterns:
- Pattern A: [4, 3, 5, 2, 4] 
- Pattern B: [2, 3, 4, 5, 5]
Which pattern does it most closely match and why?"
```

#### B. Synchronization Analysis
```python
"Identify 'power moments' where 3+ temporal events align:
- Text appearance
- Emotion change  
- Gesture
- Density spike
List each power moment with its timestamp and impact."
```

#### C. Predictive Analysis
```python
"Based on the first 5 seconds temporal data:
- Density: {density}
- Emotions: {emotions}
- Text count: {text_count}
Predict the video's completion rate and explain why."
```

### 5. Common Patterns to Reference

Include these in prompts when relevant:

**Viral Temporal Formulas**:
- `Hook_Text(0-1s) + Tease(2s) + Reveal(5-8s) = Engagement`
- `High_Density(0-3s) + CTA(4s) + Payoff(7s) = Viral`
- `Emotion_Change(1s) + Gesture(1.5s) + Text(2s) = Attention`

**Density Patterns**:
- Viral: `[4+, 3+, 4+, ...]` (sustained high)
- Building: `[2, 3, 4, 5, ...]` (crescendo)
- Rhythmic: `[4, 2, 4, 2, ...]` (alternating)

**CTA Patterns**:
- Early hook: CTA in first 5s
- Late cluster: Multiple CTAs in final 15%
- Sandwich: Early + Late CTAs

### 6. Prompt Enhancement Examples

#### Original Prompt:
"Analyze what makes this video engaging"

#### Enhanced Temporal Prompt:
"Analyze engagement using temporal markers:

1. **Density Analysis**: How does the progression {density} maintain attention?
2. **First-Second Impact**: What happens at 0-1s that prevents scrolling?
3. **Emotion Journey**: Track {emotions} and identify engagement peaks
4. **CTA Timing**: Are CTAs placed at emotional highs?
5. **Pattern Matching**: Does this follow viral formula X + Y + Z?

Provide timestamps for all key moments."

### 7. Measuring Prompt Effectiveness

Track these metrics for temporal vs non-temporal prompts:

1. **Specificity Score**: Count timestamp references in response
2. **Pattern Identification**: Number of patterns discovered
3. **Actionability**: Specific timing recommendations given
4. **Accuracy**: Correctness of temporal references

### 8. Quick Reference Card

```
TEMPORAL PROMPT CHECKLIST:
□ Reference specific temporal markers (density, emotions, etc.)
□ Ask for exact timestamps
□ Include pattern matching against known formulas
□ Request synchronization analysis
□ Ask for timing-based recommendations
□ Connect multiple temporal dimensions
```

### 9. Do's and Don'ts

**DO**:
- ✅ Reference density_progression directly
- ✅ Ask for timestamp correlations
- ✅ Include known viral patterns
- ✅ Request specific second-by-second analysis
- ✅ Ask for synchronization insights

**DON'T**:
- ❌ Use vague timing words ("early", "later")
- ❌ Ignore the CTA window data
- ❌ Ask about data not in markers
- ❌ Forget to request timestamps
- ❌ Write prompts that ignore temporal data

### 10. Testing Your Prompts

Before deploying a new temporal prompt:

1. Check it references at least 2 temporal markers
2. Ensure it asks for specific timestamps
3. Verify it leverages unique temporal insights
4. Test with and without markers to see improvement
5. Measure response quality improvements

### Remember:
The goal is to transform Claude from a general analyst into a precision temporal pattern expert who can provide timestamp-specific, data-driven insights that directly improve video performance.