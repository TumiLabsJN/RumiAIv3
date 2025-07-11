# Frame Processing Pipeline - Detailed Documentation

## Overview
This document provides comprehensive details about the frame processing pipeline in RumiAI v2, including exact code locations, logic implementation, and data flow.

## 1. Frame Extraction Process

### 1.1 Main Frame Extraction Logic
**File:** `/home/jorge/RumiAIv2-clean/automated_video_pipeline.py`
**Function:** `extract_frames()` (lines 22-66)

#### Adaptive FPS Extraction Algorithm
```python
def get_adaptive_fps(video_duration):
    """Get optimal FPS based on video duration for expression detection"""
    if video_duration < 30:
        return 5.0  # Short videos need more detail for expressions
    elif video_duration < 60:
        return 3.0  # Medium videos can use moderate sampling
    else:
        return 2.0  # Longer videos use lower sampling to manage processing
```

**Logic:**
- Videos < 30 seconds: Extract at 5 FPS
- Videos 30-60 seconds: Extract at 3 FPS  
- Videos > 60 seconds: Extract at 2 FPS

**Implementation Details:**
- Uses OpenCV (`cv2.VideoCapture`) for video reading
- Calculates frame interval: `interval_frames = max(1, int(fps * interval))`
- Saves frames as JPEG: `frame_{saved_count:04d}_t{timestamp:.2f}.jpg`
- Stores metadata in JSON format with fps, duration, frame_count, dimensions

### 1.2 Frame Sampler Utility
**File:** `/home/jorge/RumiAIv2-clean/python/frame_sampler.py`
**Class:** `FrameSampler`

**Key Methods:**
- `extract_video_metadata()` (lines 12-36): Extracts video properties
- `get_adaptive_fps()` (lines 39-53): Determines optimal FPS by analysis type
- `sample_uniform()` (lines 56-104): Samples frames at target FPS
- `get_all_frames()` (lines 116-144): Generator for all frames (used by YOLO)

**Adaptive FPS by Analysis Type:**
```python
if analysis_type == 'expression_detection' or analysis_type == 'mediapipe':
    # Higher FPS for expression/face detection
    if duration < 30:
        return 5.0  # Short videos need more detail
    elif duration < 60:
        return 3.0  # Medium videos moderate sampling
    else:
        return 2.0  # Longer videos lower sampling
elif analysis_type == 'object_detection':
    return 1.0  # Objects don't change as quickly
else:
    # Default general sampling
    return 1.0 if duration > 60 else 2.0
```

## 2. ML Model Processing

### 2.1 YOLO Object Detection
**File:** `/home/jorge/RumiAIv2-clean/python/object_tracking.py`
**Class:** `YOLODeepSortTracker`

#### Processing Rate Implementation (lines 166-185)
```python
# Adaptive frame skipping based on video duration and extraction FPS
if frame_skip == -1:  # Use adaptive mode
    if video_duration < 30:
        # Extraction at 5 FPS, we want 2.5 FPS effective
        frame_skip = int(fps / 2.5) - 1
        effective_fps = fps / (frame_skip + 1)
    elif video_duration < 60:
        # Extraction at 3 FPS, we want 2 FPS effective  
        frame_skip = int(fps / 2.0) - 1
        effective_fps = fps / (frame_skip + 1)
    else:
        # Extraction at 2 FPS, we want 2 FPS effective
        frame_skip = int(fps / 2.0) - 1
        effective_fps = fps / (frame_skip + 1)
```

**Key Components:**
- **Model:** YOLOv8n (nano version for speed)
- **Tracker:** DeepSort for object tracking across frames
- **GPU Support:** Auto-detects and uses CUDA if available
- **Processing Logic:**
  - Processes frames based on adaptive skip pattern
  - Maintains object tracks with IDs
  - Outputs normalized bounding boxes (0-1 range)
  - Tracks confidence scores per detection

**Output Format:**
```json
{
    "trackId": "object_1",
    "entity": {
        "entityId": "person",
        "description": "person"
    },
    "confidence": 0.95,
    "frames": [
        {
            "frame": 0,
            "timestamp": 0.0,
            "bbox": {
                "left": 0.2,
                "top": 0.3,
                "right": 0.8,
                "bottom": 0.9
            },
            "confidence": 0.95
        }
    ]
}
```

### 2.2 MediaPipe Human Analysis
**File:** `/home/jorge/RumiAIv2-clean/python/enhanced_human_analyzer.py`
**Class:** `EnhancedHumanAnalyzer`

**Processing Components:**
1. **Face Mesh** (lines 52-57): Up to 5 faces, refined landmarks
2. **Hand Detection** (lines 59-63): Up to 4 hands
3. **Pose Detection** (lines 66-73): Full body tracking with segmentation
4. **Scene Segmentation** (lines 76-78): Person/background separation

**Key Analysis Functions:**
- `analyze_frame()` (lines 115-187): Main frame processing
- `_analyze_body_pose()` (lines 189-240): Posture and gesture analysis
- `_analyze_gaze()` (lines 242-275): Eye contact and gaze direction
- `_analyze_scene_segmentation()` (lines 277-311): Background complexity
- `_recognize_actions()` (lines 313-338): Action detection (talking, dancing, etc.)

**Processing Rate:**
- Uses extracted frames (2-5 FPS based on video duration)
- Processes each frame independently
- No frame skipping - analyzes all extracted frames

