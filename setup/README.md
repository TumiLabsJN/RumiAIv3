# RumiAI Setup Service

This directory contains automated setup scripts for preparing a fresh RumiAI environment.

## Quick Start

```bash
# Run the bootstrap script
python setup/bootstrap.py

# Verify the installation
python setup/verify_setup.py
```

## Scripts

### bootstrap.py
Main setup orchestrator that:
- Checks system requirements (Python 3.8+, Node.js, FFmpeg)
- Creates Python virtual environment
- Detects Python version and selects appropriate requirements file
- Installs Python packages from requirements.txt (or requirements_py312.txt for Python 3.12+)
- Automatically adds setuptools for Python 3.12 (required by deep-sort-realtime)
- Installs CLIP from GitHub (required special installation)
- Installs Node.js dependencies
- Validates .env configuration
- Verifies prompt templates exist
- Sets executable permissions for shell scripts
- Generates a setup report

### requirements_check.py
System requirements checker that validates:
- Python version (3.8+)
- Node.js and npm
- FFmpeg for video processing
- Available disk space (5GB+ recommended)
- Internet connectivity
- Git (optional)
- CUDA/GPU availability (optional)

### verify_setup.py
Post-setup verification that tests:
- Python package imports
- Node.js module availability
- API key configuration
- Model loading capabilities
- Directory structure integrity

## Setup Process

1. **System Requirements**
   - Python 3.8 or higher
   - Node.js 14+ and npm
   - FFmpeg (for video processing)
   - 5GB+ free disk space
   - Internet connection (for model downloads)

2. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Add your API keys:
     - `ANTHROPIC_API_KEY`: Your Anthropic API key
     - `APIFY_TOKEN`: Your Apify token for TikTok scraping

3. **Running Setup**
   ```bash
   # From the project root directory
   python setup/bootstrap.py
   ```

4. **Verification**
   ```bash
   python setup/verify_setup.py
   ```

5. **Starting the Service**
   ```bash
   node test_rumiai_complete_flow.js
   ```

## Troubleshooting

### Python Package Installation Fails
- Ensure Python 3.8+ is installed
- Check internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`

### Node.js Modules Not Found
- Ensure Node.js 14+ is installed
- Delete `node_modules` and `package-lock.json`, then run setup again

### API Key Errors
- Check `.env` file exists
- Ensure API keys are not placeholder values
- Keys should not have quotes around them

### Model Download Issues
- Ensure stable internet connection
- Check available disk space (5GB+ needed)
- Models download on first use, be patient

## Setup Report

After running bootstrap.py, check `setup/setup_report.txt` for:
- Detailed status of each setup step
- List of any errors or warnings
- Recommended next steps

## Manual Setup (If Automated Fails)

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   pip install git+https://github.com/openai/CLIP.git
   ```

3. Install Node modules:
   ```bash
   npm install
   ```

4. Create `.env` from `.env.example` and add your API keys

5. Verify prompt templates exist in `prompt_templates/`