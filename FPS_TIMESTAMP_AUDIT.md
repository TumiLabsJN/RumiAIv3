# FPS and Timestamp Calculation Audit Report

## Critical Issues Found

### 1. Frame-to-Time Conversions (HIGH RISK)

**automated_video_pipeline.py**
- Line 34: `duration = total_frames / fps if fps > 0 else 0`
- Line 58: `timestamp = frame_count / fps`
- Line 92: `duration = frame_count / fps if fps > 0 else 0`
- **Risk**: Assumes video FPS is constant and accurate

**python/frame_sampler.py**
- Line 22: `duration = frame_count / fps if fps > 0 else 0`
- Line 71: `duration = frame_count / source_fps if source_fps > 0 else 0`
- Line 88: `'timestamp': frame_idx / source_fps`
- Line 127: `'timestamp': frame_idx / fps`
- Line 156: `'timestamp': frame_idx / fps`
- **Risk**: Multiple FPS sources, no validation

**python/object_tracking.py**
- Line 154: `timestamp = frame_idx / fps`
- **Risk**: Frame skip logic may cause timestamp drift

**python/scene_detection.py**
- Line 94: `'timestamp': middle_frame / result['fps']`
- **Risk**: Assumes PySceneDetect FPS matches actual video FPS

### 2. FPS-Based Interval Calculations (MEDIUM RISK)

**automated_video_pipeline.py**
- Line 39: `interval = 1.0 / target_fps`
- Line 49: `interval_frames = max(1, int(fps * interval))`
- **Risk**: Integer rounding causes frame drift

**python/frame_sampler.py**
- Line 75: `frame_interval = int(source_fps / target_fps) if source_fps > target_fps else 1`
- **Risk**: Integer division loses precision

### 3. Adaptive FPS Logic (MEDIUM RISK)

**python/frame_sampler.py** (get_adaptive_fps function)
- Lines 39-49: Different FPS based on duration thresholds
  - < 30s: 5.0 FPS
  - < 60s: 3.0 FPS
  - >= 60s: 2.0 FPS
- **Risk**: Arbitrary thresholds, no consideration of video content

### 4. Missing FPS Metadata (HIGH RISK)

**All output files lack FPS metadata**:
- Frame extraction doesn't record source FPS
- Analysis outputs don't include which FPS was used
- No way to trace back to original video FPS

### 5. The Core Problem in run_video_prompts_validated_v2.py

**Line 2617**: 
```python
longest_timestamp = f"{int(scene_times[longest_idx])}-{int(scene_times[longest_idx] + max_shot_duration)}s"
```
- **Risk**: `max_shot_duration` is calculated from time differences but index mapping assumes consistent FPS

## Affected Pipeline Stages

1. **Frame Extraction** (automated_video_pipeline.py)
   - Extracts frames at adaptive FPS (1-5 fps)
   - Saves with timestamp in filename

2. **Object Tracking** (object_tracking.py)
   - Processes frames with skip logic
   - Calculates timestamps from frame index

3. **Scene Detection** (scene_detection.py)
   - Uses PySceneDetect at original video FPS
   - Returns both frame numbers and seconds

4. **Frame Sampling** (frame_sampler.py)
   - Multiple sampling strategies
   - Each with different FPS assumptions

## Recommendations

### Immediate Actions

1. **Add FPS metadata to all outputs**:
   ```python
   {
       "source_fps": 30.0,
       "processing_fps": 1.0,
       "frame_interval": 30,
       "timestamp_calculation": "frame_idx / source_fps"
   }
   ```

2. **Use PySceneDetect's time values directly**:
   - Don't recalculate from frame numbers
   - Trust the library's time calculations

3. **Standardize timestamp format**:
   - Always use floating-point seconds
   - Include millisecond precision

### Long-term Fixes

1. **Create FPS-aware timestamp converter**:
   ```python
   class TimestampConverter:
       def __init__(self, source_fps, processing_fps):
           self.source_fps = source_fps
           self.processing_fps = processing_fps
       
       def frame_to_time(self, frame_idx):
           return frame_idx / self.source_fps
   ```

2. **Add validation checks**:
   - Verify FPS before calculations
   - Log warnings for FPS mismatches
   - Fail gracefully when FPS unknown

3. **Store complete timing metadata**:
   - Original video FPS
   - Processing FPS for each stage
   - Frame extraction interval
   - Timestamp generation method

## Impact Assessment

- **High Impact**: Scene pacing metrics, shot duration calculations
- **Medium Impact**: Object tracking timelines, frame sampling
- **Low Impact**: Static analysis (doesn't depend on timing)

## Testing Requirements

1. Test with videos at different FPS (24, 25, 30, 60)
2. Verify timestamp consistency across pipeline
3. Check for frame drift in long videos
4. Validate scene boundary accuracy