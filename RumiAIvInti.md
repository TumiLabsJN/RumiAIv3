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

**Complete FPS handling is documented in `FRAME_PROCESSING_DOCUMENTATION.md`**

#### The 4 FPS Contexts Explained:

1. **Original Video FPS** (e.g., 30fps)
   - Extracted during initial video processing
   - Used for accurate timestamp calculations
   - Required for scene detection and timeline synchronization

2. **Frame Extraction FPS** (adaptive: 2-5fps)
   - Based on video duration:
     - < 30s: 5 FPS
     - 30-60s: 3 FPS  
     - > 60s: 2 FPS
   - Determines which frames are saved as JPEGs

3. **ML Model Processing FPS** (varies by service)
   - YOLO: ~2 FPS (processes every 12-15th frame)
   - MediaPipe: All extracted frames
   - OCR: 1.67-2.5 FPS (adaptive sampling)
   - Enhanced Human: All extracted frames

4. **Timeline Aggregation FPS** (1fps for 1-second buckets)
   - Final output uses 1-second time buckets
   - All frame-level data aggregated to these buckets

#### Frame-to-Timestamp Conversion:

```python
# Add to video processing
def extract_video_metadata(video_path):
    import cv2
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    return VideoMetadata(
        original_fps=fps,
        frame_count=frame_count,
        duration=duration,
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    )

# Frame number to timestamp conversion
def frame_to_timestamp(frame_number, fps):
    """Convert frame number to timestamp in seconds"""
    return float(frame_number) / float(fps)

# Example: In timeline data, "frame": 1 at 30fps = 0.033 seconds
# This is why timelines use "0-1s" buckets for aggregation
```

#### Key Implementation Points:
- Store original video FPS in metadata for all conversions
- ML services output frame numbers, not timestamps
- Timeline builder converts frame numbers to timestamps using original FPS
- All timeline data ultimately aggregated to 1-second buckets

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

## Prompt Template Management

### Current State
The complete prompt templates are currently embedded in `Testytest_improved.md`. These are production-ready prompts that produce the expected 6-block output structure. They need to be extracted into individual files.

### Required Actions

1. **Extract Prompts from Testytest_improved.md**
   ```python
   # Create these files with content from Testytest_improved.md:
   
   # Creative Density (lines 179-311)
   prompt_templates/creative_density_v2.txt
   
   # Emotional Journey (lines 399-484)  
   prompt_templates/emotional_journey_v2.txt
   
   # Person Framing (lines 569-652)
   prompt_templates/person_framing_v2.txt
   
   # Scene Pacing (lines 714-805)
   prompt_templates/scene_pacing_v2.txt
   
   # Speech Analysis (lines 864-953)
   prompt_templates/speech_analysis_v2.txt
   
   # Visual Overlay (lines 1029-1114)
   prompt_templates/visual_overlay_v2.txt
   
   # Metadata Analysis (lines 1179-1300)
   prompt_templates/metadata_analysis_v2.txt
   ```

2. **Prompt Structure (from Testytest_improved.md)**
   Each prompt follows this pattern:
   - Goal statement
   - Input file reference
   - List of precomputed metrics with descriptions
   - 6-block output specification with JSON schemas
   - Field definitions for each block

3. **Integration in Code**
   ```python
   # In MLDataExtractor or new PromptManager
   class PromptManager:
       def __init__(self, template_dir="prompt_templates"):
           self.template_dir = template_dir
           self.prompts = {}
           self._load_prompts()
       
       def _load_prompts(self):
           """Load all prompt templates extracted from Testytest_improved.md"""
           for prompt_type in PromptType:
               filename = f"{prompt_type.value}_v2.txt"
               path = os.path.join(self.template_dir, filename)
               with open(path, 'r') as f:
                   self.prompts[prompt_type] = f.read()
       
       def get_prompt(self, prompt_type: PromptType) -> str:
           """Get the prompt template for a specific analysis type"""
           return self.prompts.get(prompt_type, "")
   ```

### Why This Matters
- Testytest_improved.md contains the **exact, tested prompts** that produce the expected 6-block output
- These aren't generic templates - they're specifically crafted for Claude to understand the data structure
- The prompts include the precise field names and types expected by the ML pipeline
- Each prompt is designed to work with the precomputed metrics from the corresponding compute function

### Prompt Versioning Strategy
- Start with v2 (since v1 was the non-6-block version)
- Keep prompts in sync with precompute function outputs
- Test any prompt changes against sample data before deployment
- Document changes in a CHANGELOG.md within prompt_templates/

## Runtime Validation and Error Handling

### 1. Response Validation in Production

