#!/usr/bin/env python3
"""
Interactive Training Workshop for Temporal Markers
Teaches team members how to interpret and use temporal data
"""

import json
import time
from typing import Dict, Any


def display_section(title: str, content: str):
    """Display a training section"""
    print("\n" + "="*80)
    print(f"📚 {title}")
    print("="*80)
    print(content)
    input("\nPress Enter to continue...")


def interactive_exercise(title: str, question: str, answer: str):
    """Run an interactive exercise"""
    print("\n" + "-"*60)
    print(f"🎯 EXERCISE: {title}")
    print("-"*60)
    print(f"\n{question}")
    
    user_input = input("\nYour answer (or press Enter to see solution): ")
    
    print("\n✅ SOLUTION:")
    print(answer)
    
    if user_input:
        print(f"\n💭 Your answer: {user_input}")
    input("\nPress Enter to continue...")


def run_workshop():
    """Run the temporal markers training workshop"""
    
    print("\n" + "🎓 TEMPORAL MARKERS TRAINING WORKSHOP 🎓".center(80))
    print("="*80)
    print("Welcome to the interactive training for temporal markers!")
    print("This workshop will teach you how to interpret and use temporal data.")
    input("\nPress Enter to begin...")
    
    # Module 1: Understanding Temporal Markers
    display_section(
        "MODULE 1: What Are Temporal Markers?",
        """
Temporal markers capture WHEN events happen in videos with precision:

📊 Key Components:
1. **Density Progression**: Events per second [3, 2, 4, 1, 2]
2. **Text Moments**: {time: 0.5s, text: "WAIT FOR IT", size: "L"}
3. **Emotion Sequence**: ['neutral', 'happy', 'surprise', ...]
4. **Gesture Moments**: {time: 1.5s, gesture: "pointing", target: "product"}
5. **CTA Window**: Last 15% of video with conversion elements

🎯 Why It Matters:
- Traditional: "The video has good pacing"
- With Markers: "Density peaks at 2s with 5 events, creating viral hook"

💡 Key Insight: We now see the video's timeline like a musical score,
with every beat precisely mapped.
"""
    )
    
    # Exercise 1
    interactive_exercise(
        "Interpreting Density",
        """
Given this density progression: [1, 2, 5, 2, 3]

What can you conclude about the video's pacing strategy?
Consider: Hook strength, attention patterns, viral potential
""",
        """
This shows a "building crescendo" pattern:
- Second 0-1: Low density (1-2 events) - soft opening
- Second 2: Peak density (5 events) - attention spike  
- Second 3-4: Moderate (2-3 events) - sustained engagement

This is a STRONG viral pattern because:
1. Peak at 2s matches when viewers decide to keep watching
2. 5 events create maximum stimulation at critical moment
3. Post-peak sustains interest without overwhelming

Viral potential: HIGH (8/10)
"""
    )
    
    # Module 2: Pattern Recognition
    display_section(
        "MODULE 2: Recognizing Viral Patterns",
        """
🔍 Common Temporal Patterns in Viral Videos:

1. **"Wait For It" Pattern**:
   - Marker: Text "wait/watch" at 2-3s
   - Density: Drop after tease, spike at reveal
   - Example: [3, 4, 2, 1, 1, 3, 5] with text at 2s

2. **"Rapid Fire Hook"**:
   - Marker: 4+ events in first 2 seconds
   - Density: [4, 5, 3, ...]
   - Success rate: 73% higher completion

3. **"Emotional Rollercoaster"**:
   - Marker: 3+ emotion changes
   - Sequence: neutral → curious → excited → surprise
   - Engagement: 2.5x average

4. **"CTA Sandwich"**:
   - Marker: Early CTA (3-5s) + Late CTAs (85-100%)
   - Pattern: Soft ask → Content → Hard ask
   - Conversion: 40% higher

🎯 Pattern Matching Formula:
If density[2] > 4 AND text contains "wait" AND emotions > 2 changes
Then: Viral_Score += 3
"""
    )
    
    # Exercise 2
    interactive_exercise(
        "Pattern Identification",
        """
You see this temporal data:
- Density: [4, 3, 5, 1, 1, 2, 6]
- Text at 2.0s: "You won't believe this"
- Text at 6.5s: "BOOM!"
- Emotions: neutral → curious → neutral → neutral → shocked

Which viral pattern(s) does this match?
""",
        """
This matches TWO viral patterns:

1. ✅ "Wait For It" Pattern:
   - Tease text at 2s ("You won't believe")
   - Density drops (5→1→1) creating anticipation
   - Payoff spike at 6s (density: 6) with "BOOM!"
   
2. ✅ Modified "Rapid Fire Hook":
   - First 3 seconds average: 4 events/sec
   - Qualifies as high-density opening

Missing: Emotional Rollercoaster (only 2 changes, need 3+)

Overall: STRONG viral potential using proven patterns
"""
    )
    
    # Module 3: Writing Temporal Prompts
    display_section(
        "MODULE 3: Writing Effective Temporal Prompts",
        """
📝 Temporal Prompt Formula:

1. **Reference Specific Data**:
   ❌ "Analyze the beginning"
   ✅ "Analyze density progression [3,2,4,1,2] in first 5 seconds"

2. **Request Timestamps**:
   ❌ "When do CTAs appear?"
   ✅ "List all CTAs with exact timestamps from the cta_window data"

3. **Connect Multiple Markers**:
   ❌ "Look at emotions"
   ✅ "Correlate emotion changes with text appearances and density spikes"

4. **Pattern Matching**:
   ❌ "Is this viral?"
   ✅ "Does this match the 'Wait For It' pattern (tease@2s → reveal@7s)?"

🎯 Template Structure:
"[ANALYZE WHAT] using [SPECIFIC MARKER DATA].
[SPECIFIC QUESTIONS WITH TIMING].
[PATTERN TO CHECK].
Provide [TIMESTAMP-BASED OUTPUT]."
"""
    )
    
    # Exercise 3
    interactive_exercise(
        "Write a Temporal Prompt",
        """
Task: Write a prompt to analyze CTA effectiveness

Available data:
- cta_window: {time_range: "12.75-15s", cta_appearances: [...]}
- gesture_sync: [{time: 14.5s, gesture: "pointing"}]
- Emotion during CTA window: "happy"

Write a temporal-aware prompt:
""",
        """
Example temporal-aware prompt:

"Analyze CTA effectiveness using the cta_window temporal data.

Examine:
1. CTA density in the 12.75-15s window - how many CTAs per second?
2. At 14.5s, there's a pointing gesture - does this align with a CTA?
3. The emotion is 'happy' during CTAs - is this optimal for conversion?
4. Compare the number of CTAs to viral patterns (2-3 CTAs optimal)

For each CTA:
- Provide exact timestamp
- Note if gesture-synchronized
- Rate effectiveness (1-10)
- Suggest timing optimization

Does this follow the 'CTA Sandwich' pattern with early + late CTAs?"
"""
    )
    
    # Module 4: Interpreting Results
    display_section(
        "MODULE 4: Interpreting Temporal Insights",
        """
🔬 How to Read Claude's Temporal Analysis:

1. **Timestamp Specificity**:
   - Good: "At 2.3s, density peaks with text appearance"
   - Better: "At 2.3s, 5 simultaneous events create attention spike"

2. **Pattern Recognition**:
   - Look for: "This matches [pattern] because [temporal evidence]"
   - Example: "Viral 'Wait' pattern confirmed: text@2s, reveal@7.2s"

3. **Synchronization Insights**:
   - Key finding: "Gesture + Emotion + Text align at 4.5s"
   - Impact: "Triple synchronization increases engagement 3x"

4. **Optimization Recommendations**:
   - Specific: "Move CTA from 13s to 12.5s to align with gesture"
   - Measurable: "Increase density at second 3 from 2→4 events"

⚡ Quality Checklist:
□ 10+ specific timestamps mentioned
□ 2+ patterns identified
□ Synchronization moments noted
□ Density values referenced
□ Timing-based improvements suggested
"""
    )
    
    # Module 5: Advanced Applications
    display_section(
        "MODULE 5: Advanced Temporal Analysis",
        """
🚀 Advanced Techniques:

1. **Multi-Video Pattern Discovery**:
   - Compare density signatures across videos
   - Identify winning formulas: [4,3,5,2,3] = viral
   - Build pattern library

2. **Predictive Analysis**:
   - First 5s density > 3.5 avg → 85% completion likely
   - 3+ emotion changes → 2.5x engagement rate
   - Early CTA + gesture → 40% higher conversion

3. **Optimization Algorithms**:
   - Smooth density valleys: [4,2,5,1,4] → [4,3,5,3,4]
   - Align events: Move text 0.5s to sync with gesture
   - Balance distribution: Spread 15 events optimally

4. **A/B Testing with Temporal Data**:
   Version A: [3,2,4,1,2] = 45% completion
   Version B: [4,3,3,3,3] = 62% completion
   Insight: Consistent density beats spikes

5. **Custom Pattern Creation**:
   Your brand pattern: Text(1s) + Product(2s) + CTA(4s)
   Test variations: ±0.5s adjustments
   Find optimal timing
"""
    )
    
    # Exercise 4: Practical Application
    interactive_exercise(
        "Real-World Application",
        """
Your video has:
- Current density: [2, 1, 3, 1, 2]
- Text "Check this out" at 3s
- No gestures in first 5s
- Single CTA at 14s
- Completion rate: 35%

Using temporal patterns, what 3 specific changes would you recommend?
""",
        """
Recommended changes based on temporal patterns:

1. **Boost Opening Density** (Seconds 0-2):
   - Current: [2, 1, ...] - too weak
   - Target: [4, 3, ...] - viral baseline
   - Add: Text overlay at 0.5s + gesture at 1s
   
2. **Implement "Wait For It" Pattern**:
   - Move "Check this out" to 2s (prime spot)
   - Add reveal/payoff at 6-7s with density spike
   - Create anticipation gap (low density 3-5s)

3. **Add CTA Sandwich**:
   - Early soft CTA at 4s: "Follow to see more"
   - Keep final CTA at 14s but add gesture sync
   - Add middle CTA at 10s for momentum

Expected improvement:
- Completion: 35% → 55-60%
- Density pattern: [4,3,3,1,1,2,5] (viral signature)
- 3 strategic CTAs with gesture alignment
"""
    )
    
    # Module 6: Best Practices
    display_section(
        "MODULE 6: Best Practices & Tips",
        """
✅ DO's:
1. Always check density_progression first - it's your roadmap
2. Look for synchronization moments (2+ events within 0.5s)
3. Compare against known viral patterns
4. Provide specific timestamps in recommendations
5. Consider the full journey (first 5s → middle → CTA window)

❌ DON'Ts:
1. Don't ignore low-density moments - they serve a purpose
2. Don't overstuff (>5 events/second is too much)
3. Don't place CTAs during density valleys
4. Don't forget emotion-action alignment
5. Don't analyze without checking temporal markers

🏆 Pro Tips:
- The 2-second mark is GOLDEN - most decisions happen here
- Emotion changes are 2x more powerful than static emotions
- Gesture-CTA sync increases conversion by 40% average
- First impression density (0-1s) predicts completion
- CTA window density should match or exceed opening

💡 Remember:
Temporal markers transform video analysis from art to science.
Every second counts, and now we can count what's in every second!
"""
    )
    
    # Completion
    print("\n" + "="*80)
    print("🎉 WORKSHOP COMPLETE! 🎉".center(80))
    print("="*80)
    print("""
You've learned:
✅ How to interpret temporal markers
✅ Recognize viral patterns in data
✅ Write effective temporal prompts
✅ Analyze results for insights
✅ Apply patterns for optimization

Next steps:
1. Practice with real video temporal data
2. Build your own pattern library
3. Test improvements with A/B studies
4. Share discoveries with the team

Remember: With temporal markers, you're not just analyzing videos—
you're reverse-engineering viral mechanics with scientific precision!
""")


