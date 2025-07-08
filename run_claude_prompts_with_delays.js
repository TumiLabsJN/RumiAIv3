const { exec } = require('child_process');
const path = require('path');

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runClaudePromptsWithDelays(videoId, options = {}) {
    const prompts = [
        'creative_density',
        'emotional_journey', 
        'speech_analysis',
        'visual_overlay_analysis',
        'metadata_analysis',
        'person_framing',
        'scene_pacing'
    ];
    
    const delayBetweenPrompts = options.delayMs || 5000; // 5 second delay by default
    const results = { successful: 0, failed: 0 };
    
    console.log(`\n🧠 Running ${prompts.length} Claude prompts with ${delayBetweenPrompts/1000}s delays\n`);
    
    for (let i = 0; i < prompts.length; i++) {
        const prompt = prompts[i];
        console.log(`[${i+1}/${prompts.length}] Running ${prompt}...`);
        
        try {
            await new Promise((resolve, reject) => {
                const cmd = `python run_claude_single_prompt.py ${videoId} ${prompt}`;
                exec(cmd, { cwd: __dirname }, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`❌ ${prompt} failed:`, error.message);
                        results.failed++;
                        resolve(); // Continue even if failed
                    } else {
                        console.log(`✅ ${prompt} completed`);
                        results.successful++;
                        resolve();
                    }
                });
            });
            
            // Add delay between prompts to avoid rate limiting
            if (i < prompts.length - 1) {
                console.log(`⏳ Waiting ${delayBetweenPrompts/1000}s before next prompt...`);
                await sleep(delayBetweenPrompts);
            }
        } catch (error) {
            console.error(`Error with ${prompt}:`, error);
            results.failed++;
        }
    }
    
    console.log(`\n📊 Results: ${results.successful} successful, ${results.failed} failed\n`);
    return results;
}

// Export for use in other scripts
module.exports = { runClaudePromptsWithDelays };

// Run if called directly
if (require.main === module) {
    const videoId = process.argv[2];
    if (!videoId) {
        console.error('Usage: node run_claude_prompts_with_delays.js <videoId>');
        process.exit(1);
    }
    
    runClaudePromptsWithDelays(videoId, { delayMs: 10000 }) // 10s delay
        .then(() => process.exit(0))
        .catch(err => {
            console.error(err);
            process.exit(1);
        });
}