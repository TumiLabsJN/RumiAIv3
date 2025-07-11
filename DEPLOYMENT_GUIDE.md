# RumiAI v2 Pure Big Bang Deployment Guide

## 🚀 Overview

This guide covers the deployment of the completely rewritten RumiAI v2 system. The Pure Big Bang implementation fixes all fundamental architectural flaws identified in the post-mortem.

## ✅ Pre-Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed  
- [ ] All API keys configured (.env file)
- [ ] Backup of any existing v1 data

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Run automated tests
./run_tests.sh

# Run end-to-end test
python test_e2e.py
```

## 🔄 Migration from v1

If you have existing RumiAI v1 data:

```bash
# Dry run first to see what will be migrated
python scripts/migrate_to_v2.py --dry-run

# Run actual migration (creates backups by default)
python scripts/migrate_to_v2.py
```

## 🎯 Usage

### Direct Python Usage (Recommended)

```bash
# Process new video from URL
python scripts/rumiai_runner.py https://www.tiktok.com/@user/video/123456789

# Process existing video by ID (legacy mode)
python scripts/rumiai_runner.py VIDEO_ID_HERE
```

### Node.js Integration

Update your `test_rumiai_complete_flow.js` to use the new runner:

```javascript
const { spawn } = require('child_process');

function processVideo(videoUrl) {
    return new Promise((resolve, reject) => {
        const child = spawn('python3', [
            'scripts/rumiai_runner.py',
            videoUrl,
            '--output-format', 'json'
        ]);
        
        let output = '';
        child.stdout.on('data', (data) => output += data);
        child.stderr.on('data', (data) => console.error(data.toString()));
        
        child.on('close', (code) => {
            if (code === 0) {
                resolve(JSON.parse(output));
            } else {
                reject(new Error(`Process exited with code ${code}`));
            }
        });
    });
}
```

### Using Compatibility Wrapper

For gradual migration:

```bash
# Check system compatibility
node scripts/compatibility_wrapper.js --check

# Process video with automatic v2 detection
node scripts/compatibility_wrapper.js https://www.tiktok.com/@user/video/123456789
```

## 🏗️ Architecture Changes

### Key Improvements

1. **Single Timestamp Format**: All timestamps are float seconds internally
2. **Fresh HTTP Sessions**: Each Claude API request uses a new session
3. **Unified Error Handling**: All errors return valid JSON
4. **Atomic File Operations**: Prevents corruption during concurrent access
5. **Single Source of Truth**: One implementation for each component

### Directory Structure

```
rumiai_v2_data/
├── unified/          # Unified analysis files
├── temporal/         # Temporal marker files  
├── insights/         # Claude prompt results
├── config/           # Configuration
└── logs/            # Application logs
```

## 🔍 Monitoring

### Check Processing Status

```python
# In your monitoring script
from rumiai_v2.utils import Metrics, VideoProcessingMetrics

metrics = VideoProcessingMetrics()
summary = metrics.get_summary()
print(f"Success rate: {summary['success_rate']*100:.1f}%")
print(f"Average cost per video: ${summary['cost_per_video']:.4f}")
```

### View Logs

```bash
# Application logs
tail -f rumiai_v2_data/logs/rumiai_v2.log

# Error logs only
grep ERROR rumiai_v2_data/logs/rumiai_v2.log
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Error: No module named 'rumiai_v2'**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Claude API Connection Errors**
   - Verify API key in .env file
   - Check network connectivity
   - The new implementation automatically retries transient failures

3. **Temporal Marker Generation Failures**
   - Check unified analysis file exists
   - Verify timeline has events
   - The new processor always returns valid JSON even on error

### Exit Codes

- `0`: Success
- `1`: General failure
- `2`: Invalid arguments  
- `3`: API failure
- `4`: ML processing failure

## 🔐 Security

- Never commit `.env` file
- API keys should have minimal required permissions
- Use read-only ML service endpoints
- Enable rate limiting on production

## 📊 Performance

Expected performance metrics:
- Video scraping: 2-5 seconds
- ML analysis: 10-30 seconds per model
- Claude prompts: 5-15 seconds each
- Total processing: 2-5 minutes per video

## 🎉 Success Criteria

Your deployment is successful when:
1. `./run_tests.sh` shows all tests passing
2. `python test_e2e.py` completes without errors
3. Processing a real TikTok URL produces unified analysis and temporal markers
4. No "No valid JSON output found" errors
5. No RemoteDisconnected errors

## 🆘 Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Run the compatibility checker
3. Verify all dependencies are installed
4. Ensure API keys are valid and have credits

## 🎯 Next Steps

After successful deployment:
1. Process a few test videos to verify stability
2. Monitor success rates and costs
3. Set up automated backups of `rumiai_v2_data/`
4. Consider implementing webhook notifications for failures

---

**Remember**: This is a complete rewrite. The old broken implementations are gone. Trust the new system - it's designed to be bulletproof! 🚀