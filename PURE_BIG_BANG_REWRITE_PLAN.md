# RumiAI v2 Pure Big Bang Rewrite - Complete Execution Guide

## ⚠️ CRITICAL PRE-MORTEM ANALYSIS

### What This Rewrite Could Break

1. **Node.js Integration Points**
   - `test_rumiai_complete_flow.js` expects specific Python script paths
   - `LocalVideoAnalyzer.js` hardcodes paths to ML analysis scripts
   - `TemporalMarkerService.js` expects specific JSON output format
   - **Impact**: Complete pipeline failure if paths/formats change

2. **File System Dependencies**
   - Current system writes to specific directories without validation
   - Multiple processes may write to same files simultaneously
   - No file locking mechanism exists
   - **Impact**: Data corruption, race conditions

3. **External API Assumptions**
   - Claude API rate limits not properly tracked
   - Apify token validation happens late in process
   - No circuit breaker for failing services
   - **Impact**: Wasted processing, incomplete results

4. **Memory and Performance**
   - Loading entire video analysis into memory
   - No streaming for large videos (>5 min)
   - Python subprocess buffer limits in Node.js
   - **Impact**: OOM crashes, subprocess hangs

### Validation Required Before Ship

1. **Automated Integration Tests**
   ```bash
   # Must pass ALL without manual intervention
   ./test_integration_suite.sh
   ```

2. **Path Compatibility Layer**
   - Symlinks from old paths to new during transition
   - JSON output adapters for backward compatibility

3. **Performance Benchmarks**
   - Process 10 videos of varying lengths
   - Memory usage must stay under 4GB
   - No single video should take >5 minutes

## Executive Summary

This document provides a complete blueprint for rewriting the RumiAI v2 system from scratch. The current system suffers from:
- Missing Python dependencies (90% of failures)
- Inconsistent timestamp formats causing TypeErrors
- Multiple implementations of the same functionality
- No data validation or error boundaries
- Fragmented Python/Node.js architecture

**Goal**: Build a clean, reliable system that processes TikTok videos through ML analysis and generates Claude insights without the current architectural flaws.

**Timeline**: 14-20 days of focused development
**Automation Requirement**: Must maintain `node test_rumiai_complete_flow.js VIDEO_URL` interface

## Current System Problems (DO NOT REPLICATE)

### 1. Timestamp Format Chaos
```python
# Current system has multiple formats:
"0-1s"          # String range
"0s"            # String single
0               # Integer seconds
0.5             # Float seconds
None            # Missing data
"0:00"          # Time format
```

### 2. Missing Core Dependencies
```
❌ python/temporal_marker_extractors.py     - NEVER CREATED
❌ python/timestamp_normalizer.py           - NEVER CREATED  
❌ python/temporal_marker_safety.py         - NEVER CREATED
```

### 3. Multiple Temporal Marker Generators
```
TemporalMarkerGenerator.py         (broken)
generate_temporal_markers_simple.py (broken)
generate_temporal_markers_working.py (broken)
generate_temporal_markers_fixed.py  (partially works)
```

### 4. Error Cascade Pattern
```python
# Current: One failure breaks everything
try:
    temporal_markers = generate()
except:
    pass  # Silent failure
# Later: assumes temporal_markers exists → crash
```

## New Architecture Overview

```
RumiAIv2-clean/
├── rumiai_v2/                       # NEW SYSTEM ROOT
│   ├── __init__.py
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── models/                  # Data models
│   │   │   ├── __init__.py
│   │   │   ├── timestamp.py         # Single timestamp implementation
│   │   │   ├── timeline.py          # Unified timeline model
│   │   │   ├── video.py             # Video metadata
│   │   │   ├── analysis.py          # ML analysis results
│   │   │   └── prompt.py            # Prompt-related models
│   │   │
│   │   ├── validators/              # Validation layer
│   │   │   ├── __init__.py
│   │   │   ├── timestamp_validator.py
│   │   │   ├── timeline_validator.py
│   │   │   └── ml_data_validator.py
│   │   │
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── processors/                  # Business logic
│   │   ├── __init__.py
│   │   ├── temporal_markers.py      # ONE implementation only
│   │   ├── ml_data_extractor.py     # Extract data for prompts
│   │   ├── timeline_builder.py      # Build unified timeline
│   │   ├── prompt_builder.py        # Build Claude prompts
│   │   └── video_analyzer.py        # Orchestrate ML analysis
│   │
│   ├── api/                         # External interfaces
│   │   ├── __init__.py
│   │   ├── claude_client.py         # Claude API with retry
│   │   ├── apify_client.py          # TikTok scraping
│   │   └── ml_services.py           # ML model interfaces
│   │
│   ├── config/                      # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py              # Environment config
│   │   ├── prompts.yaml             # Prompt templates
│   │   └── constants.py             # System constants
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── file_handler.py          # File I/O with validation
│   │   ├── logger.py                # Structured logging
│   │   └── metrics.py               # Performance tracking
│   │
│   └── tests/                       # Test suite
│       ├── __init__.py
│       ├── fixtures/                # Test data
│       ├── unit/                    # Unit tests
│       └── integration/             # Integration tests
│
├── scripts/                         # Entry points
│   ├── rumiai_runner.py            # Main entry point
│   ├── test_single_video.py        # Test harness
│   └── validate_fixtures.py        # Validate test data
│
├── docs/                           # Documentation
│   ├── API.md                      # API documentation
│   ├── DATA_MODELS.md              # Data model specs
│   └── MIGRATION.md                # Migration guide
│
└── old_system_archived/            # Move ALL old code here

## ⚠️ CRITICAL IMPLEMENTATION CONSTRAINTS

### 1. Automation Requirements
- **NO MANUAL STEPS**: Everything must work via `node test_rumiai_complete_flow.js VIDEO_URL`
- **NO INTERACTIVE PROMPTS**: All config via environment variables or files
- **NO HUMAN DECISIONS**: All logic must be deterministic

### 2. Backward Compatibility During Transition
```bash
# These commands MUST continue working:
node test_rumiai_complete_flow.js "https://tiktok.com/..."
python run_video_prompts_validated_v2.py VIDEO_ID  # Called by Node.js
```

### 3. File Output Compatibility
```python
# New system must write to EXACT same paths:
# unified_analysis/{video_id}.json
# temporal_markers/{video_id}_{timestamp}.json
# insights/{video_id}/{prompt_name}/*
```

## Phase 1: Core Data Models (Days 1-3)

### ⚠️ FAILURE MODE ANALYSIS - Data Models

**What Could Break**:
1. Existing JSON parsers expect string timestamps ("0-1s")
2. Comparison operators throughout codebase assume specific formats
3. Frontend/reporting tools may parse these files

**Mitigation Strategy**:
```python
# Dual-format serialization during transition
class Timestamp:
    def to_json(self, legacy_mode=True):
        if legacy_mode:
            return f"{int(self.seconds)}s"  # Old format
        return self.seconds  # New format
