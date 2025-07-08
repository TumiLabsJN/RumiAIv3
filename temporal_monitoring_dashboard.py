#!/usr/bin/env python3
"""
Temporal Marker Monitoring Dashboard
Displays metrics and health status for temporal marker rollout
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from python.temporal_monitoring import TemporalMarkerMonitor, get_monitor, check_rollout_health


def display_dashboard():
    """Display monitoring dashboard"""
    monitor = get_monitor()
    
    print("\n" + "="*80)
    print("📊 TEMPORAL MARKER MONITORING DASHBOARD")
    print("="*80)
    
    # Get current metrics
    current = monitor.get_current_metrics()
    
    # Display extraction metrics
    print("\n🔧 EXTRACTION METRICS")
    print("-" * 40)
    print(f"Total Extractions: {current['extraction_count']}")
    print(f"Failed Extractions: {current['extraction_errors']} ({current['extraction_error_rate']:.1%} error rate)")
    print(f"Avg Extraction Time: {current['avg_extraction_time']:.2f}s")
    print(f"Avg Marker Size: {current['avg_marker_size_kb']:.1f}KB")
    print(f"Size Range: {current['min_marker_size_kb']:.1f}KB - {current['max_marker_size_kb']:.1f}KB")
    
    # Display Claude integration metrics
    print("\n🤖 CLAUDE INTEGRATION")
    print("-" * 40)
    total_requests = current['claude_requests_with_markers'] + current['claude_requests_without_markers']
    print(f"Total Claude Requests: {total_requests}")
    print(f"  With Temporal Markers: {current['claude_requests_with_markers']} ({current['temporal_marker_adoption']:.1%})")
    print(f"  Without Temporal Markers: {current['claude_requests_without_markers']}")
    print(f"API Error Rate: {current['api_error_rate']:.1%}")
    
    # Display rollout decisions
    print("\n🎯 ROLLOUT DECISIONS")
    print("-" * 40)
    for decision, count in current['rollout_decisions'].items():
        print(f"  {decision}: {count}")
    
    # Display quality comparison
    quality = monitor.get_quality_comparison()
    if quality:
        print("\n📈 QUALITY COMPARISON (with vs without markers)")
        print("-" * 40)
        for prompt_name, data in quality.items():
            improvement = data['improvement']
            sign = "+" if improvement > 0 else ""
            print(f"\n{prompt_name}:")
            print(f"  Improvement: {sign}{improvement:.2f}")
            print(f"  With markers: {data['with_markers']['avg_score']:.2f} (n={data['with_markers']['sample_size']})")
            print(f"  Without markers: {data['without_markers']['avg_score']:.2f} (n={data['without_markers']['sample_size']})")
    
    # Check rollout health
    print("\n🏥 ROLLOUT HEALTH CHECK")
    print("-" * 40)
    health = check_rollout_health()
    
    if health['healthy']:
        print("✅ All systems healthy - ready for rollout expansion")
    else:
        print("⚠️  Issues detected:")
        for rec in health['recommendations']:
            print(f"   - {rec}")
    
    print("\nHealth Checks:")
    for check, status in health['checks'].items():
        emoji = "✅" if status else "❌"
        print(f"  {emoji} {check.replace('_', ' ').title()}")
    
    # Display recent errors if any
    if current['api_errors']:
        print("\n⚠️  RECENT API ERRORS")
        print("-" * 40)
        for error in current['api_errors'][-5:]:  # Last 5 errors
            print(f"  Video: {error['video_id']}")
            print(f"  Prompt: {error['prompt_name']}")
            print(f"  Has Markers: {error['has_markers']}")
            print(f"  Error: {error['error'][:100]}...")
            print()
    
    # Save session option
    print("\n" + "="*80)
    save = input("💾 Save session metrics? (y/n): ")
    if save.lower() == 'y':
        monitor.save_session_metrics()
        print("✅ Session metrics saved!")


def generate_report():
    """Generate and save a detailed report"""
    monitor = get_monitor()
    report = monitor.generate_report()
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"metrics/temporal_markers/report_{timestamp}.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    print("\n" + "="*80)
    print(report)
    print("="*80)


def simulate_rollout_scenarios():
    """Simulate different rollout percentages to help decision making"""
    monitor = get_monitor()
    current = monitor.get_current_metrics()
    
    print("\n🎲 ROLLOUT SIMULATION")
    print("="*80)
    
    total_videos = 1000  # Simulate for 1000 videos
    
    for percentage in [10, 25, 50, 75, 100]:
        with_markers = int(total_videos * percentage / 100)
        without_markers = total_videos - with_markers
        
        print(f"\n{percentage}% Rollout:")
        print(f"  Videos with markers: {with_markers}")
        print(f"  Videos without markers: {without_markers}")
        
        # Estimate resource usage
        est_extraction_time = with_markers * current['avg_extraction_time']
        est_total_size = with_markers * current['avg_marker_size_kb'] / 1024  # MB
        
        print(f"  Est. extraction time: {est_extraction_time/60:.1f} minutes")
        print(f"  Est. total marker size: {est_total_size:.1f} MB")
        
        # Estimate API impact
        if current['api_error_rate'] > 0:
            est_errors = with_markers * current['api_error_rate']
            print(f"  Est. API errors: {est_errors:.0f}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--report':
            generate_report()
        elif sys.argv[1] == '--simulate':
            simulate_rollout_scenarios()
        else:
            print("Usage: python temporal_monitoring_dashboard.py [--report|--simulate]")
    else:
        display_dashboard()


if __name__ == "__main__":
    main()