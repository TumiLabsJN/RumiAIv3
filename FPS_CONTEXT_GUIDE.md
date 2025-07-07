# FPS Context Management Guide

## Overview

The RumiAI video analysis pipeline processes videos at different frame rates (FPS) in different stages:
- **Original video**: 24-60 fps (variable)
- **Scene detection**: Original video FPS
- **ML analysis**: 1 fps (downsampled)
- **OCR**: 0.067 fps (every 15th frame)

This creates confusion when timestamps like "584-585s" could mean:
- Frames 584-585 at 30fps = 19.5 seconds
- Seconds 584-585 = 9.7 minutes (impossible for a 66s video!)

## The Solution: FPS Context Registry

Each video has an FPS registry file that tracks what timestamps mean in each context.

### Registry Location
```
fps_registry/
  ├── 7367449043070356782.json
  ├── 7345139303762234642.json
  └── ...
```

### Registry Format
```json
{
  "video_id": "7367449043070356782",
  "video_specs": {
    "original_fps": 30.0,
    "duration": 66.4,
    "total_frames": 1991
  },
  "analysis_contexts": {
    "scene_detection": {
      "fps": 30.0,
      "uses_original_fps": true,
      "description": "PySceneDetect runs on original video"
    },
    "frame_extraction": {
      "fps": 1.0,
      "sampling_rate": 30,
      "description": "Frames extracted for ML analysis"
    }
  }
}
```

## Usage

### 1. Create Registry for New Videos

During video analysis:
```python
from fps_utils import FPSContextManager

manager = FPSContextManager(video_id)
manager.create_registry_for_video(video_metadata, analysis_config)
```

Or from existing analysis:
```bash
python3 create_fps_registry.py 7367449043070356782
```

### 2. Convert Timestamps to Seconds

```python
from fps_utils import FPSContextManager

manager = FPSContextManager(video_id)

# Convert frame-based timestamp to seconds
seconds = manager.timestamp_to_seconds("584-585s", context="scene_detection")
# Returns: 19.47 (frame 584 at 30fps)
```

### 3. Generate Display Timestamps

```python
# Fix broken timestamps like "584-891s"
scene_data = {"frame": 584, "startTime": 19.5, "endTime": 29.7}
display = manager.get_display_timestamp(scene_data, duration_frames=307)
# Returns: "19-29s" (correct!)
```

## Implementation Status

### ✅ Fixed
- Scene pacing timestamp display (no more "584-891s")
- FPS context tracking system

### 🔄 In Progress
- Integration with video analysis pipeline
- Automatic registry generation

### 📋 TODO
- Update UnifiedTimelineAssembler to use FPS context
- Add FPS metadata to all analysis outputs
- Create migration script for existing videos

## Common Issues

### Missing FPS Registry
If no registry exists, the system uses defaults (30fps original, 1fps analysis).

### Frame vs Second Detection
The system uses heuristics:
- Values > video_duration are likely frames
- Values < 100 for long videos are likely seconds
- When in doubt, check the registry!

## Best Practices

1. **Always specify context** when converting timestamps
2. **Create registries early** in the pipeline
3. **Log warnings** when using fallback behavior
4. **Test with videos** of different frame rates

## Migration Guide

For existing videos without registries:
1. Run `python3 create_fps_registry.py <video_id>`
2. Verify the generated registry looks correct
3. Test scene pacing analysis produces valid timestamps