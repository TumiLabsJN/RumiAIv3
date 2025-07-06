#!/usr/bin/env python3
"""
Run Claude prompts with ML data validation - Version 2
Integrated into the complete flow for any TikTok URL
"""

import os
import sys
import json
import time
import statistics
from datetime import datetime
from run_claude_insight import ClaudeInsightRunner

# Initialize the runner
runner = ClaudeInsightRunner()


def parse_timestamp_to_seconds(timestamp):
    """Convert timestamp like '0-1s' to start second"""
    try:
        return int(timestamp.split('-')[0])
    except:
        return None


def is_timestamp_in_second(timestamp, second):
    """Check if a timestamp range overlaps with a given second"""
    try:
        parts = timestamp.split('-')
        if len(parts) == 2:
            start = float(parts[0])
            end = float(parts[1].replace('s', ''))
            return start <= second < end
        return False
    except:
        return False


def mean(values):
    """Calculate mean of a list"""
    return sum(values) / len(values) if values else 0


def stdev(values):
    """Calculate standard deviation of a list"""
    if len(values) < 2:
        return 0
    return statistics.stdev(values)


def variance(values):
    """Calculate variance of a list"""
    if len(values) < 2:
        return 0
    return statistics.variance(values)