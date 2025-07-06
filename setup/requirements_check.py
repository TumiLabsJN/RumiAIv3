#!/usr/bin/env python3
"""
System requirements checker for RumiAI
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class SystemChecker:
    def __init__(self):
        self.results = {}
        
    def check_all(self):
        """Run all system checks"""
        self.check_python_version()
        self.check_nodejs()
        self.check_ffmpeg()
        self.check_disk_space()
        self.check_internet_connection()
        self.check_git()
        self.check_cuda()  # Optional for GPU acceleration
        return self.results
    
    def check_python_version(self):
        """Check Python version >= 3.8"""
        python_version = sys.version_info
        version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        
        if python_version.major >= 3 and python_version.minor >= 8:
            self.results['Python'] = {
                'status': 'success',
                'message': f'Version {version_str} meets requirements (3.8+)'
            }
        else:
            self.results['Python'] = {
                'status': 'error',
                'message': f'Version {version_str} does not meet requirements (3.8+)'
            }
    
    def check_nodejs(self):
        """Check Node.js installation and version"""
        try:
            # Check node
            node_result = subprocess.run(['node', '--version'], 
                                       capture_output=True, text=True)
            if node_result.returncode != 0:
                raise Exception("Node not found")
            
            node_version = node_result.stdout.strip()
            
            # Check npm
            npm_result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, text=True)
            if npm_result.returncode != 0:
                raise Exception("npm not found")
            
            npm_version = npm_result.stdout.strip()
            
            # Extract major version
            major_version = int(node_version.split('.')[0].replace('v', ''))
            if major_version >= 14:
                self.results['Node.js'] = {
                    'status': 'success',
                    'message': f'Node {node_version}, npm {npm_version} found'
                }
            else:
                self.results['Node.js'] = {
                    'status': 'warning',
                    'message': f'Node {node_version} found but v14+ recommended'
                }
                
        except Exception as e:
            self.results['Node.js'] = {
                'status': 'error',
                'message': 'Not installed (required for main service)'
            }
    
    def check_ffmpeg(self):
        """Check FFmpeg installation"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Extract version
                version_line = result.stdout.split('\n')[0]
                self.results['FFmpeg'] = {
                    'status': 'success',
                    'message': f'{version_line.split(" ")[2]} found'
                }
            else:
                raise Exception()
        except:
            self.results['FFmpeg'] = {
                'status': 'warning',
                'message': 'Not installed (required for video processing)'
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            # Get disk usage for home directory
            home_path = Path.home()
            stat = os.statvfs(home_path)
            
            # Calculate free space in GB
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100
            
            if free_gb >= 10:
                self.results['Disk Space'] = {
                    'status': 'success',
                    'message': f'{free_gb:.1f}GB free ({used_percent:.1f}% used)'
                }
            elif free_gb >= 5:
                self.results['Disk Space'] = {
                    'status': 'warning',
                    'message': f'Only {free_gb:.1f}GB free - ML models need ~5GB'
                }
            else:
                self.results['Disk Space'] = {
                    'status': 'error',
                    'message': f'Only {free_gb:.1f}GB free - insufficient for ML models'
                }
        except Exception as e:
            self.results['Disk Space'] = {
                'status': 'warning',
                'message': f'Could not check disk space: {e}'
            }
    
    def check_internet_connection(self):
        """Check internet connectivity"""
        try:
            # Try to reach common DNS servers
            if platform.system() == "Windows":
                result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                                      capture_output=True)
            else:
                result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                      capture_output=True)
            
            if result.returncode == 0:
                self.results['Internet'] = {
                    'status': 'success',
                    'message': 'Connected (required for model downloads)'
                }
            else:
                raise Exception()
        except:
            self.results['Internet'] = {
                'status': 'warning',
                'message': 'No connection detected (required for initial setup)'
            }
    
    def check_git(self):
        """Check Git installation"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.results['Git'] = {
                    'status': 'success',
                    'message': version
                }
            else:
                raise Exception()
        except:
            self.results['Git'] = {
                'status': 'warning',
                'message': 'Not installed (optional but recommended)'
            }
    
    def check_cuda(self):
        """Check CUDA availability for GPU acceleration"""
        try:
            # First check if nvidia-smi exists
            nvidia_result = subprocess.run(['nvidia-smi'], 
                                         capture_output=True, text=True)
            if nvidia_result.returncode == 0:
                # Try to import torch and check CUDA
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_name = torch.cuda.get_device_name(0)
                        self.results['CUDA/GPU'] = {
                            'status': 'success',
                            'message': f'Available - {gpu_name}'
                        }
                    else:
                        self.results['CUDA/GPU'] = {
                            'status': 'warning',
                            'message': 'GPU found but CUDA not available in PyTorch'
                        }
                except ImportError:
                    self.results['CUDA/GPU'] = {
                        'status': 'warning',
                        'message': 'GPU found but PyTorch not installed yet'
                    }
            else:
                raise Exception()
        except:
            self.results['CUDA/GPU'] = {
                'status': 'warning',
                'message': 'Not available (CPU mode will be used)'
            }

def main():
    """Run standalone system check"""
    print("RumiAI System Requirements Check")
    print("=" * 60)
    
    checker = SystemChecker()
    results = checker.check_all()
    
    # Print results
    for component, result in results.items():
        status_symbol = {
            'success': '✅',
            'warning': '⚠️ ',
            'error': '❌'
        }[result['status']]
        
        print(f"{status_symbol} {component}: {result['message']}")
    
    # Summary
    errors = sum(1 for r in results.values() if r['status'] == 'error')
    warnings = sum(1 for r in results.values() if r['status'] == 'warning')
    
    print("\n" + "=" * 60)
    print(f"Summary: {len(results) - errors - warnings} OK, {warnings} warnings, {errors} errors")
    
    if errors > 0:
        print("\n⚠️  Please fix the errors before proceeding with setup.")
        return False
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)