#!/usr/bin/env node

require('dotenv').config();
const { ApifyClient } = require('apify-client');

const TEST_VIDEO_URL = 'https://www.tiktok.com/@aliasherbals/video/7522345762324237623';

async function checkVideoUrlFields() {
    console.log('🔍 Checking what video URL fields Apify returns\n');
    
    const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
    
    // Test without downloads
    const input = {
        postURLs: [TEST_VIDEO_URL],
        resultsPerPage: 1,
        shouldDownloadVideos: false,
        shouldDownloadCovers: false,
        shouldDownloadSubtitles: false,
        proxyConfiguration: { useApifyProxy: true }
    };
    
    console.log('🚀 Starting Apify run (no downloads)...');
    const run = await client.actor('clockworks/tiktok-scraper').start(input);
    
    // Wait for completion
    let status;
    do {
        await new Promise(r => setTimeout(r, 3000));
        status = await client.run(run.id).get();
    } while (status.status === 'RUNNING' || status.status === 'READY');
    
    console.log('✅ Apify run completed\n');
    
    // Get the data
    const { items } = await client.dataset(status.defaultDatasetId).listItems();
    
    if (items?.[0]) {
        const video = items[0];
        console.log('📊 Available video URL fields:');
        console.log(`   - videoUrl: ${video.videoUrl || 'NOT FOUND'}`);
        console.log(`   - downloadAddr: ${video.downloadAddr || 'NOT FOUND'}`);
        console.log(`   - videoUrlNoWaterMark: ${video.videoUrlNoWaterMark || 'NOT FOUND'}`);
        console.log(`   - mediaUrls: ${video.mediaUrls ? JSON.stringify(video.mediaUrls) : 'NOT FOUND'}`);
        console.log(`   - video.url: ${video.video?.url || 'NOT FOUND'}`);
        console.log(`   - video.downloadAddr: ${video.video?.downloadAddr || 'NOT FOUND'}`);
        console.log(`   - video.playAddr: ${video.video?.playAddr || 'NOT FOUND'}`);
        
        console.log('\n📋 All top-level fields:');
        Object.keys(video).forEach(key => {
            const value = video[key];
            if (key.toLowerCase().includes('url') || key.toLowerCase().includes('video') || key.toLowerCase().includes('download')) {
                console.log(`   - ${key}: ${typeof value === 'object' ? JSON.stringify(value).substring(0, 100) + '...' : value}`);
            }
        });
        
        // Save full response for inspection
        await require('fs').promises.writeFile('apify_video_response.json', JSON.stringify(video, null, 2));
        console.log('\n💾 Full response saved to apify_video_response.json');
    }
}

checkVideoUrlFields().catch(console.error);