### 2.3 OCR Text Detection
**File:** `/home/jorge/RumiAIv2-clean/detect_tiktok_creative_elements.py`
**Class:** `TikTokCreativeDetector`

#### Adaptive Sampling for OCR (lines 346-366)
```python
if video_duration < 30:
    # Videos < 30s: Process every 2nd frame (2.5 FPS effective)
    for i in range(0, len(frames), 2):
        sampled_frames.append(frames[i])
elif video_duration < 60:
    # Videos 30-60s: Process first 2 of every 3 frames (2 FPS effective)
    for i in range(len(frames)):
        if i % 3 != 2:  # Skip every 3rd frame
            sampled_frames.append(frames[i])
else:
    # Videos > 60s: Process every frame (2 FPS effective)
    sampled_frames = frames
```

**Key Components:**
- **OCR Engine:** EasyOCR with GPU support
- **Text Categorization:** Based on position and content
- **Creative Elements:** Detects stickers, banners, UI elements
- **Batch Processing:** Adjusts batch size based on VRAM

**GPU Memory Management (lines 370-379):**
```python
if detector.gpu_enabled and CUDA_AVAILABLE:
    free_vram_gb = (torch.cuda.get_device_properties(0).total_memory - 
                    torch.cuda.memory_allocated()) / 1024**3
    if free_vram_gb < 2.0:
        BATCH_SIZE = 3  # Conservative for low VRAM
    elif free_vram_gb < 4.0:
        BATCH_SIZE = 5  # Medium batch size
    else:
        BATCH_SIZE = 10  # Full batch size for 4GB+ free
```

### 2.4 Enhanced Human Analysis
**File:** `/home/jorge/RumiAIv2-clean/enhanced_human_analyzer.py`

**Processing Features:**
- Body pose detection with 33 landmarks
- Face mesh with 468 landmarks
- Hand tracking with gesture recognition
- Scene segmentation for person/background
- Action recognition (8 predefined actions)
- Gaze analysis and eye contact detection

**Temporal Analysis:**
- Background change detection (lines 498-563)
- Temporal marker extraction (lines 565-649)
- Expression and gesture timeline building

## 3. Pipeline Orchestration

### 3.1 Main Orchestrator
**File:** `/home/jorge/RumiAIv2-clean/server/services/LocalVideoAnalyzer.js`
**Class:** `LocalVideoAnalyzer`

**Key Methods:**
- `analyzeVideo()` (lines 595-749): Main orchestration function
- `extractFrames()` (lines 850-879): Frame extraction coordination
- `runYOLOWithDeepSort()` (lines 98-166): YOLO processing
- `runMediaPipe()` (lines 171-239): MediaPipe processing
- `runOCR()` (lines 244-334): OCR processing
- `runEnhancedHumanAnalysis()` (lines 449-521): Enhanced analysis

**Processing Flow:**
1. Extract video metadata
2. Run Whisper transcription (parallel)
3. Extract frames (if needed)
4. Run all ML models in parallel:
   - YOLO + DeepSort
   - MediaPipe
   - OCR
   - Scene Detection
   - CLIP labeling
   - Enhanced Human Analysis
   - Content Moderation
5. Synchronize timelines
6. Generate temporal markers
7. Return unified analysis

### 3.2 Timeline Synchronization
**File:** `/home/jorge/RumiAIv2-clean/server/services/TimelineSynchronizer.js`

**Purpose:** Aligns all ML model outputs to a common timeline based on frame numbers and timestamps.

## 4. Data Flow

### Input
- Video file (MP4, AVI, MOV, MKV)
- Video ID (extracted from filename)

### Processing Steps
1. **Frame Extraction**
   - Adaptive FPS (2-5 FPS) based on duration
   - Saved as JPEG in `frame_outputs/{video_id}/`
   - Metadata saved as JSON

2. **Model Processing**
   - Each model processes frames independently
   - Some models (YOLO) use frame skipping
   - Others (MediaPipe, OCR) process all extracted frames

3. **Output Storage**
   - YOLO: `object_detection_outputs/{video_id}/`
   - MediaPipe: `human_analysis_outputs/{video_id}/`
   - OCR: `creative_analysis_outputs/{video_id}/`
   - Enhanced: `enhanced_human_analysis_outputs/{video_id}/`

### Output Format
Unified JSON structure containing:
- Speech transcriptions
- Object annotations
- Person annotations
- Text annotations
- Scene shots
- Labels
- Temporal markers
- Metadata

## 5. Dependencies

### Python Libraries
- opencv-python: Video processing
- ultralytics: YOLOv8
- deep-sort-realtime: Object tracking
- mediapipe: Human analysis
- easyocr: Text detection
- numpy: Numerical operations
- torch: GPU acceleration

### System Requirements
- Python 3.8+
- CUDA (optional, for GPU acceleration)
- 4GB+ VRAM recommended for GPU mode
- FFmpeg (for video processing)

## 6. Performance Characteristics

### Frame Extraction
- 2-5 FPS adaptive based on video duration
- JPEG compression for storage efficiency

### Model Processing Rates
- YOLO: ~2-2.5 FPS effective (with frame skipping)
- MediaPipe: Processes all extracted frames
- OCR: ~2 FPS effective (with adaptive sampling)
- Enhanced Human: Processes all extracted frames

### GPU Optimization
- Automatic GPU detection and usage
- Batch processing with VRAM-aware sizing
- Memory cleanup between batches
- Fallback to CPU on GPU errors