# Enhanced Temporal Markers - Quick Reference

## 🎯 Core System Flow

```
Video Analysis Pipeline
         ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ OCR Analyzer    │     │ YOLO Tracker    │     │ MediaPipe       │
│ (modified)      │     │ (modified)      │     │ (modified)      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         ↓                       ↓                       ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ OCRTemporal     │     │ YOLOTemporal    │     │ MediaPipeTemporal│
│ Extractor       │     │ Extractor       │     │ Extractor       │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         └───────────────────────┴───────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │ TemporalMarker         │
                    │ Integrator             │
                    └──────────┬─────────────┘
                               ↓
                    ┌────────────────────────┐
                    │ TemporalMarker         │
                    │ Safety                 │
                    └──────────┬─────────────┘
                               ↓
                    ┌────────────────────────┐
                    │ Claude Temporal        │
                    │ Integration            │
                    └──────────┬─────────────┘
                               ↓
                         Claude API
```

## 📁 Key Files Quick Reference

### Core Modules
- **`python/timestamp_normalizer.py`** - Converts all timestamps to seconds
- **`python/temporal_marker_safety.py`** - Size limits and validation
- **`python/temporal_marker_extractors.py`** - Analyzer-specific extractors
- **`python/temporal_marker_integration.py`** - Main pipeline

### Integration Points
- **`run_claude_insight.py`** - Modified to include temporal markers
- **`update_unified_analysis.py`** - Modified to extract markers
- **`detect_tiktok_creative_elements.py`** - OCR analyzer (modified)
- **`python/object_tracking.py`** - YOLO analyzer (modified)
- **`python/enhanced_human_analyzer.py`** - MediaPipe analyzer (modified)

### Monitoring & Control
- **`python/temporal_monitoring.py`** - Metrics tracking
- **`temporal_monitoring_dashboard.py`** - View metrics
- **`temporal_rollout_controller.py`** - Control deployment

### Prompts & Training
- **`prompts/temporal_aware_prompts.py`** - New prompt library
- **`temporal_training_workshop.py`** - Interactive training

## 🚀 Quick Start Commands

```bash
# 1. Check if temporal markers are working
python demo_temporal_markers.py <video_id>

# 2. Compare Claude analysis with/without markers
python demo_claude_temporal.py <video_id>

# 3. Enable temporal markers (0% rollout)
python temporal_rollout_controller.py enable

# 4. Start 10% rollout
python temporal_rollout_controller.py phase 1

# 5. Monitor health
python temporal_monitoring_dashboard.py

# 6. Run training workshop
python temporal_training_workshop.py
```

## 📊 Data Structure

```python
temporal_markers = {
    "first_5_seconds": {
        "density_progression": [3, 2, 4, 1, 2],  # Events per second
        "text_moments": [...],                    # Text with timestamps
        "emotion_sequence": [...],                # Emotion changes
        "gesture_moments": [...],                 # Gestures detected
        "object_appearances": [...]               # Objects seen
    },
    "cta_window": {
        "time_range": "51.0-60.0s",              # Last 15% of video
        "cta_appearances": [...],                 # CTAs detected
        "gesture_sync": [...],                    # Gesture alignment
        "object_focus": [...]                     # What's in focus
    }
}
```

## ⚙️ Configuration

Location: `config/temporal_markers.json`
```json
{
  "enable_temporal_markers": true,
  "rollout_percentage": 10.0,
  "format_options": {
    "include_density": true,
    "include_emotions": true,
    "include_gestures": true,
    "include_objects": true,
    "include_cta": true,
    "compact_mode": false
  }
}
```

## 🧪 Testing

```bash
# Run all temporal marker tests
source venv/bin/activate
python -m pytest tests/test_*temporal*.py tests/test_marker*.py -v

# Test specific component
python -m pytest tests/test_temporal_monitoring.py -v
```

## 🔍 Debugging

```python
# Check if markers are being extracted
from python.temporal_marker_integration import extract_temporal_markers
markers = extract_temporal_markers('video_id_123')
print(json.dumps(markers, indent=2))

# Check monitoring metrics
from python.temporal_monitoring import generate_metrics_report
print(generate_metrics_report())

# Check rollout status
python temporal_rollout_controller.py status
```

## 📈 Key Metrics to Monitor

1. **Extraction Success Rate** - Should be >90%
2. **Average Marker Size** - Should be <100KB
3. **Processing Time** - Should be <5s
4. **API Error Rate** - Should be <5%
5. **Quality Improvement** - Should show +2 or higher

## 🚨 Common Issues

1. **No temporal markers in Claude response**
   - Check rollout percentage
   - Verify ENABLE_TEMPORAL_MARKERS=true
   - Check if video has analyzer outputs

2. **Large marker sizes**
   - Enable compact_mode in config
   - Check for videos with excessive events

3. **Extraction failures**
   - Verify analyzer output files exist
   - Check file paths in integration module

## 💡 Pro Tips

1. Always run monitoring dashboard before increasing rollout
2. Test prompts with `compare_prompts_demo.py` first
3. Use training workshop for team onboarding
4. Start with high-impact prompts (hook_analysis, cta_effectiveness)
5. Monitor quality scores to validate improvements