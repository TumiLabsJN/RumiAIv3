const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const crypto = require('crypto');

/**
 * TemporalMarkerService - Generates temporal markers for video analysis
 * Includes comprehensive safety measures for production deployment
 */
class TemporalMarkerService {
    constructor() {
        this.pythonPath = path.join(__dirname, '../../venv/bin/python');
        this.pythonScriptsPath = path.join(__dirname, '../../python');
        this.outputPath = path.join(__dirname, '../../temporal_markers');
        
        // Circuit breaker pattern for graceful degradation
        this.failures = 0;
        this.maxFailures = 3;
        this.enabled = true;
        this.resetTimeout = null;
        
        // Memory safety limits
        this.maxVideoDuration = 300; // 5 minutes max
        this.maxOutputSize = 10 * 1024 * 1024; // 10MB max output
        
        // Performance tracking
        this.metrics = {
            totalRuns: 0,
            successes: 0,
            failures: 0,
            totalTime: 0,
            memoryPeaks: []
        };
        
        this.ensureOutputDirectory();
    }
    
    async ensureOutputDirectory() {
        try {
            await fs.mkdir(this.outputPath, { recursive: true });
            console.log('📁 Temporal markers output directory ready');
        } catch (error) {
            console.error('Failed to create temporal markers directory:', error);
        }
    }
    
    /**
     * Generate temporal markers with comprehensive safety checks
     */
    async generateTemporalMarkers(videoPath, videoId, metadata, dependencies = {}) {
        // Circuit breaker check
        if (!this.enabled) {
            console.warn('⚠️ Temporal markers disabled due to repeated failures');
            return null;
        }
        
        const startTime = Date.now();
        const runId = crypto.randomBytes(8).toString('hex');
        
        try {
            // Pre-flight checks
            const safetyCheck = await this.performSafetyChecks(videoPath, metadata, dependencies);
            if (!safetyCheck.safe) {
                console.warn(`⚠️ Temporal markers skipped: ${safetyCheck.reason}`);
                return null;
            }
            
            console.log(`🎯 Generating temporal markers for ${videoId} (run ${runId})`);
            
            // Run Python temporal marker generator
            const result = await this.runTemporalMarkerGenerator(
                videoPath, 
                videoId, 
                dependencies,
                runId
            );
            
            // Validate output
            const validation = await this.validateTemporalMarkers(result);
            if (!validation.valid) {
                throw new Error(`Invalid temporal markers: ${validation.reason}`);
            }
            
            // Save to disk
            const outputPath = await this.saveTemporalMarkers(videoId, result);
            
            // Update metrics
            this.recordSuccess(Date.now() - startTime);
            
            console.log(`✅ Temporal markers generated successfully: ${outputPath}`);
            
            return {
                success: true,
                data: result,
                outputPath,
                metrics: {
                    generationTime: Date.now() - startTime,
                    markerCount: this.countMarkers(result),
                    outputSize: Buffer.byteLength(JSON.stringify(result))
                }
            };
            
        } catch (error) {
            // Record failure
            this.recordFailure(error);
            
            console.error(`❌ Temporal marker generation failed for ${videoId}:`, error.message);
            
            // Return null for graceful degradation
            return null;
        }
    }
    
    /**
     * Perform comprehensive safety checks before processing
     */
    async performSafetyChecks(videoPath, metadata, dependencies) {
        const checks = [];
        
        // 1. Video duration check
        if (metadata && metadata.duration > this.maxVideoDuration) {
            return {
                safe: false,
                reason: `Video too long (${metadata.duration}s > ${this.maxVideoDuration}s)`
            };
        }
        
        // 2. Memory availability check
        const memCheck = await this.checkMemoryAvailability();
        if (!memCheck.sufficient) {
            return {
                safe: false,
                reason: 'Insufficient memory available'
            };
        }
        
        // 3. Required dependencies check
        const requiredDeps = ['yolo', 'mediapipe', 'ocr'];
        for (const dep of requiredDeps) {
            if (!dependencies[dep]) {
                console.warn(`⚠️ Missing dependency: ${dep} - temporal markers may be incomplete`);
            }
        }
        
        // 4. Frame extraction check
        const frameDir = path.join(__dirname, '../../frame_outputs', 
            path.basename(videoPath).replace('.mp4', ''));
        try {
            await fs.access(frameDir);
        } catch (error) {
            return {
                safe: false,
                reason: 'Frame extraction not completed'
            };
        }
        
        return { safe: true };
    }
    