def quick_reference():
    """Display quick reference card"""
    print("\n" + "="*80)
    print("📋 TEMPORAL MARKERS QUICK REFERENCE")
    print("="*80)
    print("""
DENSITY PATTERNS:
[4,3,5,2,3] = Viral signature
[2,3,4,5,6] = Building crescendo  
[5,5,5,5,5] = Sustained high (risky)
[4,2,4,2,4] = Rhythmic engagement

VIRAL FORMULAS:
Wait Pattern: Text(2s) + Low_density(3-5s) + Spike(6-7s)
Rapid Hook: Density ≥4 in first 2 seconds
Emotion Ride: 3+ changes in 15 seconds
CTA Sandwich: Early(3-5s) + Late(85-100%)

KEY TIMESTAMPS:
0-1s: First impression (prevent swipe)
2s: Decision point (keep watching?)
5s: Engagement checkpoint
7s: Common payoff timing
50%: Mid-point re-engagement
85%+: CTA window begins

SYNCHRONIZATION POWER:
Text + Gesture = 2x impact
Emotion + CTA = 1.5x conversion
3+ simultaneous = "Power moment"

PROMPT CHECKLIST:
□ Reference density_progression
□ Ask for exact timestamps
□ Include pattern matching
□ Request synchronization analysis
□ Connect multiple markers
""")


def main():
    print("\n🎓 TEMPORAL MARKERS TRAINING SYSTEM")
    print("="*80)
    print("1. Run Full Workshop (30 mins)")
    print("2. Quick Reference Card")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        run_workshop()
        print("\nWould you like the quick reference card? (y/n)")
        if input().lower() == 'y':
            quick_reference()
    elif choice == "2":
        quick_reference()
    else:
        print("\nThank you for learning about temporal markers!")


if __name__ == "__main__":
    main()