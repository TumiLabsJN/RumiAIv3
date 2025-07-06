#!/usr/bin/env node

/**
 * Resume Analysis - Creates unified analysis from existing component files
 * Use this when the main process was interrupted
 */

const fs = require('fs').promises;
const path = require('path');

async function findAnalysisFiles(videoId) {
    const files = {
        speech: `speech_transcriptions/${videoId}_whisper.json`,
        human: `human_analysis_outputs/${videoId}_1/${videoId}_1_human_analysis.json`,
        enhanced: `enhanced_human_analysis_outputs/${videoId}/${videoId}_enhanced_human_analysis.json`,
        scenes: `local_analysis_outputs/scene_detection_outputs/${videoId}/${videoId}_scenes.json`,
        labels: `local_analysis_outputs/scene_labels/${videoId}_labels.json`
    };
    
    const found = {};
    for (const [key, filePath] of Object.entries(files)) {
        try {
            await fs.access(filePath);
            found[key] = filePath;
            console.log(`✅ Found ${key}: ${filePath}`);
        } catch {
            console.log(`❌ Missing ${key}: ${filePath}`);
        }
    }
    
    return found;
}

async function createUnifiedAnalysis(videoId) {
    console.log(`🔄 Creating unified analysis for video: ${videoId}`);
    
    const files = await findAnalysisFiles(videoId);
    
    if (Object.keys(files).length < 3) {
        console.error('❌ Not enough analysis files found. Need at least 3 components.');
        return false;
    }
    
    // Load all available data
    const unified = {
        video_id: videoId,
        created_at: new Date().toISOString(),
        timelines: {},
        metadata: {},
        analysis_type: 'resumed'
    };
    
    // Load speech timeline
    if (files.speech) {
        const speechData = JSON.parse(await fs.readFile(files.speech, 'utf8'));
        unified.timelines.speechTimeline = speechData.speechTranscriptions || {};
    }
    
    // Load human analysis
    if (files.human) {
        const humanData = JSON.parse(await fs.readFile(files.human, 'utf8'));
        unified.timelines.expressionTimeline = humanData.timelines?.expressionTimeline || {};
        unified.timelines.gestureTimeline = humanData.timelines?.gestureTimeline || {};
    }
    
    // Load enhanced analysis
    if (files.enhanced) {
        const enhancedData = JSON.parse(await fs.readFile(files.enhanced, 'utf8'));
        unified.duration_seconds = enhancedData.total_frames / 3; // Approximate
        unified.insights = enhancedData.summary || {};
    }
    
    // Load scene data
    if (files.scenes) {
        const sceneData = JSON.parse(await fs.readFile(files.scenes, 'utf8'));
        unified.timelines.sceneChangeTimeline = sceneData.scenes || {};
    }
    
    // Save unified analysis
    const outputDir = 'unified_analysis';
    await fs.mkdir(outputDir, { recursive: true });
    const outputPath = path.join(outputDir, `${videoId}.json`);
    
    await fs.writeFile(outputPath, JSON.stringify(unified, null, 2));
    console.log(`✅ Unified analysis created: ${outputPath}`);
    
    return true;
}

async function runClaudePrompts(videoId) {
    console.log('🤖 Running Claude prompts...');
    
    try {
        const { execSync } = require('child_process');
        execSync(`python3 run_video_prompts_validated.py ${videoId}`, {
            stdio: 'inherit'
        });
        console.log('✅ Claude insights generated');
    } catch (error) {
        console.error('❌ Error running Claude prompts:', error.message);
    }
}

async function main() {
    const videoId = process.argv[2];
    
    if (!videoId) {
        console.log('Usage: node resume_analysis.js <video_id>');
        console.log('Example: node resume_analysis.js 7499329767292914975');
        process.exit(1);
    }
    
    const success = await createUnifiedAnalysis(videoId);
    
    if (success) {
        console.log('\n📊 Unified analysis created successfully!');
        console.log('🤖 Starting Claude prompt generation...\n');
        await runClaudePrompts(videoId);
    }
}

main().catch(console.error);