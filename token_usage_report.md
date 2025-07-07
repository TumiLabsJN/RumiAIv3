# Token Usage Report for 66-Second Video Analysis

## Video Information
- **Video ID**: 7367449043070356782
- **Duration**: 66 seconds
- **Unified Analysis File**: 907,395 bytes (887 KB)

## Timeline Data Breakdown
The unified analysis contains:
- **Object Timeline**: 662 entries (largest dataset)
- **Speech Timeline**: 121 entries
- **Expression Timeline**: 119 entries
- **Gesture Timeline**: 51 entries
- **Scene Change Timeline**: 11 entries
- **Text Overlay Timeline**: 9 entries
- **Sticker Timeline**: 2 entries
- **Total Timeline Entries**: 975

## Actual Token Usage by Prompt

Based on the actual prompt files sent to Claude API:

| Prompt | File Size | Estimated Tokens |
|--------|-----------|-----------------|
| emotional_journey | 80,788 bytes (78.8 KB) | ~20,197 tokens |
| speech_analysis | 63,145 bytes (61.6 KB) | ~15,786 tokens |
| visual_overlay_analysis | 20,884 bytes (20.3 KB) | ~5,221 tokens |
| creative_density | 17,315 bytes (16.9 KB) | ~4,329 tokens |
| person_framing | 15,992 bytes (15.6 KB) | ~3,998 tokens |
| metadata_analysis | 13,534 bytes (13.2 KB) | ~3,384 tokens |
| scene_pacing | 10,421 bytes (10.1 KB) | ~2,605 tokens |
| **TOTAL** | **222,079 bytes (216.8 KB)** | **~55,520 tokens** |

## Key Observations

1. **Data Compression**: The system implements smart compression strategies:
   - Object timeline (662 entries) is compressed to ~30 entries for person_framing and scene_pacing
   - Computed metrics are sent instead of raw timelines for creative_density
   - Verbose descriptions are removed from object detection data

2. **Largest Prompts**:
   - **emotional_journey** (78.8 KB): Includes full expression, gesture, and speech timelines
   - **speech_analysis** (61.6 KB): Contains full transcript and speech segments
   - These two prompts account for 65% of total token usage

3. **Efficiency Measures**:
   - The creative_density prompt receives computed metrics instead of raw timelines
   - Object timeline compression saves ~95% of data for person_framing prompt
   - JSON is sent in compact format (no extra whitespace)

4. **Token Estimation**:
   - Using conservative estimate: 1 token ≈ 4 characters
   - Actual Claude tokenization may vary
   - Total estimated: **~55,520 tokens** across all 7 prompts
   - Average per prompt: ~7,931 tokens

## Cost Implications
- Each prompt includes both the template instructions and the context data
- The system processes videos with smart batching and compression
- Large videos (>60 seconds with rich object detection) require careful data management
- The 662 object timeline entries would have been ~180KB uncompressed but are reduced to ~10KB when compressed

## Recommendations for Token Optimization
1. Continue using computed metrics where possible
2. Implement adaptive compression based on timeline size
3. Consider sampling strategies for very long videos
4. Cache intermediate computations to avoid redundant processing