```

### 1.1 Timestamp Model

**File**: `rumiai_v2/core/models/timestamp.py`

```python
from dataclasses import dataclass
from typing import Union, Optional
import re

@dataclass(frozen=True)
class Timestamp:
    """Immutable timestamp in seconds."""
    seconds: float
    
    def __post_init__(self):
        if self.seconds < 0:
            raise ValueError(f"Timestamp cannot be negative: {self.seconds}")
    
    @classmethod
    def from_value(cls, value: Union[str, int, float, None]) -> Optional['Timestamp']:
        """Parse any timestamp format to Timestamp object.
        
        CRITICAL: This function is called thousands of times per video.
        Any exception here cascades to complete pipeline failure.
        """
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            return cls(float(value))
            
        if isinstance(value, str):
            # Handle "0-1s" format
            if match := re.match(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)s?', value):
                start = float(match.group(1))
                return cls(start)  # Use start of range
                
            # Handle "0s" or "0.5s" format
            if match := re.match(r'(\d+(?:\.\d+)?)s?', value):
                return cls(float(match.group(1)))
                
            # Handle "0:00" format
            if match := re.match(r'(\d+):(\d+)', value):
                minutes, seconds = int(match.group(1)), int(match.group(2))
                return cls(minutes * 60 + seconds)
                
        # Log but don't crash - return None for unparseable
        import logging
        logging.warning(f"Cannot parse timestamp: {value}, returning None")
        return None  # CRITICAL: Don't break pipeline on bad timestamp
    
    def __lt__(self, other: 'Timestamp') -> bool:
        return self.seconds < other.seconds
```

### 1.2 Timeline Model

**CRITICAL PATH**: This model is used by ALL 7 Claude prompts. Any failure here affects everything.

**File**: `rumiai_v2/core/models/timeline.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator
from .timestamp import Timestamp

@dataclass
class TimelineEntry:
    """Single entry in a timeline."""
    start: Timestamp
    end: Optional[Timestamp]  # None for instantaneous events
    entry_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        if self.end:
            return self.end.seconds - self.start.seconds
        return 0.0
    
    def overlaps(self, other: 'TimelineEntry') -> bool:
        """Check if two entries overlap in time."""
        if not self.end or not other.end:
            return False
        return (self.start.seconds < other.end.seconds and 
                self.end.seconds > other.start.seconds)

@dataclass
class Timeline:
    """Unified timeline structure."""
    video_id: str
    duration: float  # Total video duration in seconds
    entries: List[TimelineEntry] = field(default_factory=list)
    
    def add_entry(self, entry: TimelineEntry) -> None:
        """Add entry maintaining chronological order.
        
        CRITICAL: MediaPipe/YOLO often report timestamps beyond video duration.
        Must handle gracefully to prevent pipeline failure.
        """
        if entry.start.seconds > self.duration:
            # Log but don't fail - clamp to duration
            import logging
            logging.warning(f"Entry start {entry.start.seconds} exceeds duration {self.duration}, clamping")
            entry.start = Timestamp(self.duration)
        
        # Insert in chronological order
        insert_idx = 0
        for i, existing in enumerate(self.entries):
            if entry.start.seconds < existing.start.seconds:
                insert_idx = i
                break
            insert_idx = i + 1
        
        self.entries.insert(insert_idx, entry)
    
    def get_entries_in_range(self, start: float, end: float) -> List[TimelineEntry]:
        """Get all entries within time range."""
        return [
            entry for entry in self.entries
            if (entry.start.seconds >= start and entry.start.seconds < end) or
               (entry.end and entry.end.seconds > start and entry.end.seconds <= end)
        ]
    
    def get_entries_by_type(self, entry_type: str) -> List[TimelineEntry]:
        """Get all entries of specific type."""
        return [entry for entry in self.entries if entry.entry_type == entry_type]
```

### 1.3 Analysis Model

**File**: `rumiai_v2/core/models/analysis.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .timeline import Timeline

@dataclass
class MLAnalysisResult:
    """Results from a single ML model."""
    model_name: str
    model_version: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time: float = 0.0