```python
# Add to MLDataExtractor or create ResponseValidator
class ResponseValidator:
    def __init__(self):
        self.expected_blocks = {
            PromptType.CREATIVE_DENSITY: [
                "densityCoreMetrics", "densityDynamics", "densityInteractions",
                "densityKeyEvents", "densityPatterns", "densityQuality"
            ],
            PromptType.EMOTIONAL_JOURNEY: [
                "emotionalCoreMetrics", "emotionalDynamics", "emotionalInteractions",
                "emotionalKeyEvents", "emotionalPatterns", "emotionalQuality"
            ],
            # ... other prompt types
        }
    
    def validate_claude_response(self, response: str, prompt_type: PromptType) -> dict:
        """Validate Claude's 6-block response structure"""
        try:
            data = json.loads(response)
            
            # Check for expected blocks
            expected = self.expected_blocks[prompt_type]
            missing = [block for block in expected if block not in data]
            
            if missing:
                logger.warning(f"{prompt_type.value}: Missing blocks {missing}")
                # Continue with partial data - don't fail the pipeline
            
            # Basic type validation for each block
            for block_name, block_data in data.items():
                if not isinstance(block_data, dict):
                    logger.warning(f"{block_name} is not a dict, got {type(block_data)}")
                if 'confidence' not in block_data:
                    logger.warning(f"{block_name} missing confidence score")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return {}
```

### 2. Precompute Function Error Handling

```python
# Add to MLDataExtractor.prepare_ml_context()
def prepare_ml_context(self, unified_data: dict, prompt_type: PromptType) -> dict:
    """Prepare context with precomputed metrics for Claude"""
    context = {
        "video_duration": unified_data.get("duration_seconds", 0),
        "timelines": unified_data.get("timelines", {})
    }
    
    try:
        # Import and run appropriate precompute function
        if prompt_type == PromptType.CREATIVE_DENSITY:
            from precompute_functions import compute_creative_density_analysis
            context["precomputed_metrics"] = compute_creative_density_analysis(
                context["timelines"], context["video_duration"]
            )
        elif prompt_type == PromptType.EMOTIONAL_JOURNEY:
            # ... similar for other types
            
    except Exception as e:
        logger.error(f"Precompute failed for {prompt_type.value}: {e}")
        # Add minimal metrics to allow pipeline to continue
        context["precomputed_metrics"] = {
            "error": str(e),
            "fallback": True,
            "basic_metrics": self._compute_basic_metrics(unified_data)
        }
    
    return context
```

### 3. Pipeline Resilience

```python
# Update _run_claude_prompts to handle validation
async def _run_claude_prompts(self, unified_path: str) -> Dict[str, Any]:
    """Run all 7 ML prompts with validation"""
    results = {}
    validator = ResponseValidator()
    
    for prompt_type in PromptType:
        try:
            # Prepare context with precomputed metrics
            context = self.ml_extractor.prepare_ml_context(unified_data, prompt_type)
            
            # Get and format prompt
            prompt = self.prompt_manager.format_prompt(prompt_type, context)
            
            # Call Claude
            response = await self.claude_client.analyze(prompt)
            
            # Validate and parse response
            parsed = validator.validate_claude_response(response, prompt_type)
            
            if parsed:
                results[prompt_type.value] = parsed
            else:
                logger.error(f"Invalid response for {prompt_type.value}")
                results[prompt_type.value] = {"error": "Invalid response"}
                
        except Exception as e:
            logger.error(f"Failed to run {prompt_type.value}: {e}")
            results[prompt_type.value] = {"error": str(e)}
    
    return results
```

### 4. Testing Approach (Separate from Production)

**Note**: Comprehensive testing should be implemented separately from the production runner:

- **Unit tests** for each precompute function in `tests/test_precompute_functions.py`
- **Integration tests** for the full pipeline in `tests/test_ml_pipeline.py`
- **Schema validation tests** using JSON schemas in `tests/schemas/`
- **Sample test data** in `tests/fixtures/` with known-good unified analysis files

Example test structure:
```
tests/
├── test_precompute_functions.py     # Test each compute_* function
├── test_response_validation.py      # Test 6-block validation
├── test_ml_pipeline_integration.py  # End-to-end tests
├── fixtures/
│   ├── sample_unified_analysis.json
│   └── expected_outputs/
│       └── creative_density_6blocks.json
└── conftest.py                      # Pytest fixtures
```

### 5. Logging and Monitoring

Add comprehensive logging to track pipeline health:
- Log precompute execution times
- Track Claude response success rates
- Monitor missing blocks or validation failures
- Alert on high error rates

This approach ensures the production pipeline is resilient while maintaining quality through separate comprehensive testing.

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