    /**
     * Check available system memory
     */
    async checkMemoryAvailability() {
        try {
            const os = require('os');
            const freeMem = os.freemem();
            const totalMem = os.totalmem();
            const usagePercent = ((totalMem - freeMem) / totalMem) * 100;
            
            // Require at least 1GB free memory
            const minFreeMemory = 1024 * 1024 * 1024; // 1GB
            
            return {
                sufficient: freeMem > minFreeMemory,
                freeMemory: freeMem,
                usagePercent
            };
        } catch (error) {
            // If we can't check, assume it's safe
            return { sufficient: true };
        }
    }
    
    /**
     * Run the Python temporal marker generator with streaming output
     */
    async runTemporalMarkerGenerator(videoPath, videoId, dependencies, runId) {
        return new Promise((resolve, reject) => {
            // Use the fixed generator that handles actual data structures
            const script = path.join(this.pythonScriptsPath, 'generate_temporal_markers_fixed.py');
            
            // Prepare dependency paths
            const depPaths = {
                yolo: dependencies.yolo?.outputPath || '',
                mediapipe: dependencies.mediapipe?.outputPath || '',
                ocr: dependencies.ocr?.outputPath || '',
                enhancedHuman: dependencies.enhancedHuman?.outputPath || '',
                sceneDetection: dependencies.scenes?.outputPath || ''
            };
            
            const args = [
                script,
                '--video-path', videoPath,
                '--video-id', videoId,
                '--run-id', runId,
                '--deps', JSON.stringify(depPaths),
                '--compact-mode', process.env.TEMPORAL_COMPACT_MODE || 'false'
            ];
            
            const pythonProcess = spawn(this.pythonPath, args, {
                maxBuffer: this.maxOutputSize
            });
            
            let output = '';
            let errorOutput = '';
            let outputSize = 0;
            
            // Set timeout for long-running processes
            const timeout = setTimeout(() => {
                pythonProcess.kill('SIGTERM');
                reject(new Error(`Temporal marker generation timeout (60s)`));
            }, 60000); // 60 second timeout
            
            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
                outputSize += data.length;
                
                // Check output size limit
                if (outputSize > this.maxOutputSize) {
                    pythonProcess.kill('SIGTERM');
                    reject(new Error('Output size limit exceeded'));
                }
                
                // Stream progress updates
                const lines = data.toString().split('\n');
                for (const line of lines) {
                    if (line.includes('Progress:') || line.includes('Processing:')) {
                        console.log(`   ${line.trim()}`);
                    }
                }
            });
            
            pythonProcess.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });
            
            pythonProcess.on('close', (code) => {
                clearTimeout(timeout);
                
                if (code !== 0) {
                    reject(new Error(`Process failed with code ${code}: ${errorOutput}`));
                } else {
                    try {
                        // Parse JSON output
                        const jsonMatch = output.match(/\{[\s\S]*\}$/);
                        if (jsonMatch) {
                            const result = JSON.parse(jsonMatch[0]);
                            resolve(result);
                        } else {
                            reject(new Error('No valid JSON output found'));
                        }
                    } catch (parseError) {
                        reject(new Error(`Failed to parse output: ${parseError.message}`));
                    }
                }
            });
            
            pythonProcess.on('error', (error) => {
                clearTimeout(timeout);
                reject(error);
            });
        });
    }
    
    /**
     * Validate temporal marker structure and content
     */
    async validateTemporalMarkers(markers) {
        // Check basic structure
        if (!markers || typeof markers !== 'object') {
            return { valid: false, reason: 'Invalid markers object' };
        }
        
        // Required fields
        const requiredFields = ['first_5_seconds', 'cta_window', 'metadata'];
        for (const field of requiredFields) {
            if (!markers[field]) {
                return { valid: false, reason: `Missing required field: ${field}` };
            }
        }
        
        // Validate first_5_seconds structure
        const first5 = markers.first_5_seconds;
        if (!first5.density_progression || !Array.isArray(first5.density_progression)) {
            return { valid: false, reason: 'Invalid density_progression' };
        }
        
        // Validate timestamps are in correct format
        if (first5.text_moments) {
            for (const moment of first5.text_moments) {
                if (typeof moment.time !== 'number' || moment.time < 0) {
                    return { valid: false, reason: 'Invalid timestamp in text_moments' };
                }
            }
        }
        
        // Check output size
        const size = Buffer.byteLength(JSON.stringify(markers));
        if (size > this.maxOutputSize) {
            return { valid: false, reason: 'Output too large' };
        }
        
        return { valid: true };
    }
    
    /**
     * Save temporal markers to disk with compression if needed
     */
    async saveTemporalMarkers(videoId, markers) {
        const outputPath = path.join(this.outputPath, `${videoId}.json`);
        
        // Check if we need to compact
        const size = Buffer.byteLength(JSON.stringify(markers));
        let dataToSave = markers;
        
        if (size > 1024 * 1024) { // 1MB threshold
            console.log('📦 Compacting temporal markers due to size...');
            dataToSave = this.compactTemporalMarkers(markers);
        }
        
        await fs.writeFile(outputPath, JSON.stringify(dataToSave, null, 2));
        
        return outputPath;
    }
    
    /**
     * Compact temporal markers to reduce size
     */
    compactTemporalMarkers(markers) {
        const compacted = {
            ...markers,
            first_5_seconds: {
                ...markers.first_5_seconds,
                // Keep only essential data
                density_progression: markers.first_5_seconds.density_progression,
                text_moments: markers.first_5_seconds.text_moments?.slice(0, 5), // Top 5 only
                emotion_sequence: markers.first_5_seconds.emotion_sequence,
                gesture_moments: markers.first_5_seconds.gesture_moments?.slice(0, 3) // Top 3 only
            },
            cta_window: {
                ...markers.cta_window,
                cta_appearances: markers.cta_window.cta_appearances?.slice(0, 5), // Top 5 only
                gesture_sync: markers.cta_window.gesture_sync?.slice(0, 3) // Top 3 only
            }
        };
        
        // Remove raw frame data if present
        delete compacted._raw;
        delete compacted.frame_analysis;
        
        return compacted;
    }
    
    /**
     * Count total markers in the result
     */
    countMarkers(markers) {
        let count = 0;
        
        if (markers.first_5_seconds) {
            count += (markers.first_5_seconds.text_moments?.length || 0);
            count += (markers.first_5_seconds.gesture_moments?.length || 0);
            count += (markers.first_5_seconds.object_appearances?.length || 0);
        }
        
        if (markers.cta_window) {
            count += (markers.cta_window.cta_appearances?.length || 0);
            count += (markers.cta_window.gesture_sync?.length || 0);
        }
        
        return count;
    }
    
    /**
     * Record successful run for metrics
     */
    recordSuccess(duration) {
        this.metrics.totalRuns++;
        this.metrics.successes++;
        this.metrics.totalTime += duration;
        
        // Reset failure counter
        this.failures = 0;
        
        // Clear reset timeout if any
        if (this.resetTimeout) {
            clearTimeout(this.resetTimeout);
            this.resetTimeout = null;
        }
    }
    
    /**
     * Record failure and handle circuit breaker
     */
    recordFailure(error) {
        this.metrics.totalRuns++;
        this.metrics.failures++;
        this.failures++;
        
        // Circuit breaker logic
        if (this.failures >= this.maxFailures) {
            this.enabled = false;
            console.error(`🔴 Temporal markers disabled after ${this.failures} failures`);
            
            // Auto-reset after 5 minutes
            this.resetTimeout = setTimeout(() => {
                this.enabled = true;
                this.failures = 0;
                console.log('🟢 Temporal markers re-enabled after cooldown');
            }, 5 * 60 * 1000);
        }
    }
    
    /**
     * Get service metrics
     */
    getMetrics() {
        return {
            ...this.metrics,
            enabled: this.enabled,
            failureCount: this.failures,
            averageTime: this.metrics.successes > 0 
                ? this.metrics.totalTime / this.metrics.successes 
                : 0,
            successRate: this.metrics.totalRuns > 0
                ? (this.metrics.successes / this.metrics.totalRuns) * 100
                : 0
        };
    }
    
    /**
     * Check if temporal markers are available for a video
     */
    async hasTemporalMarkers(videoId) {
        try {
            const filePath = path.join(this.outputPath, `${videoId}.json`);
            await fs.access(filePath);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Load existing temporal markers
     */
    async loadTemporalMarkers(videoId) {
        try {
            const filePath = path.join(this.outputPath, `${videoId}.json`);
            const data = await fs.readFile(filePath, 'utf8');
            return JSON.parse(data);
        } catch (error) {
            return null;
        }
    }
}

// Export singleton instance
module.exports = new TemporalMarkerService();