@dataclass
class UnifiedAnalysis:
    """Complete analysis results for a video."""
    video_id: str
    video_metadata: Dict[str, Any]
    timeline: Timeline
    ml_results: Dict[str, MLAnalysisResult] = field(default_factory=dict)
    temporal_markers: Optional[Dict[str, Any]] = None
    
    def add_ml_result(self, result: MLAnalysisResult) -> None:
        """Add ML analysis result."""
        self.ml_results[result.model_name] = result
    
    def get_ml_data(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get data from specific ML model."""
        if model_name in self.ml_results and self.ml_results[model_name].success:
            return self.ml_results[model_name].data
        return None
    
    def is_complete(self) -> bool:
        """Check if all required analyses are complete."""
        required_models = ['yolo', 'whisper', 'mediapipe', 'ocr', 'scene_detection']
        return all(
            model in self.ml_results and self.ml_results[model].success
            for model in required_models
        )
```

## Phase 2: Validators and Exceptions (Days 4-5)

### ⚠️ CRITICAL DESIGN DECISION: Fail Fast vs Graceful Degradation

**Current System**: Fails silently, produces empty results
**New System**: Must balance between:
1. **Failing fast** for development/debugging
2. **Graceful degradation** for production

**Solution**: Environment-based behavior
```python
STRICT_MODE = os.getenv('RUMIAI_STRICT_MODE', 'false').lower() == 'true'

if STRICT_MODE:
    raise ValidationError(...)  # Fail fast in dev
else:
    log_error_and_continue()   # Degrade gracefully in prod
```

### 2.1 Custom Exceptions

**File**: `rumiai_v2/core/exceptions.py`

```python
class RumiAIError(Exception):
    """Base exception for all RumiAI errors."""
    pass

class ValidationError(RumiAIError):
    """Data validation error."""
    def __init__(self, field: str, value: Any, expected: str):
        self.field = field
        self.value = value
        self.expected = expected
        # Include video context for debugging
        video_id = getattr(self, '_video_id', 'unknown')
        super().__init__(f"[Video {video_id}] Invalid {field}: got {value}, expected {expected}")

class TimelineError(RumiAIError):
    """Timeline-related error."""
    pass

class MLAnalysisError(RumiAIError):
    """ML analysis error."""
    def __init__(self, model: str, reason: str):
        self.model = model
        self.reason = reason
        super().__init__(f"ML analysis failed for {model}: {reason}")

class PromptError(RumiAIError):
    """Prompt processing error."""
    pass

class APIError(RumiAIError):
    """External API error."""
    def __init__(self, service: str, status_code: int, message: str):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API error ({status_code}): {message}")
```

### 2.2 Validators

**File**: `rumiai_v2/core/validators/ml_data_validator.py`

```python
from typing import Dict, Any, List
from ..exceptions import ValidationError

class MLDataValidator:
    """Validate ML model outputs."""
    
    @staticmethod
    def validate_yolo_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize YOLO object detection data.
        
        CRITICAL: YOLO output format varies by version.
        Must handle v5, v8, and custom formats.
        """
        # Handle multiple format variants
        if 'objectAnnotations' not in data:
            # Try alternative keys
            if 'detections' in data:
                data['objectAnnotations'] = data['detections']
            elif 'results' in data:
                data['objectAnnotations'] = data['results']
            else:
                # Return empty but valid structure
                logging.warning("No YOLO detections found, using empty structure")
                data['objectAnnotations'] = []
        
        # Validate structure
        if not isinstance(data['objectAnnotations'], list):
            raise ValidationError('objectAnnotations', type(data['objectAnnotations']), 'list')
        
        for annotation in data['objectAnnotations']:
            if 'frames' not in annotation:
                raise ValidationError('annotation', annotation, "must contain 'frames'")
    
    @staticmethod
    def validate_whisper_data(data: Dict[str, Any]) -> None:
        """Validate Whisper transcription data."""
        required_keys = ['segments', 'text', 'language']
        for key in required_keys:
            if key not in data:
                raise ValidationError('whisper_data', data, f"must contain '{key}'")
        
        if not isinstance(data['segments'], list):
            raise ValidationError('segments', type(data['segments']), 'list')
        
        for segment in data['segments']:
            required_segment_keys = ['start', 'end', 'text']
            for key in required_segment_keys:
                if key not in segment:
                    raise ValidationError('segment', segment, f"must contain '{key}'")
```

## Phase 3: Core Processors (Days 6-9)

### ⚠️ INTEGRATION RISK ANALYSIS

**Critical Integration Points**:
1. **Node.js → Python**: Subprocess communication via stdout/stderr
2. **Python → File System**: JSON files read by multiple processes
3. **File System → Node.js**: Results aggregation

**Failure Modes**:
1. **Subprocess Buffer Overflow**: Large videos produce >10MB JSON
2. **Race Conditions**: Node.js reads while Python writes
3. **Partial Writes**: Process killed mid-write corrupts JSON

**Mitigation**:
```python
# Atomic file writes
import tempfile
import shutil

def save_json_atomic(path: Path, data: Dict):
    # Write to temp file first
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name
    
    # Atomic move
    shutil.move(tmp_path, path)
```

### 3.1 Temporal Marker Processor

**File**: `rumiai_v2/processors/temporal_markers.py`

```python
from typing import Dict, Any, List, Optional
from ..core.models import Timestamp, Timeline, UnifiedAnalysis
from ..core.exceptions import MLAnalysisError
import logging

logger = logging.getLogger(__name__)

class TemporalMarkerProcessor:
    """Generate temporal markers from unified analysis."""
    
    def generate_markers(self, analysis: UnifiedAnalysis) -> Dict[str, Any]:
        """Generate temporal markers for video.
        
        CRITICAL: This is called by Node.js via subprocess.
        MUST output valid JSON to stdout even on error.
        """
        try:
            # Extract data from ML results
            yolo_data = analysis.get_ml_data('yolo')
            whisper_data = analysis.get_ml_data('whisper')
            ocr_data = analysis.get_ml_data('ocr')
            
            if not all([yolo_data, whisper_data, ocr_data]):
                raise MLAnalysisError('temporal_markers', 'Missing required ML data')
            
            # Generate markers for different time windows
            markers = {
                'first_5_seconds': self._analyze_opening(analysis, 0, 5),
                'cta_window': self._analyze_cta_window(analysis),
                'peak_moments': self._find_peak_moments(analysis),
                'metadata': {
                    'video_id': analysis.video_id,
                    'duration': analysis.timeline.duration,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
            return markers
            
        except Exception as e:
            # CRITICAL: Log to stderr only, not stdout
            logger.error(f"Temporal marker generation failed: {str(e)}")
            # ALWAYS return valid JSON structure
            return self._get_empty_markers(analysis.video_id)
    
    def _analyze_opening(self, analysis: UnifiedAnalysis, start: float, end: float) -> Dict[str, Any]:
        """Analyze opening seconds of video."""
        timeline_entries = analysis.timeline.get_entries_in_range(start, end)
        
        return {
            'density_progression': self._calculate_density_progression(timeline_entries, start, end),
            'text_moments': self._extract_text_moments(timeline_entries),
            'emotion_sequence': self._extract_emotion_sequence(timeline_entries),
            'gesture_moments': self._extract_gesture_moments(timeline_entries),
            'object_appearances': self._extract_object_appearances(timeline_entries)
        }
    
    def _calculate_density_progression(self, entries: List[Any], start: float, end: float) -> List[int]:
        """Calculate information density per second."""
        duration = int(end - start)
        density = [0] * duration
        
        for i in range(duration):
            second_start = start + i
            second_end = start + i + 1
            
            # Count events in this second
            count = sum(
                1 for entry in entries
                if entry.start.seconds >= second_start and entry.start.seconds < second_end
            )
            density[i] = min(count, 10)  # Cap at 10 for normalization
        
        return density
    
    def _get_empty_markers(self, video_id: str) -> Dict[str, Any]:
        """Return empty but valid marker structure."""
        return {
            'first_5_seconds': {
                'density_progression': [0, 0, 0, 0, 0],
                'text_moments': [],
                'emotion_sequence': ['neutral'] * 5,
                'gesture_moments': [],
                'object_appearances': []
            },
            'cta_window': {
                'time_range': 'last 15%',
                'cta_appearances': [],
                'gesture_sync': [],
                'object_focus': []
            },
            'peak_moments': [],
            'metadata': {
                'video_id': video_id,
                'error': 'Generation failed - empty markers returned'
            }
        }
```

### 3.2 ML Data Extractor

**File**: `rumiai_v2/processors/ml_data_extractor.py`

```python
from typing import Dict, Any, List, Optional
from enum import Enum
from ..core.models import UnifiedAnalysis, Timeline, TimelineEntry
from ..core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class PromptType(Enum):
    CREATIVE_DENSITY = "creative_density"
    EMOTIONAL_JOURNEY = "emotional_journey"
    SPEECH_ANALYSIS = "speech_analysis"
    VISUAL_OVERLAY = "visual_overlay_analysis"
    METADATA_ANALYSIS = "metadata_analysis"
    PERSON_FRAMING = "person_framing"
    SCENE_PACING = "scene_pacing"

class MLDataExtractor:
    """Extract relevant ML data for each prompt type."""
    
    def extract_for_prompt(self, analysis: UnifiedAnalysis, prompt_type: PromptType) -> Dict[str, Any]:
        """Extract ML data specific to prompt type."""
        
        # Base context all prompts need
        base_context = {
            'video_id': analysis.video_id,
            'duration': analysis.timeline.duration,
            'metadata': analysis.video_metadata
        }
        
        # Prompt-specific extractors
        extractors = {
            PromptType.CREATIVE_DENSITY: self._extract_creative_density,
            PromptType.EMOTIONAL_JOURNEY: self._extract_emotional_journey,
            PromptType.SPEECH_ANALYSIS: self._extract_speech_analysis,
            PromptType.VISUAL_OVERLAY: self._extract_visual_overlay,
            PromptType.METADATA_ANALYSIS: self._extract_metadata_analysis,
            PromptType.PERSON_FRAMING: self._extract_person_framing,
            PromptType.SCENE_PACING: self._extract_scene_pacing
        }
        
        if prompt_type not in extractors:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        # Extract prompt-specific data
        prompt_data = extractors[prompt_type](analysis)
        
        # Merge with base context
        return {**base_context, **prompt_data}
    
    def _extract_creative_density(self, analysis: UnifiedAnalysis) -> Dict[str, Any]:
        """Extract data for creative density analysis."""
        ocr_data = analysis.get_ml_data('ocr') or {}
        
        # Extract text timeline
        text_timeline = {}
        for entry in analysis.timeline.get_entries_by_type('text'):
            timestamp_key = f"{int(entry.start.seconds)}s"
            text_timeline[timestamp_key] = entry.data.get('text', '')
        
        # Extract sticker timeline
        sticker_timeline = {}
        if 'stickers' in ocr_data:
            for sticker in ocr_data.get('stickers', []):
                if 'timestamp' in sticker:
                    ts = Timestamp.from_value(sticker['timestamp'])
                    if ts:
                        timestamp_key = f"{int(ts.seconds)}s"
                        sticker_timeline[timestamp_key] = sticker
        
        return {
            'text_timeline': text_timeline,
            'sticker_timeline': sticker_timeline,
            'text_density': self._calculate_text_density(analysis),
            'creative_elements_count': len(text_timeline) + len(sticker_timeline)
        }
    
    def _calculate_text_density(self, analysis: UnifiedAnalysis) -> List[float]:
        """Calculate text density over time."""
        # 10-second buckets
        bucket_size = 10
        num_buckets = int(analysis.timeline.duration / bucket_size) + 1
        density = [0.0] * num_buckets
        
        text_entries = analysis.timeline.get_entries_by_type('text')
        for entry in text_entries:
            bucket_idx = int(entry.start.seconds / bucket_size)
            if bucket_idx < num_buckets:
                density[bucket_idx] += 1
        
        # Normalize
        max_density = max(density) if density else 1
        if max_density > 0:
            density = [d / max_density for d in density]
        
        return density
```

### 3.3 Timeline Builder

**File**: `rumiai_v2/processors/timeline_builder.py`

```python
from typing import Dict, Any, List, Optional
from ..core.models import Timeline, TimelineEntry, Timestamp, UnifiedAnalysis, MLAnalysisResult
from ..core.validators import MLDataValidator
from ..core.exceptions import ValidationError, TimelineError
import logging

logger = logging.getLogger(__name__)

class TimelineBuilder:
    """Build unified timeline from ML analysis results."""
    
    def __init__(self):
        self.validator = MLDataValidator()
    
    def build_timeline(self, video_id: str, video_metadata: Dict[str, Any], 
                      ml_results: Dict[str, MLAnalysisResult]) -> UnifiedAnalysis:
        """Build complete unified analysis with timeline."""
        
        # Extract video duration
        duration = video_metadata.get('duration', 0)
        if duration <= 0:
            raise ValidationError('duration', duration, 'positive number')
        
        # Create timeline
        timeline = Timeline(video_id=video_id, duration=float(duration))
        
        # Add entries from each ML model
        builders = {
            'yolo': self._add_yolo_entries,
            'whisper': self._add_whisper_entries,
            'ocr': self._add_ocr_entries,
            'mediapipe': self._add_mediapipe_entries,
            'scene_detection': self._add_scene_entries
        }
        
        for model_name, builder_func in builders.items():
            if model_name in ml_results and ml_results[model_name].success:
                try:
                    builder_func(timeline, ml_results[model_name].data)
                    logger.info(f"Added {model_name} entries to timeline")
                except Exception as e:
                    logger.error(f"Failed to add {model_name} entries: {str(e)}")
        
        # Create unified analysis
        analysis = UnifiedAnalysis(
            video_id=video_id,
            video_metadata=video_metadata,
            timeline=timeline,
            ml_results=ml_results
        )
        
        return analysis
    
    def _add_yolo_entries(self, timeline: Timeline, yolo_data: Dict[str, Any]) -> None:
        """Add YOLO object detection entries."""
        self.validator.validate_yolo_data(yolo_data)
        
        for annotation in yolo_data.get('objectAnnotations', []):
            for frame_data in annotation.get('frames', []):
                timestamp = frame_data.get('timestamp')
                if not timestamp:
                    continue
                
                ts = Timestamp.from_value(timestamp)
                if not ts:
                    continue
                
                entry = TimelineEntry(
                    start=ts,
                    end=None,  # Object detection is instantaneous
                    entry_type='object',
                    data={
                        'class': annotation.get('class', 'unknown'),
                        'confidence': frame_data.get('confidence', 0),
                        'bbox': frame_data.get('bbox', [])
                    }
                )
                timeline.add_entry(entry)
    
    def _add_whisper_entries(self, timeline: Timeline, whisper_data: Dict[str, Any]) -> None:
        """Add Whisper transcription entries."""
        self.validator.validate_whisper_data(whisper_data)
        
        for segment in whisper_data.get('segments', []):
            start = Timestamp.from_value(segment.get('start'))
            end = Timestamp.from_value(segment.get('end'))
            
            if not start or not end:
                continue
            
            entry = TimelineEntry(
                start=start,
                end=end,
                entry_type='speech',
                data={
                    'text': segment.get('text', ''),
                    'confidence': segment.get('confidence', 0),
                    'language': whisper_data.get('language', 'unknown')
                }
            )
            timeline.add_entry(entry)
```

## Phase 4: API Clients (Days 10-11)

### ⚠️ EXTERNAL DEPENDENCY RISKS

**Critical Failures**:
1. **Claude API**: Rate limits, connection drops, response timeouts
2. **Apify API**: Token expiration, quota limits, service downtime
3. **Network**: DNS failures, proxy issues, SSL problems

**Current System Behavior**:
- Retries with exponential backoff
- Silent failures after max retries
- No tracking of API costs/usage

**Required Improvements**:
```python
class APIMetrics:
    def __init__(self):
        self.api_calls = defaultdict(int)
        self.api_costs = defaultdict(float)
        self.api_errors = defaultdict(list)
    
    def track_call(self, service: str, success: bool, cost: float = 0):
        self.api_calls[service] += 1
        self.api_costs[service] += cost
        if not success:
            self.api_errors[service].append(timestamp())
```

### 4.1 Claude Client

**File**: `rumiai_v2/api/claude_client.py`

```python
from typing import Dict, Any, Optional, List
import requests
import time
import json
from ..core.exceptions import APIError
import logging

logger = logging.getLogger(__name__)

class ClaudeClient:
    """Claude API client with retry logic and error handling."""
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.max_retries = 3
        self.base_delay = 5  # seconds
    
    def send_prompt(self, prompt: str, context_data: Dict[str, Any], 
                   timeout: int = 60) -> Dict[str, Any]:
        """Send prompt to Claude with context data."""
        
        messages = [{
            "role": "user",
            "content": self._build_prompt_content(prompt, context_data)
        }]
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        # CRITICAL: Track retry attempts for monitoring
        retry_metadata = {
            'video_id': context_data.get('video_id', 'unknown'),
            'prompt_type': context_data.get('prompt_type', 'unknown'),
            'attempts': []
        }
        
        for attempt in range(self.max_retries):
            attempt_start = time.time()
            try:
                # Create fresh session for each request
                with requests.Session() as session:
                    response = session.post(
                        self.api_url,
                        headers=headers,
                        json=request_data,
                        timeout=timeout
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    # Track successful API usage
                    usage = result.get('usage', {})
                    tokens = usage.get('total_tokens', 0)
                    estimated_cost = tokens * 0.00025  # Haiku pricing
                    
                    retry_metadata['attempts'].append({
                        'attempt': attempt + 1,
                        'status': 200,
                        'duration': time.time() - attempt_start,
                        'tokens': tokens,
                        'cost': estimated_cost
                    })
                    
                    return {
                        'success': True,
                        'response': result.get('content', [{}])[0].get('text', ''),
                        'usage': usage,
                        'retry_metadata': retry_metadata
                    }
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, retrying in {delay}s...")
                        time.sleep(delay)
                        continue
                else:
                    raise APIError('Claude', response.status_code, response.text)
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Connection error, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
                    continue
                else:
                    raise APIError('Claude', 0, f"Connection failed after {self.max_retries} attempts")
            except requests.exceptions.Timeout:
                raise APIError('Claude', 0, f"Request timed out after {timeout}s")
            except Exception as e:
                raise APIError('Claude', 0, f"Unexpected error: {str(e)}")
        
        return {
            'success': False,
            'error': f"Failed after {self.max_retries} attempts"
        }
    
    def _build_prompt_content(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """Build complete prompt with context."""
        # Format context data as structured text
        context_sections = []
        
        if 'metadata' in context_data:
            context_sections.append(f"VIDEO METADATA:\n{json.dumps(context_data['metadata'], indent=2)}")
        
        if 'text_timeline' in context_data:
            context_sections.append(f"TEXT TIMELINE:\n{json.dumps(context_data['text_timeline'], indent=2)}")
        
        if 'speech_segments' in context_data:
            context_sections.append(f"SPEECH:\n{json.dumps(context_data['speech_segments'], indent=2)}")
        
        # Add more sections as needed
        
        context_text = "\n\n".join(context_sections)
        
        return f"{prompt}\n\nCONTEXT DATA:\n{context_text}"
```

## Phase 5: Main Runner (Days 12-13)

### ⚠️ ORCHESTRATION FAILURE ANALYSIS

**Critical Failure Points**:
1. **Entry Point Compatibility**: Must work with existing Node.js calls
2. **Output Format**: Must match expected JSON structure exactly
3. **Exit Codes**: Node.js depends on specific exit codes
4. **Progress Tracking**: Node.js monitors stdout for progress

**Backward Compatibility Requirements**:
```python
# Must support both calling conventions:
# OLD: python run_video_prompts_validated_v2.py VIDEO_ID
# NEW: python scripts/rumiai_runner.py --video-url URL

if __name__ == "__main__":
    # Detect calling convention
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        # Legacy mode: VIDEO_ID provided
        video_id = sys.argv[1]
        # Load video data from existing files
        runner = RumiAIRunner(legacy_mode=True)
        result = runner.process_video_id(video_id)
    else:
        # New mode: full URL processing
        parser = argparse.ArgumentParser()
        parser.add_argument('--video-url', required=True)
        args = parser.parse_args()
        runner = RumiAIRunner()
        result = runner.process_video_url(args.video_url)
```

### 5.1 Main Entry Point

**File**: `scripts/rumiai_runner.py`

```python
#!/usr/bin/env python3
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rumiai_v2.api import ClaudeClient, ApifyClient, MLServices
from rumiai_v2.processors import (
    VideoAnalyzer, TimelineBuilder, TemporalMarkerProcessor,
    MLDataExtractor, PromptType
)
from rumiai_v2.config import Settings
from rumiai_v2.utils import FileHandler, Logger, Metrics

# Configure logging
logger = Logger.setup(__name__)

class RumiAIRunner:
    """Main orchestrator for RumiAI v2."""
    
    def __init__(self):
        self.settings = Settings()
        self.file_handler = FileHandler(self.settings.output_dir)
        self.metrics = Metrics()
        
        # Initialize clients
        self.apify = ApifyClient(self.settings.apify_token)
        self.claude = ClaudeClient(self.settings.claude_api_key)
        self.ml_services = MLServices()
        
        # Initialize processors
        self.video_analyzer = VideoAnalyzer(self.ml_services)
        self.timeline_builder = TimelineBuilder()
        self.temporal_processor = TemporalMarkerProcessor()
        self.ml_extractor = MLDataExtractor()
    
    async def process_video(self, video_url: str) -> Dict[str, Any]:
        """Process a single video through the entire pipeline.
        
        CRITICAL: This is the main orchestration function.
        Must maintain progress output format expected by Node.js:
        - Progress markers: "📊 step_name... (XX%)" 
        - Success markers: "✅ Step complete"
        - Error format: "❌ Step failed: reason"
        """
        
        # CRITICAL: Node.js parses this exact format
        print(f"🚀 Starting processing for: {video_url}")
        self.metrics.start_timer('total_processing')
        
        try:
            # Step 1: Scrape video metadata
            print("📊 scraping_metadata... (0%)")
            video_data = await self._scrape_video(video_url)
            video_id = video_data['id']
            print(f"✅ Video ID: {video_id}")
            
            # Step 2: Download video
            logger.info("Step 2: Downloading video...")
            video_path = await self._download_video(video_data)
            
            # Step 3: Run ML analysis
            logger.info("Step 3: Running ML analysis...")
            ml_results = await self._run_ml_analysis(video_id, video_path)
            
            # Step 4: Build unified timeline
            logger.info("Step 4: Building unified timeline...")
            unified_analysis = self.timeline_builder.build_timeline(
                video_id, video_data, ml_results
            )
            
            # Step 5: Generate temporal markers
            logger.info("Step 5: Generating temporal markers...")
            temporal_markers = self.temporal_processor.generate_markers(unified_analysis)
            unified_analysis.temporal_markers = temporal_markers
            
            # Step 6: Save unified analysis
            logger.info("Step 6: Saving unified analysis...")
            self._save_unified_analysis(unified_analysis)
            
            # Step 7: Run Claude prompts
            print("📊 running_claude_prompts... (70%)")
            # CRITICAL: Node.js expects specific progress format
            prompt_results = await self._run_claude_prompts(unified_analysis)
            
            # Step 8: Generate final report
            logger.info("Step 8: Generating final report...")
            report = self._generate_report(unified_analysis, prompt_results)
            
            self.metrics.stop_timer('total_processing')
            logger.info(f"Processing complete! Total time: {self.metrics.get_time('total_processing')}s")
            
            return {
                'success': True,
                'video_id': video_id,
                'report': report,
                'metrics': self.metrics.get_all()
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics.get_all()
            }
    
    async def _scrape_video(self, video_url: str) -> Dict[str, Any]:
        """Scrape video metadata from TikTok."""
        self.metrics.start_timer('scraping')
        result = await self.apify.scrape_video(video_url)
        self.metrics.stop_timer('scraping')
        return result
    
    async def _download_video(self, video_data: Dict[str, Any]) -> Path:
        """Download video file."""
        self.metrics.start_timer('download')
        video_path = await self.apify.download_video(
            video_data['downloadUrl'],
            video_data['id']
        )
        self.metrics.stop_timer('download')
        return video_path
    
    async def _run_ml_analysis(self, video_id: str, video_path: Path) -> Dict[str, Any]:
        """Run all ML analyses on video."""
        self.metrics.start_timer('ml_analysis')
        results = await self.video_analyzer.analyze_video(video_id, video_path)
        self.metrics.stop_timer('ml_analysis')
        return results
    
    async def _run_claude_prompts(self, analysis: UnifiedAnalysis) -> Dict[str, Any]:
        """Run all Claude prompts."""
        self.metrics.start_timer('claude_prompts')
        
        prompt_types = [
            PromptType.CREATIVE_DENSITY,
            PromptType.EMOTIONAL_JOURNEY,
            PromptType.SPEECH_ANALYSIS,
            PromptType.VISUAL_OVERLAY,
            PromptType.METADATA_ANALYSIS,
            PromptType.PERSON_FRAMING,
            PromptType.SCENE_PACING
        ]
        
        results = {}
        for i, prompt_type in enumerate(prompt_types):
            logger.info(f"Running prompt {i+1}/{len(prompt_types)}: {prompt_type.value}")
            
            try:
                # Extract relevant data
                context_data = self.ml_extractor.extract_for_prompt(analysis, prompt_type)
                
                # Get prompt template
                prompt_text = self.settings.get_prompt_template(prompt_type.value)
                
                # Send to Claude
                result = self.claude.send_prompt(
                    prompt_text,
                    context_data,
                    timeout=self.settings.prompt_timeouts.get(prompt_type.value, 60)
                )
                
                results[prompt_type.value] = result
                
                # Save individual result
                self._save_prompt_result(analysis.video_id, prompt_type.value, result)
                
                # Delay between prompts to avoid rate limits
                if i < len(prompt_types) - 1:
                    await asyncio.sleep(self.settings.prompt_delay)
                    
            except Exception as e:
                logger.error(f"Prompt {prompt_type.value} failed: {str(e)}")
                results[prompt_type.value] = {
                    'success': False,
                    'error': str(e)
                }
        
        self.metrics.stop_timer('claude_prompts')
        return results
    
    def _save_unified_analysis(self, analysis: UnifiedAnalysis) -> None:
        """Save unified analysis to disk."""
        output_path = self.file_handler.get_path(
            'unified_analysis',
            f"{analysis.video_id}.json"
        )
        self.file_handler.save_json(output_path, analysis.to_dict())
    
    def _save_prompt_result(self, video_id: str, prompt_name: str, result: Dict[str, Any]) -> None:
        """Save individual prompt result."""
        output_path = self.file_handler.get_path(
            'insights',
            video_id,
            prompt_name,
            f"{prompt_name}_result.json"
        )
        self.file_handler.save_json(output_path, result)
    
    def _generate_report(self, analysis: UnifiedAnalysis, prompt_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final analysis report."""
        successful_prompts = sum(1 for r in prompt_results.values() if r.get('success'))
        
        return {
            'video_id': analysis.video_id,
            'duration': analysis.timeline.duration,
            'ml_analyses_complete': analysis.is_complete(),
            'temporal_markers_generated': analysis.temporal_markers is not None,
            'prompts_successful': f"{successful_prompts}/{len(prompt_results)}",
            'processing_metrics': self.metrics.get_all()
        }

def main():
    """Main entry point.
    
    CRITICAL: Exit codes must match Node.js expectations:
    - 0: Success
    - 1: General failure  
    - 2: Invalid arguments
    - 3: API failure
    - 4: ML processing failure
    """
    if len(sys.argv) < 2:
        print("Usage: rumiai_runner.py <video_url>")
        sys.exit(2)  # Invalid arguments
    
    video_url = sys.argv[1]
    runner = RumiAIRunner()
    
    # Run async processing
    result = asyncio.run(runner.process_video(video_url))
    
    # Print result
    if result['success']:
        print(f"\n✅ Success! Video {result['video_id']} processed successfully.")
        print(f"Report: {json.dumps(result['report'], indent=2)}")
    else:
        print(f"\n❌ Failed! Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Phase 6: Testing Strategy (Days 14-15)

### ⚠️ AUTOMATED TESTING REQUIREMENTS

**Critical**: ALL tests must run without human intervention

### 6.0 Test Automation Setup

```bash
#!/bin/bash
# test_automation_setup.sh

# Create test environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements_test.txt

# Download test fixtures if not present
if [ ! -d "rumiai_v2/tests/fixtures/ml_outputs" ]; then
    echo "Downloading test fixtures..."
    wget -q https://storage.googleapis.com/rumiai-test-fixtures/fixtures.tar.gz
    tar -xzf fixtures.tar.gz -C rumiai_v2/tests/
    rm fixtures.tar.gz
fi

# Validate fixtures
python scripts/validate_fixtures.py || exit 1

# Run all tests
pytest -v --cov=rumiai_v2 --cov-report=html
```

### 6.1 Test Fixtures

**CRITICAL**: Test fixtures must cover all edge cases found in production

Create comprehensive test fixtures:

```bash
mkdir -p rumiai_v2/tests/fixtures/{video_metadata,ml_outputs,expected_outputs}

# Copy successful analysis outputs
cp unified_analysis/7374228033655393579.json rumiai_v2/tests/fixtures/expected_outputs/
cp object_detection_outputs/*/7374228033655393579*.json rumiai_v2/tests/fixtures/ml_outputs/
```

### 6.2 Unit Tests

**CRITICAL**: Unit tests must cover ALL timestamp formats found in production data

**File**: `rumiai_v2/tests/unit/test_timestamp.py`

```python
import pytest
from rumiai_v2.core.models import Timestamp

class TestTimestamp:
    def test_from_int(self):
        ts = Timestamp.from_value(5)
        assert ts.seconds == 5.0
    
    def test_from_float(self):
        ts = Timestamp.from_value(5.5)
        assert ts.seconds == 5.5
    
    def test_from_range_string(self):
        ts = Timestamp.from_value("0-1s")
        assert ts.seconds == 0.0  # Uses start of range
    
    def test_from_single_string(self):
        ts = Timestamp.from_value("5s")
        assert ts.seconds == 5.0
    
    def test_from_time_format(self):
        ts = Timestamp.from_value("1:30")
        assert ts.seconds == 90.0
    
    def test_from_none(self):
        ts = Timestamp.from_value(None)
        assert ts is None
    
    def test_invalid_format(self):
        # CHANGED: Don't raise, return None for invalid
        ts = Timestamp.from_value("invalid")
        assert ts is None
    
    def test_edge_cases_from_production(self):
        # Real formats found in production
        assert Timestamp.from_value("").is None  # Empty string
        assert Timestamp.from_value("0-1").seconds == 0.0  # Missing 's'
        assert Timestamp.from_value("1.5-2.5s").seconds == 1.5
        assert Timestamp.from_value("00:00:30").seconds == 30.0  # HH:MM:SS
        assert Timestamp.from_value("-1s") is None  # Negative
    
    def test_comparison(self):
        ts1 = Timestamp(5.0)
        ts2 = Timestamp(10.0)
        assert ts1 < ts2
        assert not ts2 < ts1
```

### 6.3 Integration Tests

**CRITICAL**: Must test the complete automated flow

```python
# rumiai_v2/tests/integration/test_full_pipeline.py
import subprocess
import json
import pytest
from pathlib import Path

class TestFullPipeline:
    """Test complete automated pipeline."""
    
    def test_node_js_compatibility(self, tmp_path):
        """Ensure new system works with existing Node.js flow."""
        # Use test video with known output
        test_video_url = "https://www.tiktok.com/@test/video/123"
        
        # Run through Node.js entry point
        result = subprocess.run(
            ["node", "test_rumiai_complete_flow.js", test_video_url],
            capture_output=True,
            text=True,
            env={**os.environ, "RUMIAI_TEST_MODE": "true"}
        )
        
        # Verify exit code
        assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
        
        # Verify output format
        output = json.loads(result.stdout.splitlines()[-1])  # Last line is JSON
        assert output['success'] is True
        assert 'video_id' in output
        assert 'outputs' in output
    
    def test_legacy_python_call(self):
        """Ensure backward compatibility with old Python calls."""
        # Simulate Node.js calling Python directly
        result = subprocess.run(
            ["python", "scripts/rumiai_runner.py", "test_video_123"],
            capture_output=True,
            text=True
        )
        
        # Should work in legacy mode
        assert result.returncode == 0
```

### 6.4 Performance Tests

```python
# rumiai_v2/tests/performance/test_memory_usage.py
import psutil
import pytest

class TestMemoryUsage:
    def test_large_video_memory(self):
        """Ensure memory usage stays within bounds."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large video fixture (5+ minutes)
        runner = RumiAIRunner()
        result = runner.process_video_fixture('large_video.json')
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        assert memory_increase < 2048, f"Memory usage too high: {memory_increase}MB"
```

**File**: `rumiai_v2/tests/integration/test_pipeline.py`

```python
import pytest
from pathlib import Path
from rumiai_v2.processors import TimelineBuilder, TemporalMarkerProcessor

class TestPipeline:
    @pytest.fixture
    def sample_ml_results(self):
        # Load from fixtures
        return {
            'yolo': MLAnalysisResult(
                model_name='yolo',
                model_version='v8',
                success=True,
                data=load_fixture('ml_outputs/yolo_output.json')
            ),
            # Add other models...
        }
    
    def test_timeline_building(self, sample_ml_results):
        builder = TimelineBuilder()
        video_metadata = {'id': 'test123', 'duration': 60}
        
        analysis = builder.build_timeline('test123', video_metadata, sample_ml_results)
        
        assert analysis.video_id == 'test123'
        assert analysis.timeline.duration == 60.0
        assert len(analysis.timeline.entries) > 0
    
    def test_temporal_marker_generation(self, sample_ml_results):
        # Build timeline first
        builder = TimelineBuilder()
        analysis = builder.build_timeline('test123', {'duration': 60}, sample_ml_results)
        
        # Generate markers
        processor = TemporalMarkerProcessor()
        markers = processor.generate_markers(analysis)
        
        assert 'first_5_seconds' in markers
        assert 'cta_window' in markers
        assert markers['metadata']['video_id'] == 'test123'
```

## Migration Strategy

### ⚠️ ZERO-DOWNTIME MIGRATION PLAN

**Critical Requirement**: System must continue processing videos during migration

### Step 1: Create Compatibility Layer
```bash
#!/bin/bash
# migration/create_compatibility_layer.sh

# Create symlinks for backward compatibility
ln -sf scripts/rumiai_runner.py run_video_prompts_validated_v2.py
ln -sf rumiai_v2/processors/temporal_markers.py python/generate_temporal_markers_fixed.py

# Create adapter scripts
cat > run_video_prompts_adapter.py << 'EOF'
#!/usr/bin/env python3
"""Adapter for legacy calls."""
import sys
import subprocess

# Detect old vs new calling convention
if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
    # Legacy: python script.py VIDEO_ID
    video_id = sys.argv[1]
    subprocess.run([sys.executable, "scripts/rumiai_runner.py", "--video-id", video_id])
else:
    # New: python script.py --video-url URL
    subprocess.run([sys.executable, "scripts/rumiai_runner.py"] + sys.argv[1:])
EOF

chmod +x run_video_prompts_adapter.py
```

### Step 2: Parallel Testing Phase
```bash
#!/bin/bash  
# migration/test_parallel_systems.sh

# Run old and new systems in parallel
VIDEO_URL="$1"

# Run old system
echo "Running old system..."
node test_rumiai_complete_flow.js "$VIDEO_URL" > old_output.json 2>&1 &
OLD_PID=$!

# Run new system  
echo "Running new system..."
RUMIAI_USE_NEW_SYSTEM=true node test_rumiai_complete_flow.js "$VIDEO_URL" > new_output.json 2>&1 &
NEW_PID=$!

# Wait for both
wait $OLD_PID $NEW_PID

# Compare outputs
python migration/compare_outputs.py old_output.json new_output.json
```

### Step 2: Install New System
```bash
# Create new virtual environment
python -m venv venv_v2
source venv_v2/bin/activate

# Install dependencies
pip install -r requirements_v2.txt
```

### Step 3: Test with Fixtures
```bash
# Run unit tests
pytest rumiai_v2/tests/unit/

# Run integration tests with saved data
pytest rumiai_v2/tests/integration/

# Test single video with saved data (no API calls)
python scripts/test_single_video.py --use-fixtures 7374228033655393579
```

### Step 4: Atomic Cutover
```bash
#!/bin/bash
# migration/atomic_cutover.sh

# Pre-flight checks
echo "Running pre-flight checks..."
python scripts/preflight_checks.py || exit 1

# Create backup point
echo "Creating backup..."
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    old_system_archived/ \
    *.py \
    python/ \
    server/services/

# Atomic switch
echo "Switching to new system..."
mv run_video_prompts_validated_v2.py run_video_prompts_validated_v2.py.old
ln -sf scripts/rumiai_runner.py run_video_prompts_validated_v2.py

# Verify
echo "Verifying cutover..."
python migration/verify_cutover.py || {
    echo "Cutover failed, rolling back..."
    rm run_video_prompts_validated_v2.py
    mv run_video_prompts_validated_v2.py.old run_video_prompts_validated_v2.py
    exit 1
}

echo "Cutover complete!"
```

## Key Differences from Old System

1. **Single Timestamp Format**: Everything is float seconds internally
2. **Validation First**: All data validated before processing
3. **Error Boundaries**: Each component isolated, failures don't cascade
4. **One Implementation**: No duplicate temporal marker generators
5. **Type Safety**: Full type hints prevent data mismatches
6. **Structured Logging**: Easy to debug issues
7. **Metrics**: Track performance of each component
8. **Test Coverage**: Unit and integration tests

## Success Criteria

1. Temporal markers generate successfully for all videos
2. No TypeError from timestamp comparisons
3. All 7 Claude prompts complete without crashes
4. Clean JSON output (no stdout contamination)
5. < 5 minute processing time per video
6. Clear error messages when failures occur

## Common Pitfalls to Avoid

### ⚠️ LEARNED FROM PRODUCTION FAILURES

1. **Don't Mix Timestamp Formats**: Always convert to float seconds immediately
   ```python
   # WRONG: Comparing mixed formats
   if timestamp_str <= other_timestamp_int:  # TypeError!
   
   # RIGHT: Convert first
   if Timestamp.from_value(timestamp_str).seconds <= other_timestamp_int:
   ```

2. **Don't Trust External Data**: Always validate with defaults
   ```python
   # WRONG: Assume structure exists
   frames = yolo_data['objectAnnotations'][0]['frames']  # KeyError!
   
   # RIGHT: Safe navigation
   annotations = yolo_data.get('objectAnnotations', [])
   frames = annotations[0].get('frames', []) if annotations else []
   ```

3. **Don't Mix stdout/stderr**: Node.js parses stdout
   ```python
   # WRONG: Print debug to stdout
   print(f"Processing {video_id}...")  # Breaks JSON parsing!
   
   # RIGHT: Use stderr for logs
   print(f"Processing {video_id}...", file=sys.stderr)
   ```

4. **Don't Buffer Large Data**: Stream when possible
   ```python
   # WRONG: Load entire timeline in memory
   timeline_json = json.dumps(massive_timeline)  # OOM!
   
   # RIGHT: Stream to file
   with open(output_path, 'w') as f:
       json.dump(massive_timeline, f, indent=2)
   ```

5. **Don't Ignore Process Limits**: Respect subprocess boundaries
   ```python
   # WRONG: Unlimited output
   result = subprocess.run(cmd, capture_output=True)  # Hangs!
   
   # RIGHT: Set limits
   result = subprocess.run(cmd, capture_output=True, 
                          timeout=300, # 5 min max
                          env={**os.environ, 'PYTHONUNBUFFERED': '1'})
   ```

6. **Don't Assume Atomic Operations**: File writes can fail mid-way
   ```python
   # WRONG: Direct write
   with open(path, 'w') as f:
       json.dump(data, f)  # Partial write on crash!
   
   # RIGHT: Write to temp, then move
   with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as tmp:
       json.dump(data, tmp)
       temp_path = tmp.name
   shutil.move(temp_path, path)  # Atomic on same filesystem
   ```

## Maintenance Notes

1. **Adding New ML Models**: 
   - Add to `MLAnalysisResult` model
   - Add validator in `ml_data_validator.py`
   - Add timeline builder in `timeline_builder.py`

2. **Adding New Prompts**:
   - Add to `PromptType` enum
   - Add extractor method in `ml_data_extractor.py`
   - Add prompt template to `config/prompts.yaml`

3. **Debugging Issues**:
   - Check logs first (structured JSON logs)
   - Validate data at component boundaries
   - Use metrics to identify slow components

## Automated Deployment Script

```bash
#!/bin/bash
# deploy_big_bang_rewrite.sh

set -euo pipefail  # Exit on error

echo "🚀 RumiAI v2 Big Bang Deployment"
echo "================================"

# Phase 1: Environment Setup
echo "📦 Setting up environment..."
python -m venv venv_v2
source venv_v2/bin/activate
pip install -r requirements_v2.txt

# Phase 2: Run Tests
echo "🧪 Running test suite..."
pytest rumiai_v2/tests/ -v || {
    echo "❌ Tests failed, aborting deployment"
    exit 1
}

# Phase 3: Compatibility Check
echo "🔄 Checking backward compatibility..."
python migration/check_compatibility.py || {
    echo "❌ Compatibility check failed"
    exit 1  
}

# Phase 4: Deploy
echo "🚀 Deploying new system..."
./migration/atomic_cutover.sh

# Phase 5: Verify
echo "✅ Running smoke tests..."
python migration/smoke_tests.py || {
    echo "❌ Smoke tests failed, check logs"
    exit 1
}

echo "✨ Deployment complete!"
```

## Success Metrics Dashboard

```python
# monitoring/success_metrics.py
import json
from datetime import datetime, timedelta

class MetricsDashboard:
    """Track success metrics for the new system."""
    
    def __init__(self):
        self.metrics = {
            'temporal_markers_success_rate': 0,
            'prompt_completion_rate': 0,
            'average_processing_time': 0,
            'memory_peak_mb': 0,
            'api_costs_daily': 0
        }
    
    def check_health(self) -> bool:
        """Return True if all metrics are healthy."""
        return (
            self.metrics['temporal_markers_success_rate'] > 0.95 and
            self.metrics['prompt_completion_rate'] > 0.90 and
            self.metrics['average_processing_time'] < 300 and
            self.metrics['memory_peak_mb'] < 4096
        )
```

This plan provides a complete blueprint for rebuilding RumiAI v2 with a clean, maintainable architecture that:
1. **Maintains full automation** - No manual steps required
2. **Ensures backward compatibility** - Existing Node.js flows continue working
3. **Handles all edge cases** - Based on production failures
4. **Provides rollback capability** - Can revert if issues arise
5. **Includes comprehensive testing** - Automated test suite catches regressions