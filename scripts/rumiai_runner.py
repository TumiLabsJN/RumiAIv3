#!/usr/bin/env python3
"""
Main entry point for RumiAI v2.

CRITICAL: Must maintain backward compatibility with existing Node.js calls.
Supports both old and new calling conventions.
"""
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import json
import os
import time

# Load .env file if it exists
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rumiai_v2.api import ClaudeClient, ApifyClient, MLServices
from rumiai_v2.processors import (
    VideoAnalyzer, TimelineBuilder, TemporalMarkerProcessor,
    MLDataExtractor, PromptBuilder
)
from rumiai_v2.core.models import PromptType, PromptBatch, VideoMetadata
from rumiai_v2.config import Settings
from rumiai_v2.utils import FileHandler, Logger, Metrics, VideoProcessingMetrics

# Configure logging
logger = Logger.setup('rumiai_v2', level=os.getenv('LOG_LEVEL', 'INFO'))


class RumiAIRunner:
    """
    Main orchestrator for RumiAI v2.
    
    CRITICAL: Maintains backward compatibility with old system.
    """
    
    def __init__(self, legacy_mode: bool = False):
        """
        Initialize runner.
        
        Args:
            legacy_mode: If True, operate in backward compatibility mode
        """
        self.legacy_mode = legacy_mode
        self.settings = Settings()
        self.metrics = Metrics()
        self.video_metrics = VideoProcessingMetrics()
        
        # Initialize file handlers
        self.file_handler = FileHandler(self.settings.output_dir)
        self.unified_handler = FileHandler(self.settings.unified_dir)
        self.insights_handler = FileHandler(self.settings.insights_dir)
        self.temporal_handler = FileHandler(self.settings.temporal_dir)
        
        # Initialize clients
        self.apify = ApifyClient(self.settings.apify_token)
        self.claude = ClaudeClient(self.settings.claude_api_key, self.settings.claude_model)
        self.ml_services = MLServices()
        
        # Initialize processors
        self.video_analyzer = VideoAnalyzer(self.ml_services)
        self.timeline_builder = TimelineBuilder()
        self.temporal_processor = TemporalMarkerProcessor()
        self.ml_extractor = MLDataExtractor()
        self.prompt_builder = PromptBuilder(self.settings._prompt_templates)
    
    async def process_video_url(self, video_url: str) -> Dict[str, Any]:
        """
        Process a video from URL (new mode).
        
        This is the main entry point for new system.
        """
        logger.info(f"🚀 Starting processing for: {video_url}")
        self.metrics.start_timer('total_processing')
        
        try:
            # Step 1: Scrape video metadata
            print("📊 scraping_metadata... (0%)")
            video_metadata = await self._scrape_video(video_url)
            video_id = video_metadata.video_id
            print(f"✅ Video ID: {video_id}")
            
            # Step 2: Download video
            print("📊 downloading_video... (10%)")
            video_path = await self._download_video(video_metadata)
            print(f"✅ Downloaded to: {video_path}")
            
            # Step 3: Run ML analysis
            print("📊 running_ml_analysis... (20%)")
            ml_results = await self._run_ml_analysis(video_id, video_path)
            
            # Step 4: Build unified timeline
            print("📊 building_timeline... (50%)")
            unified_analysis = self.timeline_builder.build_timeline(
                video_id, 
                video_metadata.to_dict(), 
                ml_results
            )
            
            # Step 5: Generate temporal markers
            print("📊 generating_temporal_markers... (60%)")
            temporal_markers = self.temporal_processor.generate_markers(unified_analysis)
            unified_analysis.temporal_markers = temporal_markers
            
            # Save temporal markers separately for compatibility
            temporal_path = self.temporal_handler.get_path(
                f"{video_id}_{int(time.time())}.json"
            )
            self.temporal_handler.save_json(temporal_path, temporal_markers)
            
            # Step 6: Save unified analysis
            print("📊 saving_analysis... (65%)")
            unified_path = self.unified_handler.get_path(f"{video_id}.json")
            unified_analysis.save_to_file(str(unified_path))
            
            # Step 7: Run Claude prompts
            print("📊 running_claude_prompts... (70%)")
            prompt_results = await self._run_claude_prompts(unified_analysis)
            
            # Step 8: Generate final report
            print("📊 generating_report... (95%)")
            report = self._generate_report(unified_analysis, prompt_results)
            
            self.metrics.stop_timer('total_processing')
            self.video_metrics.record_video(success=True)
            
            print("📊 completed... (100%)")
            logger.info(f"✅ Processing complete! Total time: {self.metrics.get_time('total_processing'):.1f}s")
            
            # Return result in format expected by Node.js
            return {
                'success': True,
                'video_id': video_id,
                'outputs': {
                    'video': str(video_path),
                    'unified': str(unified_path),
                    'temporal': str(temporal_path),
                    'insights': str(self.insights_handler.base_dir / video_id)
                },
                'report': report,
                'metrics': self.metrics.get_all()
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            self.video_metrics.record_video(success=False)
            
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'metrics': self.metrics.get_all()
            }
    
    async def process_video_id(self, video_id: str) -> Dict[str, Any]:
        """
        Process a video by ID (legacy mode).
        
        This maintains compatibility with old Python script calls.
        """
        logger.info(f"🔄 Processing video ID in legacy mode: {video_id}")
        
        try:
            # Load existing analysis data
            unified_path = self.unified_handler.get_path(f"{video_id}.json")
            if not unified_path.exists():
                # Try old path structure
                old_path = Path(f"unified_analysis/{video_id}.json")
                if old_path.exists():
                    unified_path = old_path
                else:
                    raise FileNotFoundError(f"No unified analysis found for {video_id}")
            
            # Load unified analysis
            from ..core.models import UnifiedAnalysis
            unified_analysis = UnifiedAnalysis.load_from_file(str(unified_path))
            
            # Generate temporal markers if missing
            if not unified_analysis.temporal_markers:
                print("🔄 Generating temporal markers...")
                temporal_markers = self.temporal_processor.generate_markers(unified_analysis)
                unified_analysis.temporal_markers = temporal_markers
                
                # Save temporal markers
                temporal_path = self.temporal_handler.get_path(
                    f"{video_id}_{int(time.time())}.json"
                )
                self.temporal_handler.save_json(temporal_path, temporal_markers)
            
            # Run Claude prompts
            print("🧠 Running Claude prompts...")
            prompt_results = await self._run_claude_prompts(unified_analysis)
            
            # Generate report
            report = self._generate_report(unified_analysis, prompt_results)
            
            return {
                'success': True,
                'video_id': video_id,
                'prompts_completed': len([r for r in prompt_results.values() if r.success]),
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Legacy processing failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _scrape_video(self, video_url: str) -> VideoMetadata:
        """Scrape video metadata from TikTok."""
        self.metrics.start_timer('scraping')
        try:
            metadata = await self.apify.scrape_video(video_url)
            self.metrics.stop_timer('scraping')
            return metadata
        except Exception as e:
            self.metrics.stop_timer('scraping')
            raise
    
    async def _download_video(self, video_metadata: VideoMetadata) -> Path:
        """Download video file."""
        self.metrics.start_timer('download')
        try:
            video_path = await self.apify.download_video(
                video_metadata.download_url,
                video_metadata.video_id,
                self.settings.temp_dir
            )
            self.metrics.stop_timer('download')
            return video_path
        except Exception as e:
            self.metrics.stop_timer('download')
            raise
    
    async def _run_ml_analysis(self, video_id: str, video_path: Path) -> Dict[str, Any]:
        """Run all ML analyses on video."""
        self.metrics.start_timer('ml_analysis')
        try:
            results = await self.video_analyzer.analyze_video(video_id, video_path)
            
            # Log ML timing
            for model_name, result in results.items():
                if result.processing_time > 0:
                    self.video_metrics.record_ml_time(model_name, result.processing_time)
            
            self.metrics.stop_timer('ml_analysis')
            return results
        except Exception as e:
            self.metrics.stop_timer('ml_analysis')
            raise
    
    async def _run_claude_prompts(self, analysis) -> Dict[str, Any]:
        """Run all Claude prompts."""
        self.metrics.start_timer('claude_prompts')
        
        # Define prompts to run
        prompt_types = [
            PromptType.CREATIVE_DENSITY,
            PromptType.EMOTIONAL_JOURNEY,
            PromptType.SPEECH_ANALYSIS,
            PromptType.VISUAL_OVERLAY,
            PromptType.METADATA_ANALYSIS,
            PromptType.PERSON_FRAMING,
            PromptType.SCENE_PACING
        ]
        
        # Create prompt batch
        batch = PromptBatch(
            video_id=analysis.video_id,
            prompts=prompt_types
        )
        
        # Process each prompt
        for i, prompt_type in enumerate(prompt_types):
            # Progress output for Node.js
            progress = int((i / len(prompt_types)) * 100)
            print(f"\n[{'█' * (i+1)}{'░' * (len(prompt_types)-i-1)}] {i+1}/{len(prompt_types)} ({progress}%)")
            print(f"🎬 Running {prompt_type.value} for video {analysis.video_id}")
            
            try:
                # Extract relevant data
                context = self.ml_extractor.extract_for_prompt(analysis, prompt_type)
                
                # Build prompt
                prompt_text = self.prompt_builder.build_prompt(context)
                
                # Log prompt info
                print(f"📏 Payload size: {context.get_size_bytes() / 1024:.1f}KB")
                
                # Send to Claude
                self.metrics.start_timer(f'prompt_{prompt_type.value}')
                result = self.claude.send_prompt(
                    prompt_text,
                    {
                        'video_id': analysis.video_id,
                        'prompt_type': prompt_type.value
                    },
                    timeout=self.settings.prompt_timeouts.get(prompt_type.value, 60)
                )
                prompt_time = self.metrics.stop_timer(f'prompt_{prompt_type.value}')
                
                # Record metrics
                self.video_metrics.record_prompt_time(prompt_type.value, prompt_time)
                if result.success:
                    self.video_metrics.record_prompt_cost(prompt_type.value, result.estimated_cost)
                
                # Save result
                self._save_prompt_result(analysis.video_id, prompt_type.value, result)
                
                # Add to batch
                batch.add_result(result)
                
                if result.success:
                    print(f"✅ {prompt_type.value} completed successfully!")
                    print(f"⏱️  {prompt_type.value} completed in {prompt_time:.1f}s")
                else:
                    print(f"❌ {prompt_type.value} failed: {result.error}")
                
                # Delay between prompts
                if i < len(prompt_types) - 1 and self.settings.prompt_delay > 0:
                    print(f"⏳ Waiting {self.settings.prompt_delay}s before next prompt...")
                    await asyncio.sleep(self.settings.prompt_delay)
                    
            except Exception as e:
                logger.error(f"Prompt {prompt_type.value} failed with exception: {str(e)}")
                print(f"❌ {prompt_type.value} crashed: {str(e)}")
                
                # Create failed result
                from rumiai_v2.core.models import PromptResult
                result = PromptResult(
                    prompt_type=prompt_type,
                    success=False,
                    error=str(e)
                )
                batch.add_result(result)
        
        self.metrics.stop_timer('claude_prompts')
        
        # Summary
        print(f"\n📊 Prompt Summary: {batch.get_success_rate()*100:.0f}% success rate")
        print(f"💰 Total cost: ${batch.get_total_cost():.4f}")
        
        return batch.results
    
    def _save_prompt_result(self, video_id: str, prompt_name: str, result) -> None:
        """Save individual prompt result."""
        # Create directory structure
        prompt_dir = self.insights_handler.get_path(video_id, prompt_name)
        prompt_dir.mkdir(parents=True, exist_ok=True)
        
        # Save result
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        result_path = prompt_dir / f"{prompt_name}_result_{timestamp}.txt"
        complete_path = prompt_dir / f"{prompt_name}_complete_{timestamp}.json"
        
        if result.success:
            # Save response text
            with open(result_path, 'w') as f:
                f.write(result.response)
        
        # Save complete data
        self.insights_handler.save_json(complete_path, result.to_dict())
    
    def _generate_report(self, analysis, prompt_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final analysis report."""
        successful_prompts = sum(1 for r in prompt_results.values() if r.success)
        
        return {
            'video_id': analysis.video_id,
            'duration': analysis.timeline.duration,
            'ml_analyses_complete': analysis.is_complete(),
            'ml_completion_details': analysis.get_completion_status(),
            'temporal_markers_generated': analysis.temporal_markers is not None,
            'prompts_successful': successful_prompts,
            'prompts_total': len(prompt_results),
            'prompt_details': {
                name: {
                    'success': result.success,
                    'tokens': result.tokens_used,
                    'cost': result.estimated_cost,
                    'time': result.processing_time
                }
                for name, result in prompt_results.items()
            },
            'processing_metrics': self.metrics.get_all(),
            'video_metrics': self.video_metrics.get_summary()
        }


def main():
    """
    Main entry point.
    
    CRITICAL: Exit codes must match Node.js expectations:
    - 0: Success
    - 1: General failure  
    - 2: Invalid arguments
    - 3: API failure
    - 4: ML processing failure
    """
    parser = argparse.ArgumentParser(description='RumiAI v2 Video Processor')
    
    # Support multiple calling conventions
    parser.add_argument('video_input', nargs='?', help='Video URL or ID')
    parser.add_argument('--video-url', help='Video URL to process')
    parser.add_argument('--video-id', help='Video ID to process (legacy mode)')
    parser.add_argument('--config-dir', help='Configuration directory')
    parser.add_argument('--output-format', choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    # Determine mode and input
    video_url = None
    video_id = None
    legacy_mode = False
    
    if args.video_url:
        video_url = args.video_url
    elif args.video_id:
        video_id = args.video_id
        legacy_mode = True
    elif args.video_input:
        # Auto-detect URL vs ID
        if args.video_input.startswith('http'):
            video_url = args.video_input
        else:
            video_id = args.video_input
            legacy_mode = True
    else:
        print("Usage: rumiai_runner.py <video_url_or_id>", file=sys.stderr)
        sys.exit(2)
    
    try:
        # Create runner
        runner = RumiAIRunner(legacy_mode=legacy_mode)
        
        # Run processing
        if legacy_mode:
            logger.info(f"Running in legacy mode for video ID: {video_id}")
            result = asyncio.run(runner.process_video_id(video_id))
        else:
            logger.info(f"Running in new mode for video URL: {video_url}")
            result = asyncio.run(runner.process_video_url(video_url))
        
        # Output result
        if args.output_format == 'json':
            print(json.dumps(result, indent=2))
        else:
            if result['success']:
                print(f"✅ Success! Video {result.get('video_id', 'unknown')} processed.")
                if 'report' in result:
                    print(f"Report: {json.dumps(result['report'], indent=2)}")
            else:
                print(f"❌ Failed! Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        
        # Exit with appropriate code
        if result['success']:
            sys.exit(0)
        else:
            error_type = result.get('error_type', '')
            if 'API' in error_type:
                sys.exit(3)
            elif 'ML' in error_type:
                sys.exit(4)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"🔴 FATAL ERROR: {type(e).__name__}: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()