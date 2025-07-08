"""
Temporal Marker Monitoring System
Tracks usage, performance, and quality metrics for temporal markers
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict
import statistics


class TemporalMarkerMonitor:
    """Monitors temporal marker usage and performance"""
    
    def __init__(self, metrics_dir: str = "metrics/temporal_markers"):
        """Initialize monitoring system"""
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session metrics
        self.session_metrics = {
            'start_time': datetime.now().isoformat(),
            'extraction_count': 0,
            'extraction_errors': 0,
            'claude_requests_with_markers': 0,
            'claude_requests_without_markers': 0,
            'total_marker_size_kb': 0,
            'marker_sizes': [],
            'extraction_times': [],
            'api_errors': [],
            'rollout_decisions': defaultdict(int)
        }
        
        # Load historical metrics
        self.historical_metrics = self._load_historical_metrics()
        
    def _load_historical_metrics(self) -> Dict[str, Any]:
        """Load metrics from previous sessions"""
        metrics_file = self.metrics_dir / "historical_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load historical metrics: {e}")
        
        return {
            'total_extractions': 0,
            'total_errors': 0,
            'average_extraction_time': 0,
            'average_marker_size_kb': 0,
            'insights_quality_scores': {},
            'api_error_rate': 0,
            'sessions': []
        }
    
    def record_extraction(self, video_id: str, success: bool, 
                         extraction_time: float, marker_size_kb: Optional[float] = None,
                         error: Optional[str] = None):
        """Record temporal marker extraction event"""
        self.session_metrics['extraction_count'] += 1
        
        if success:
            self.session_metrics['extraction_times'].append(extraction_time)
            if marker_size_kb:
                self.session_metrics['marker_sizes'].append(marker_size_kb)
                self.session_metrics['total_marker_size_kb'] += marker_size_kb
        else:
            self.session_metrics['extraction_errors'] += 1
            
        # Log to file
        event = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video_id,
            'success': success,
            'extraction_time': extraction_time,
            'marker_size_kb': marker_size_kb,
            'error': error
        }
        
        self._log_event('extraction', event)
    
    def record_claude_request(self, video_id: str, prompt_name: str,
                            has_temporal_markers: bool, rollout_decision: str,
                            prompt_size_kb: float, success: bool,
                            error: Optional[str] = None):
        """Record Claude API request with temporal marker status"""
        if has_temporal_markers:
            self.session_metrics['claude_requests_with_markers'] += 1
        else:
            self.session_metrics['claude_requests_without_markers'] += 1
            
        self.session_metrics['rollout_decisions'][rollout_decision] += 1
        
        if not success and error:
            self.session_metrics['api_errors'].append({
                'video_id': video_id,
                'prompt_name': prompt_name,
                'has_markers': has_temporal_markers,
                'error': error
            })
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video_id,
            'prompt_name': prompt_name,
            'has_temporal_markers': has_temporal_markers,
            'rollout_decision': rollout_decision,
            'prompt_size_kb': prompt_size_kb,
            'success': success,
            'error': error
        }
        
        self._log_event('claude_request', event)
    
    def record_insight_quality(self, video_id: str, prompt_name: str,
                             with_markers: bool, quality_score: float,
                             specific_patterns_found: List[str]):
        """Record insight quality metrics for A/B testing"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video_id,
            'prompt_name': prompt_name,
            'with_markers': with_markers,
            'quality_score': quality_score,
            'patterns_found': specific_patterns_found
        }
        
        self._log_event('insight_quality', event)
        
        # Update quality scores
        key = f"{prompt_name}_{'with' if with_markers else 'without'}"
        if key not in self.historical_metrics['insights_quality_scores']:
            self.historical_metrics['insights_quality_scores'][key] = []
        self.historical_metrics['insights_quality_scores'][key].append(quality_score)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current session metrics with calculations"""
        metrics = self.session_metrics.copy()
        
        # Calculate averages
        if metrics['extraction_times']:
            metrics['avg_extraction_time'] = statistics.mean(metrics['extraction_times'])
        else:
            metrics['avg_extraction_time'] = 0
            
        if metrics['marker_sizes']:
            metrics['avg_marker_size_kb'] = statistics.mean(metrics['marker_sizes'])
            metrics['max_marker_size_kb'] = max(metrics['marker_sizes'])
            metrics['min_marker_size_kb'] = min(metrics['marker_sizes'])
        else:
            metrics['avg_marker_size_kb'] = 0
            metrics['max_marker_size_kb'] = 0
            metrics['min_marker_size_kb'] = 0
        
        # Calculate error rates
        total_extractions = metrics['extraction_count']
        if total_extractions > 0:
            metrics['extraction_error_rate'] = metrics['extraction_errors'] / total_extractions
        else:
            metrics['extraction_error_rate'] = 0
            
        total_claude_requests = (metrics['claude_requests_with_markers'] + 
                               metrics['claude_requests_without_markers'])
        if total_claude_requests > 0:
            metrics['api_error_rate'] = len(metrics['api_errors']) / total_claude_requests
            metrics['temporal_marker_adoption'] = (
                metrics['claude_requests_with_markers'] / total_claude_requests
            )
        else:
            metrics['api_error_rate'] = 0
            metrics['temporal_marker_adoption'] = 0
            
        return metrics
    
    def get_quality_comparison(self) -> Dict[str, Any]:
        """Compare insight quality with and without temporal markers"""
        comparison = {}
        
        # Get all keys and extract prompt names
        all_keys = self.historical_metrics['insights_quality_scores'].keys()
        prompt_names = set()
        
        for key in all_keys:
            if key.endswith('_with'):
                prompt_names.add(key[:-5])  # Remove '_with'
            elif key.endswith('_without'):
                prompt_names.add(key[:-8])  # Remove '_without'
        
        for prompt_name in prompt_names:
            with_key = f"{prompt_name}_with"
            without_key = f"{prompt_name}_without"
            
            with_scores = self.historical_metrics['insights_quality_scores'].get(with_key, [])
            without_scores = self.historical_metrics['insights_quality_scores'].get(without_key, [])
            
            if with_scores and without_scores:
                comparison[prompt_name] = {
                    'with_markers': {
                        'avg_score': statistics.mean(with_scores),
                        'sample_size': len(with_scores)
                    },
                    'without_markers': {
                        'avg_score': statistics.mean(without_scores),
                        'sample_size': len(without_scores)
                    },
                    'improvement': (statistics.mean(with_scores) - 
                                  statistics.mean(without_scores))
                }
        
        return comparison
    
    def save_session_metrics(self):
        """Save current session metrics and update historical data"""
        # Get final metrics
        final_metrics = self.get_current_metrics()
        final_metrics['end_time'] = datetime.now().isoformat()
        
        # Update historical metrics
        self.historical_metrics['total_extractions'] += final_metrics['extraction_count']
        self.historical_metrics['total_errors'] += final_metrics['extraction_errors']
        
        # Update rolling averages
        if final_metrics['avg_extraction_time'] > 0:
            prev_avg = self.historical_metrics['average_extraction_time']
            prev_count = len(self.historical_metrics['sessions'])
            new_avg = ((prev_avg * prev_count + final_metrics['avg_extraction_time']) / 
                      (prev_count + 1))
            self.historical_metrics['average_extraction_time'] = new_avg
            
        if final_metrics['avg_marker_size_kb'] > 0:
            prev_avg = self.historical_metrics['average_marker_size_kb']
            prev_count = len(self.historical_metrics['sessions'])
            new_avg = ((prev_avg * prev_count + final_metrics['avg_marker_size_kb']) / 
                      (prev_count + 1))
            self.historical_metrics['average_marker_size_kb'] = new_avg
        
        # Save session
        self.historical_metrics['sessions'].append(final_metrics)
        
        # Save to file
        metrics_file = self.metrics_dir / "historical_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.historical_metrics, f, indent=2)
            
        print(f"Session metrics saved to {metrics_file}")
    
    def generate_report(self) -> str:
        """Generate human-readable metrics report"""
        current = self.get_current_metrics()
        quality = self.get_quality_comparison()
        
        report = []
        report.append("=== TEMPORAL MARKER METRICS REPORT ===")
        report.append(f"Session Start: {self.session_metrics['start_time']}")
        report.append("")
        
        report.append("EXTRACTION METRICS:")
        report.append(f"  Total Extractions: {current['extraction_count']}")
        report.append(f"  Extraction Errors: {current['extraction_errors']} ({current['extraction_error_rate']:.1%})")
        report.append(f"  Avg Extraction Time: {current['avg_extraction_time']:.2f}s")
        report.append(f"  Avg Marker Size: {current['avg_marker_size_kb']:.1f}KB")
        report.append(f"  Size Range: {current['min_marker_size_kb']:.1f}KB - {current['max_marker_size_kb']:.1f}KB")
        report.append("")
        
        report.append("CLAUDE INTEGRATION:")
        report.append(f"  Requests with Markers: {current['claude_requests_with_markers']}")
        report.append(f"  Requests without Markers: {current['claude_requests_without_markers']}")
        report.append(f"  Temporal Marker Adoption: {current['temporal_marker_adoption']:.1%}")
        report.append(f"  API Error Rate: {current['api_error_rate']:.1%}")
        report.append("")
        
        report.append("ROLLOUT DECISIONS:")
        for decision, count in current['rollout_decisions'].items():
            report.append(f"  {decision}: {count}")
        report.append("")
        
        if quality:
            report.append("QUALITY COMPARISON (with vs without markers):")
            for prompt_name, data in quality.items():
                improvement = data['improvement']
                sign = "+" if improvement > 0 else ""
                report.append(f"  {prompt_name}: {sign}{improvement:.2f} improvement")
                report.append(f"    With markers: {data['with_markers']['avg_score']:.2f} (n={data['with_markers']['sample_size']})")
                report.append(f"    Without markers: {data['without_markers']['avg_score']:.2f} (n={data['without_markers']['sample_size']})")
        
        report.append("")
        report.append("HISTORICAL SUMMARY:")
        report.append(f"  Total Sessions: {len(self.historical_metrics['sessions'])}")
        report.append(f"  All-time Extractions: {self.historical_metrics['total_extractions']}")
        report.append(f"  All-time Avg Extraction Time: {self.historical_metrics['average_extraction_time']:.2f}s")
        report.append(f"  All-time Avg Marker Size: {self.historical_metrics['average_marker_size_kb']:.1f}KB")
        
        return "\n".join(report)
    
    def _log_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log event to daily file"""
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.metrics_dir / f"{event_type}_{date_str}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(event_data) + '\n')
    
    def check_rollout_health(self) -> Dict[str, Any]:
        """Check if rollout is healthy and can proceed"""
        current = self.get_current_metrics()
        
        health_checks = {
            'extraction_error_rate_ok': current['extraction_error_rate'] < 0.1,  # <10%
            'api_error_rate_ok': current['api_error_rate'] < 0.05,  # <5%
            'marker_size_ok': current['avg_marker_size_kb'] < 100,  # <100KB avg
            'extraction_time_ok': current['avg_extraction_time'] < 5.0,  # <5s avg
            'sufficient_data': current['extraction_count'] >= 10  # At least 10 samples
        }
        
        health_checks['all_healthy'] = all(health_checks.values())
        
        recommendations = []
        if not health_checks['extraction_error_rate_ok']:
            recommendations.append("High extraction error rate - investigate failures")
        if not health_checks['api_error_rate_ok']:
            recommendations.append("High API error rate - may need to reduce marker size")
        if not health_checks['marker_size_ok']:
            recommendations.append("Large marker sizes - consider enabling compact mode")
        if not health_checks['extraction_time_ok']:
            recommendations.append("Slow extraction times - may impact performance")
        if not health_checks['sufficient_data']:
            recommendations.append("Need more data before making rollout decision")
            
        return {
            'healthy': health_checks['all_healthy'],
            'checks': health_checks,
            'recommendations': recommendations
        }


# Global monitor instance
_monitor_instance = None

def get_monitor() -> TemporalMarkerMonitor:
    """Get or create global monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = TemporalMarkerMonitor()
    return _monitor_instance


# Convenience functions for easy integration
def record_extraction(video_id: str, success: bool, extraction_time: float, 
                     marker_size_kb: Optional[float] = None, error: Optional[str] = None):
    """Record extraction event"""
    monitor = get_monitor()
    monitor.record_extraction(video_id, success, extraction_time, marker_size_kb, error)


def record_claude_request(video_id: str, prompt_name: str, has_temporal_markers: bool,
                         rollout_decision: str, prompt_size_kb: float, success: bool,
                         error: Optional[str] = None):
    """Record Claude request event"""
    monitor = get_monitor()
    monitor.record_claude_request(video_id, prompt_name, has_temporal_markers,
                                rollout_decision, prompt_size_kb, success, error)


def generate_metrics_report() -> str:
    """Generate and return metrics report"""
    monitor = get_monitor()
    return monitor.generate_report()


def check_rollout_health() -> Dict[str, Any]:
    """Check rollout health status"""
    monitor = get_monitor()
    return monitor.check_rollout_health()