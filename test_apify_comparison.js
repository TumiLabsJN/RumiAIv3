#!/usr/bin/env node

require('dotenv').config();
const { ApifyClient } = require('apify-client');

const TEST_VIDEO_URL = 'https://www.tiktok.com/@aliasherbals/video/7522345762324237623';

async function compareApifyConfigs() {
    console.log('🔬 Comparing Apify Configurations\n');
    
    const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
    
    // Configuration 1: With all downloads (what TikTokSingleVideoScraper uses)
    console.log('📊 Config 1: Full downloads (current implementation)');
    console.log('---------------------------------------------------');
    
    const input1 = {
        postURLs: [TEST_VIDEO_URL],
        resultsPerPage: 1,
        shouldDownloadVideos: true,
        shouldDownloadCovers: true,
        shouldDownloadSubtitles: true,
        proxyConfiguration: { useApifyProxy: true }
    };
    
    const start1 = Date.now();
    const run1 = await client.actor('clockworks/tiktok-scraper').start(input1);
    
    // Poll for completion
    let status1;
    do {
        await new Promise(r => setTimeout(r, 3000));
        status1 = await client.run(run1.id).get();
        const elapsed = Math.round((Date.now() - start1) / 1000);
        console.log(`   ${elapsed}s: ${status1.status}`);
    } while (status1.status === 'RUNNING' || status1.status === 'READY');
    
    const time1 = Math.round((Date.now() - start1) / 1000);
    console.log(`✅ Completed in ${time1} seconds\n`);
    
    // Get the data to check what was downloaded
    const { items: items1 } = await client.dataset(status1.defaultDatasetId).listItems();
    if (items1?.[0]) {
        console.log('📥 Downloaded content:');
        console.log(`   - Video URL: ${items1[0].videoUrl ? 'Yes' : 'No'}`);
        console.log(`   - Media URLs: ${items1[0].mediaUrls?.length || 0} URLs`);
        console.log(`   - Download Address: ${items1[0].downloadAddr ? 'Yes' : 'No'}`);
        console.log(`   - Cover URL: ${items1[0].videoMeta?.coverUrl ? 'Yes' : 'No'}`);
    }
    
    // Configuration 2: Metadata only
    console.log('\n📊 Config 2: Metadata only (optimized)');
    console.log('--------------------------------------');
    
    const input2 = {
        postURLs: [TEST_VIDEO_URL],
        resultsPerPage: 1,
        shouldDownloadVideos: false,
        shouldDownloadCovers: false,
        shouldDownloadSubtitles: false,
        proxyConfiguration: { useApifyProxy: true }
    };
    
    const start2 = Date.now();
    const run2 = await client.actor('clockworks/tiktok-scraper').start(input2);
    
    // Poll for completion
    let status2;
    do {
        await new Promise(r => setTimeout(r, 3000));
        status2 = await client.run(run2.id).get();
        const elapsed = Math.round((Date.now() - start2) / 1000);
        console.log(`   ${elapsed}s: ${status2.status}`);
    } while (status2.status === 'RUNNING' || status2.status === 'READY');
    
    const time2 = Math.round((Date.now() - start2) / 1000);
    console.log(`✅ Completed in ${time2} seconds\n`);
    
    // Summary
    console.log('📊 Performance Comparison');
    console.log('========================');
    console.log(`Full downloads: ${time1} seconds`);
    console.log(`Metadata only:  ${time2} seconds`);
    console.log(`Difference:     ${time1 - time2} seconds (${Math.round((time1 - time2) / time1 * 100)}% slower)\n`);
    
    console.log('💡 Recommendation:');
    console.log('The significant delay is caused by Apify downloading the full video file.');
    console.log('Consider fetching metadata first, then downloading video separately if needed.');
}

compareApifyConfigs().catch(console.error);