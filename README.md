# RumiAI v2 - TikTok Video Analysis Pipeline

A comprehensive pipeline for analyzing TikTok videos using multiple AI models and generating insights.

## Features

- **TikTok Video Scraping**: Automated video download from TikTok URLs
- **Multi-Model Analysis**:
  - Speech transcription (Whisper)
  - Object detection and tracking (YOLO + DeepSort)
  - Human pose and gesture analysis (MediaPipe)
  - Text extraction (EasyOCR)
  - Scene detection and labeling (PySceneDetect + CLIP)
  - Content moderation (OpenNSFW2)
- **AI-Powered Insights**: 7 specialized Claude prompts for comprehensive analysis
- **Unified Timeline**: Synchronized multi-modal analysis results

## Prerequisites

- Node.js v14+
- Python 3.8+
- FFmpeg
- Tesseract OCR

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/TumiLabsJN/RumiAIv2.git
cd RumiAIv2
```

### 2. Install system dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg tesseract-ocr

# macOS
brew install ffmpeg tesseract
```

### 3. Setup Python environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git
```

### 4. Install Node dependencies
```bash
npm install
```

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - APIFY_TOKEN (required)
# - ANTHROPIC_API_KEY (required)
```

### 6. Run the analysis
```bash
node test_rumiai_complete_flow.js https://www.tiktok.com/@username/video/123456789
```

## Usage

### Basic usage
```bash
node test_rumiai_complete_flow.js <TikTok-Video-URL>
```

### Examples
```bash
# Analyze a specific video (no query parameters)
node test_rumiai_complete_flow.js https://www.tiktok.com/@cristiano/video/7515739984452701457

# Analyze a video with query parameters (MUST use quotes!)
node test_rumiai_complete_flow.js "https://www.tiktok.com/@user/video/123456789?q=search&t=12345"

# Use default test video
node test_rumiai_complete_flow.js
```

⚠️ **Important**: URLs containing `&` characters (common with query parameters) MUST be wrapped in quotes to prevent shell interpretation issues.

## Output Structure

The analysis creates the following outputs:

```
├── temp/                    # Downloaded videos
├── frame_outputs/           # Extracted video frames
├── unified_analysis/        # Consolidated timeline data
├── insights/               # Claude AI analysis results
│   └── <video_id>/
│       ├── creative_density/
│       ├── emotional_journey/
│       ├── metadata_analysis/
│       ├── person_framing/
│       ├── scene_pacing/
│       ├── speech_analysis/
│       └── visual_overlay_analysis/
└── [other_analysis_outputs]/
```

## API Keys Required

1. **Apify Token**: For TikTok video scraping
   - Sign up at [apify.com](https://apify.com)
   - Get your API token from Account Settings

2. **Anthropic API Key**: For Claude AI analysis
   - Sign up at [anthropic.com](https://anthropic.com)
   - Get your API key from the console

## Troubleshooting

### Common Issues

1. **"No module named 'whisper'"**
   ```bash
   pip install openai-whisper
   ```

2. **"ffmpeg not found"**
   - Install ffmpeg for your system (see Prerequisites)

3. **CUDA/GPU errors**
   - The pipeline works on CPU by default
   - For GPU support, install PyTorch with CUDA support

4. **Memory issues**
   - Reduce video resolution or duration
   - Process videos one at a time

## Development

### Running with Docker
```bash
docker build -t rumiai .
docker run -it --env-file .env rumiai <video-url>
```

### Project Structure
```
├── test_rumiai_complete_flow.js    # Main entry point
├── server/services/                # Core services
│   ├── TikTokSingleVideoScraper.js
│   ├── VideoAnalysisService.js
│   └── ...
├── local_analysis/                 # Python analysis modules
│   ├── enhanced_human_analyzer.py
│   ├── object_tracking.py
│   └── ...
├── prompt_templates/               # Claude AI prompts
└── requirements.txt               # Python dependencies
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.