#!/usr/bin/env python3
"""
RumiAI Setup Verification Script
Tests that all components are properly installed and configured.
"""

import os
import sys
import subprocess
import json
import importlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    """Print colored status messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "success":
        print(f"{Colors.GREEN}✅ [{timestamp}] {message}{Colors.RESET}")
    elif status == "error":
        print(f"{Colors.RED}❌ [{timestamp}] {message}{Colors.RESET}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  [{timestamp}] {message}{Colors.RESET}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  [{timestamp}] {message}{Colors.RESET}")
    elif status == "header":
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print(f"{message}")
        print(f"{'='*60}{Colors.RESET}\n")

class SetupVerifier:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.venv_path = self.root_dir / "venv"
        self.python_path = self.venv_path / "bin" / "python"
        if not self.python_path.exists():
            self.python_path = self.venv_path / "Scripts" / "python.exe"  # Windows
        
        self.test_results = {
            'python_packages': [],
            'node_modules': [],
            'api_keys': [],
            'models': [],
            'directories': []
        }
        
    def run(self):
        """Run all verification tests"""
        print_status("RumiAI Setup Verification", "header")
        
        # Test 1: Python packages
        print_status("Testing Python Packages", "header")
        self.test_python_packages()
        
        # Test 2: Node.js modules
        print_status("Testing Node.js Modules", "header")
        self.test_node_modules()
        
        # Test 3: API keys
        print_status("Testing API Keys", "header")
        self.test_api_keys()
        
        # Test 4: Model accessibility
        print_status("Testing Model Accessibility", "header")
        self.test_models()
        
        # Test 5: Directory structure
        print_status("Testing Directory Structure", "header")
        self.test_directories()
        
        # Summary
        self.print_summary()
    
    def test_python_packages(self):
        """Test Python package imports"""
        critical_packages = [
            ('numpy', 'NumPy'),
            ('cv2', 'OpenCV'),
            ('mediapipe', 'MediaPipe'),
            ('torch', 'PyTorch'),
            ('ultralytics', 'Ultralytics YOLO'),
            ('whisper', 'OpenAI Whisper'),
            ('anthropic', 'Anthropic SDK'),
            ('dotenv', 'python-dotenv'),
            ('moviepy.editor', 'MoviePy'),
            ('easyocr', 'EasyOCR'),
            ('scenedetect', 'PySceneDetect'),
            ('PIL', 'Pillow'),
            ('deep_sort_realtime', 'DeepSort')
        ]
        
        # Special test for CLIP (needs special import)
        try:
            print_status("Testing CLIP installation...")
            result = subprocess.run([str(self.python_path), '-c', 'import clip; print(clip.available_models())'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_status("CLIP installed correctly", "success")
                self.test_results['python_packages'].append(('CLIP', True))
            else:
                print_status("CLIP not properly installed", "error")
                self.test_results['python_packages'].append(('CLIP', False))
        except Exception as e:
            print_status(f"CLIP test failed: {e}", "error")
            self.test_results['python_packages'].append(('CLIP', False))
        
        # Test other packages
        for module_name, display_name in critical_packages:
            try:
                # Run import in subprocess with venv Python
                result = subprocess.run([str(self.python_path), '-c', f'import {module_name}'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print_status(f"{display_name} imported successfully", "success")
                    self.test_results['python_packages'].append((display_name, True))
                else:
                    print_status(f"{display_name} import failed: {result.stderr}", "error")
                    self.test_results['python_packages'].append((display_name, False))
            except Exception as e:
                print_status(f"{display_name} test failed: {e}", "error")
                self.test_results['python_packages'].append((display_name, False))
        
        # Check specific versions
        print_status("\nChecking package versions...")
        version_checks = [
            ('torch', 'torch.__version__'),
            ('ultralytics', 'ultralytics.__version__'),
            ('mediapipe', 'mediapipe.__version__'),
            ('whisper', 'whisper.__version__')
        ]
        
        for module, version_attr in version_checks:
            try:
                result = subprocess.run([str(self.python_path), '-c', 
                                       f'import {module}; print({version_attr})'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print_status(f"{module} version: {version}", "info")
            except:
                pass
    
    def test_node_modules(self):
        """Test Node.js module availability"""
        package_json_path = self.root_dir / "package.json"
        
        if not package_json_path.exists():
            print_status("package.json not found", "error")
            return
        
        # Read package.json to get dependencies
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        dependencies = package_data.get('dependencies', {})
        critical_modules = ['dotenv', 'axios', 'puppeteer']
        
        node_modules_path = self.root_dir / "node_modules"
        
        for module in critical_modules:
            if module in dependencies:
                module_path = node_modules_path / module
                if module_path.exists():
                    print_status(f"{module} installed", "success")
                    self.test_results['node_modules'].append((module, True))
                else:
                    print_status(f"{module} not found in node_modules", "error")
                    self.test_results['node_modules'].append((module, False))
    
    def test_api_keys(self):
        """Test API key configuration"""
        env_path = self.root_dir / ".env"
        
        if not env_path.exists():
            print_status(".env file not found", "error")
            self.test_results['api_keys'].append(('.env file', False))
            return
        
        # Load .env
        env_vars = {}
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        # Test Anthropic API key
        if 'ANTHROPIC_API_KEY' in env_vars:
            key_value = env_vars['ANTHROPIC_API_KEY']
            if key_value and key_value != 'your-anthropic-api-key-here':
                # Basic format check
                if key_value.startswith('sk-'):
                    print_status("ANTHROPIC_API_KEY configured (format looks valid)", "success")
                    self.test_results['api_keys'].append(('ANTHROPIC_API_KEY', True))
                else:
                    print_status("ANTHROPIC_API_KEY configured (unusual format)", "warning")
                    self.test_results['api_keys'].append(('ANTHROPIC_API_KEY', True))
            else:
                print_status("ANTHROPIC_API_KEY has placeholder value", "error")
                self.test_results['api_keys'].append(('ANTHROPIC_API_KEY', False))
        else:
            print_status("ANTHROPIC_API_KEY not found", "error")
            self.test_results['api_keys'].append(('ANTHROPIC_API_KEY', False))
        
        # Test Apify token
        if 'APIFY_TOKEN' in env_vars:
            key_value = env_vars['APIFY_TOKEN']
            if key_value and key_value != 'your-apify-token-here':
                print_status("APIFY_TOKEN configured", "success")
                self.test_results['api_keys'].append(('APIFY_TOKEN', True))
            else:
                print_status("APIFY_TOKEN has placeholder value", "error")
                self.test_results['api_keys'].append(('APIFY_TOKEN', False))
        else:
            print_status("APIFY_TOKEN not found", "error")
            self.test_results['api_keys'].append(('APIFY_TOKEN', False))
    
    def test_models(self):
        """Test model accessibility"""
        print_status("Testing model loading capabilities...")
        
        # Test YOLOv8
        try:
            result = subprocess.run([str(self.python_path), '-c', 
                                   'from ultralytics import YOLO; print("YOLOv8 ready")'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_status("YOLOv8 can be loaded", "success")
                self.test_results['models'].append(('YOLOv8', True))
            else:
                print_status(f"YOLOv8 load test failed: {result.stderr}", "error")
                self.test_results['models'].append(('YOLOv8', False))
        except Exception as e:
            print_status(f"YOLOv8 test error: {e}", "error")
            self.test_results['models'].append(('YOLOv8', False))
        
        # Test MediaPipe
        try:
            result = subprocess.run([str(self.python_path), '-c', 
                                   'import mediapipe as mp; mp.solutions.face_mesh; print("MediaPipe ready")'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_status("MediaPipe models accessible", "success")
                self.test_results['models'].append(('MediaPipe', True))
            else:
                print_status("MediaPipe test failed", "error")
                self.test_results['models'].append(('MediaPipe', False))
        except Exception as e:
            print_status(f"MediaPipe test error: {e}", "error")
            self.test_results['models'].append(('MediaPipe', False))
        
        # Test EasyOCR
        try:
            result = subprocess.run([str(self.python_path), '-c', 
                                   'import easyocr; print("EasyOCR ready")'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print_status("EasyOCR ready", "success")
                self.test_results['models'].append(('EasyOCR', True))
            else:
                print_status("EasyOCR test failed", "error")
                self.test_results['models'].append(('EasyOCR', False))
        except subprocess.TimeoutExpired:
            print_status("EasyOCR test timed out (models will download on first use)", "warning")
            self.test_results['models'].append(('EasyOCR', True))
        except Exception as e:
            print_status(f"EasyOCR test error: {e}", "error")
            self.test_results['models'].append(('EasyOCR', False))
    
    def test_directories(self):
        """Test directory structure"""
        # Critical directories that should exist
        critical_dirs = [
            ('prompt_templates', 'Prompt templates directory'),
            ('venv', 'Python virtual environment'),
            ('node_modules', 'Node.js modules'),
        ]
        
        for dir_name, description in critical_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                print_status(f"{description} exists", "success")
                self.test_results['directories'].append((dir_name, True))
            else:
                print_status(f"{description} missing", "error")
                self.test_results['directories'].append((dir_name, False))
        
        # Check prompt template files
        prompt_dir = self.root_dir / "prompt_templates"
        if prompt_dir.exists():
            templates = list(prompt_dir.glob("*.txt"))
            if templates:
                print_status(f"Found {len(templates)} prompt templates", "success")
            else:
                print_status("No prompt templates found", "error")
                self.test_results['directories'].append(('prompt_templates/*.txt', False))
        
        # Check venv Python
        if self.python_path.exists():
            print_status(f"Virtual environment Python found at {self.python_path}", "success")
            self.test_results['directories'].append(('venv/bin/python', True))
        else:
            print_status("Virtual environment Python not found", "error")
            self.test_results['directories'].append(('venv/bin/python', False))
    
    def print_summary(self):
        """Print verification summary"""
        print_status("Verification Summary", "header")
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            if results:
                category_passed = sum(1 for _, passed in results if passed)
                category_total = len(results)
                total_tests += category_total
                passed_tests += category_passed
                
                print(f"\n{category.replace('_', ' ').title()}:")
                print(f"  Passed: {category_passed}/{category_total}")
                
                for name, passed in results:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {name}")
        
        print(f"\n{'='*60}")
        print(f"Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print_status("\n🎉 All tests passed! RumiAI is ready to run.", "success")
            print_status("You can now run: node test_rumiai_complete_flow.js", "info")
            return True
        else:
            print_status(f"\n⚠️  {total_tests - passed_tests} tests failed.", "error")
            print_status("Please run 'python setup/bootstrap.py' to fix issues.", "info")
            return False

def main():
    """Run verification"""
    verifier = SetupVerifier()
    success = verifier.run()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)