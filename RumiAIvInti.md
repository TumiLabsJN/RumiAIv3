# RumiAI v2 Integration Requirements

## Overview
This document outlines what's needed for `rumiai_runner.py` to have all the ML features from `Testytest_improved.md`, including the precomputed insight pipeline and proper FPS handling.

## Current State Analysis

### 🔴 Major Missing Components

#### 1. **Precompute Functions Integration**
The Python runner currently uses simple `MLDataExtractor` methods instead of the sophisticated precompute functions from `run_video_prompts_validated_v2.py`.

**Missing Functions:**
- `compute_creative_density_analysis` - 49 metrics including:
  - Density curves, volatility patterns
  - Multi-modal peak detection
  - Cognitive load categorization
- `compute_emotional_metrics` - 40 metrics including:
  - Emotion progression tracking
  - Gesture-emotion alignment
  - Audio-emotion synchronization
- `compute_person_framing_metrics` - 11 metrics including:
  - Framing quality scores
  - Position stability analysis
  - Gesture clarity assessment
- `compute_scene_pacing_metrics` - 31 metrics including:
  - Rhythm regularity
  - Pacing momentum
  - Cut intensity analysis
- `compute_speech_analysis_metrics` - 30 metrics including:
  - Speech-gesture synchronization
  - Pause pattern analysis
  - Emphasis detection
- `compute_visual_overlay_metrics` - 40 metrics including:
  - Overlay density measures
  - Text-speech synchronization
  - Visual complexity scoring
- `compute_metadata_analysis_metrics` - 45 metrics including:
  - Viral potential scoring
  - Hook detection
  - CTA identification

#### 2. **6-Block Output Structure**
The Python runner doesn't use or expect the standardized 6-block structure that Claude should output:

1. **CoreMetrics** - Basic measurements and counts
2. **Dynamics** - Temporal changes and progressions
3. **Interactions** - Element relationships and synchronization
4. **KeyEvents** - Specific moments and occurrences
5. **Patterns** - Recurring behaviors and strategies
6. **Quality** - Data confidence and completeness

#### 3. **Structured Data Input**
Currently sends basic ML data. Needs to build the specific context structure with:
- Precomputed metrics (from functions above)
- Raw timelines for validation
- Metadata and unified_analysis
- Proper field mapping

#### 4. **FPS Logic**
Missing critical FPS handling:
- Initial video metadata extraction with FPS
- FPS registry/context management
- Consistent FPS propagation through pipeline
- Proper frame-to-timestamp conversions

**Required FPS contexts:**
- Original video FPS (e.g., 30fps)
- Frame extraction FPS (typically 1fps)
- Analysis-specific FPS (varies by service)
- Scene detection FPS (uses original)

### ✅ What's Already Working

1. **Temporal Markers**
   - Fully integrated via `TemporalMarkerProcessor`
   - Generates markers after unified analysis
   - Working correctly - DO NOT modify

2. **7 ML Prompts**
   - All prompts are called through `_run_claude_prompts`
   - Correct order and naming

3. **Unified Timeline**
   - Created properly by `TimelineBuilder`
   - Validated and structured

4. **Claude Integration**
   - Has working `ClaudeClient`
   - API calls functioning

## Implementation Requirements

### 1. Precompute Function Integration

**Option A: Import from existing file**
```python
# In MLDataExtractor or new PrecomputeProcessor
from run_video_prompts_validated_v2 import (
    compute_creative_density_analysis,
    compute_emotional_metrics,
    # ... etc
)

def prepare_ml_context(self, unified_data, prompt_type):
    if prompt_type == PromptType.CREATIVE_DENSITY:
        timelines = unified_data.get('timelines', {})
        duration = unified_data.get('duration_seconds', 0)
        precomputed = compute_creative_density_analysis(timelines, duration)
        # Add raw timelines for validation
        context = {
            'precomputed_metrics': precomputed,
            'timelines': timelines,
            'duration': duration
        }
```

**Option B: Port to rumiai_v2 module**
- Copy functions into `rumiai_v2/processors/ml_precompute.py`
- Maintain clean module structure
- Better long-term maintainability

### 2. Update Prompt Templates

Replace generic prompts with structured prompts expecting 6-block output:
```
Goal: Extract creative density features as structured data for ML analysis

You will receive precomputed creative density metrics:
- average_density: Mean creative elements per second
- max_density: Maximum elements in any second
[... full list of metrics ...]

Output the following 6 modular blocks:

1. densityCoreMetrics
{
  "avgDensity": float,
  "maxDensity": float,
  ...
}

[... remaining 5 blocks ...]
```

### 3. FPS Integration

```python
# Add to video processing
def extract_video_metadata(video_path):
    import cv2
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    return VideoMetadata(
        fps=fps,
        frame_count=frame_count,
        duration=duration,
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    )

# Update timestamp conversions
def frame_to_timestamp(frame_number, fps):
    return float(frame_number) / float(fps)
```

### 4. Data Flow Update

Current flow:
```
Video → ML Services → Timeline Builder → ML Data Extractor → Claude
```

Required flow:
```
Video → ML Services → Timeline Builder → Precompute Functions → Structured Context → Claude → 6-Block Parser
         ↓
    FPS extraction
```

## Critical Constraints

1. **DO NOT modify temporal marker functionality** - it's working correctly
2. **Maintain backward compatibility** with existing outputs
3. **Keep the unified architecture** of the Python runner
4. **Preserve error handling** and JSON output structure

## Testing Requirements

After implementation, verify:
- [ ] All 7 precompute functions execute without errors
- [ ] Claude receives properly structured context with precomputed metrics
- [ ] Claude returns 6-block structured output
- [ ] FPS is correctly extracted and propagated
- [ ] Temporal markers still function
- [ ] No regression in existing functionality

## Priority Order

1. **High Priority:**
   - Add precompute functions
   - Update prompt templates for 6-block structure
   - Implement FPS extraction
   - Add 6-block output parser
   - Improve context data structure
   - Optimize precompute performance
   - Add caching for precomputed metrics

## References

- Source of truth: `Testytest_improved.md`
- Precompute functions: `run_video_prompts_validated_v2.py`
- FPS logic: `test_rumiai_complete_flow.js` and `LocalVideoAnalyzer.js`
- 6-block structure: All prompt templates in `prompt_templates/`