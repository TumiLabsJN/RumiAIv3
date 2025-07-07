# GPU Acceleration Setup for RumiAI

## Overview
GPU acceleration can speed up OCR processing by 10-30x, reducing analysis time from minutes to seconds.

## Requirements
- NVIDIA GPU with at least 2GB VRAM
- CUDA 11.8 or higher
- PyTorch with CUDA support

## Setup Instructions

### 1. Check GPU Availability
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"}')"
```

### 2. Install CUDA-enabled PyTorch
```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 3. Verify Installation
```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should output: True
```

## Usage

### Automatic GPU Detection (Default)
The system automatically detects and uses GPU if available:
```bash
node test_rumiai_complete_flow.js "https://www.tiktok.com/@user/video/123"
```

### Force GPU Mode
```bash
export RUMIAI_USE_GPU=true
node test_rumiai_complete_flow.js "https://www.tiktok.com/@user/video/123"
```

### Force CPU Mode
```bash
export RUMIAI_USE_GPU=false
node test_rumiai_complete_flow.js "https://www.tiktok.com/@user/video/123"
```

## Performance Comparison

| Mode | Frames | Processing Time | Speed per Frame |
|------|--------|----------------|-----------------|
| CPU  | 9      | 90-270s        | 10-30s         |
| GPU  | 9      | 5-18s          | 0.5-2s         |

## Memory Usage
- EasyOCR on GPU: ~2.2GB VRAM
- Total pipeline with GPU: ~3.6GB VRAM
- Recommended: 4GB+ VRAM for comfortable operation

## Troubleshooting

### "CUDA out of memory" Error
- Reduce batch size or close other GPU applications
- Monitor GPU memory: `nvidia-smi`

### "No CUDA-capable device" Error
- Ensure NVIDIA drivers are installed: `nvidia-smi`
- Check PyTorch CUDA version matches your system

### Slow GPU Performance
- First run downloads models (one-time delay)
- Ensure GPU is not thermal throttling
- Check GPU utilization: `watch -n 1 nvidia-smi`

## Environment Variables
- `RUMIAI_USE_GPU`: Control GPU usage (auto/true/false)
- Default: `auto` (use GPU if available)