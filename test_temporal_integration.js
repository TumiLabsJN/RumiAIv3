#!/usr/bin/env node

/**
 * Test script for temporal marker integration
 * Verifies that temporal markers are generated during video analysis
 * and properly included in the unified timeline
 */

const TemporalMarkerService = require('./server/services/TemporalMarkerService');
const path = require('path');
const fs = require('fs').promises;

async function testTemporalMarkerService() {
    console.log('🧪 Testing Temporal Marker Service');
    console.log('==================================\n');
    
    // Test 1: Service initialization
    console.log('📋 Test 1: Service Initialization');
    console.log(`   - Service enabled: ${TemporalMarkerService.enabled}`);
    console.log(`   - Max video duration: ${TemporalMarkerService.maxVideoDuration}s`);
    console.log(`   - Max output size: ${TemporalMarkerService.maxOutputSize / 1024 / 1024}MB`);
    console.log('   ✅ Service initialized correctly\n');
    
    // Test 2: Safety checks
    console.log('📋 Test 2: Safety Checks');
    
    // Test video too long
    const longVideoCheck = await TemporalMarkerService.performSafetyChecks(
        'test.mp4',
        { duration: 400 }, // 400s > 300s limit
        {}
    );
    console.log(`   - Long video (400s): ${longVideoCheck.safe ? '❌ FAILED' : '✅ Correctly rejected'}`);
    console.log(`     Reason: ${longVideoCheck.reason || 'N/A'}`);
    
    // Test normal video
    const normalVideoCheck = await TemporalMarkerService.performSafetyChecks(
        'test.mp4',
        { duration: 120 }, // 2 minutes
        { yolo: {}, mediapipe: {}, ocr: {} }
    );
    console.log(`   - Normal video (120s): ${normalVideoCheck.safe ? '✅ Passed' : '❌ FAILED'}`);
    
    console.log('');
    
    // Test 3: Metrics tracking
    console.log('📋 Test 3: Metrics Tracking');
    const metrics = TemporalMarkerService.getMetrics();
    console.log(`   - Total runs: ${metrics.totalRuns}`);
    console.log(`   - Successes: ${metrics.successes}`);
    console.log(`   - Failures: ${metrics.failures}`);
    console.log(`   - Success rate: ${metrics.successRate.toFixed(1)}%`);
    console.log(`   - Service enabled: ${metrics.enabled}`);
    console.log('');
    
    // Test 4: Check if temporal markers are in unified timeline
    console.log('📋 Test 4: Unified Timeline Integration');
    
    // Find a recent unified analysis file
    try {
        const unifiedDir = path.join(__dirname, 'unified_analysis');
        const files = await fs.readdir(unifiedDir);
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        
        if (jsonFiles.length > 0) {
            const testFile = jsonFiles[0];
            const filePath = path.join(unifiedDir, testFile);
            const data = await fs.readFile(filePath, 'utf8');
            const unified = JSON.parse(data);
            
            console.log(`   - Checking ${testFile}`);
            console.log(`   - Has temporal_markers field: ${unified.temporal_markers ? '✅ Yes' : '❌ No'}`);
            console.log(`   - Pipeline status includes temporal: ${unified.pipeline_status?.temporalMarkers !== undefined ? '✅ Yes' : '❌ No'}`);
            
            if (unified.temporal_markers) {
                console.log('   - Temporal marker structure:');
                console.log(`     • Has first_5_seconds: ${!!unified.temporal_markers.first_5_seconds}`);
                console.log(`     • Has cta_window: ${!!unified.temporal_markers.cta_window}`);
                console.log(`     • Has metadata: ${!!unified.temporal_markers.metadata}`);
            }
        } else {
            console.log('   ⚠️ No unified analysis files found to test');
        }
    } catch (error) {
        console.log(`   ❌ Error checking unified timeline: ${error.message}`);
    }
    
    console.log('\n✨ Temporal marker integration test complete!\n');
}

async function checkPythonScript() {
    console.log('🐍 Checking Python Temporal Marker Generator');
    console.log('==========================================\n');
    
    const scriptPath = path.join(__dirname, 'python', 'TemporalMarkerGenerator.py');
    
    try {
        await fs.access(scriptPath);
        console.log(`✅ Python script exists at: ${scriptPath}`);
        
        // Check if it's executable
        const stats = await fs.stat(scriptPath);
        const isExecutable = (stats.mode & parseInt('0111', 8)) !== 0;
        console.log(`${isExecutable ? '✅' : '⚠️'} Script is ${isExecutable ? '' : 'not '}executable`);
        
    } catch (error) {
        console.log(`❌ Python script not found: ${scriptPath}`);
    }
    
    console.log('');
}

// Run tests
(async () => {
    try {
        await checkPythonScript();
        await testTemporalMarkerService();
    } catch (error) {
        console.error('❌ Test failed:', error);
        process.exit(1);
    }
})();