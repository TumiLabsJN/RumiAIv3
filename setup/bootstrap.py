#!/usr/bin/env python3
"""
RumiAI Environment Bootstrap Script
Prepares a fresh clone of RumiAI for first-time execution.
"""

import os
import sys
import subprocess
import json
import shutil
import stat
import platform
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ANSI color codes for terminal output
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

class RumiAIBootstrap:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.setup_dir = self.root_dir / "setup"
        self.venv_path = self.root_dir / "venv"
        self.report_path = self.setup_dir / "setup_report.txt"
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def run(self):
        """Main bootstrap orchestration"""
        print_status("RumiAI Environment Setup", "header")
        
        # Phase 1: System checks
        print_status("Phase 1: System Checks", "header")
        self.check_system_requirements()
        
        # Phase 2: Environment setup
        print_status("Phase 2: Environment Setup", "header")
        self.setup_python_environment()
        self.setup_node_environment()
        self.validate_env_file()
        
        # Phase 3: Resource verification
        print_status("Phase 3: Resource Verification", "header")
        self.verify_prompt_templates()
        self.check_model_caches()
        
        # Phase 4: Script permissions
        print_status("Phase 4: Script Permissions", "header")
        self.check_script_permissions()
        
        # Phase 5: Generate report
        print_status("Phase 5: Setup Report", "header")
        self.generate_report()
        
        # Final status
        if self.errors:
            print_status(f"Setup completed with {len(self.errors)} errors", "error")
            return False
        else:
            print_status("Setup completed successfully!", "success")
            return True
    
    def check_system_requirements(self):
        """Check system-level dependencies"""
        print_status("Checking system requirements...")
        
        # Import requirements checker
        try:
            from requirements_check import SystemChecker
            checker = SystemChecker()
            results = checker.check_all()
            
            for check, result in results.items():
                if result['status'] == 'success':
                    print_status(f"{check}: {result['message']}", "success")
                    self.successes.append(f"{check}: {result['message']}")
                elif result['status'] == 'warning':
                    print_status(f"{check}: {result['message']}", "warning")
                    self.warnings.append(f"{check}: {result['message']}")
                else:
                    print_status(f"{check}: {result['message']}", "error")
                    self.errors.append(f"{check}: {result['message']}")
                    
        except ImportError:
            # Fallback if requirements_check.py doesn't exist yet
            self.basic_system_checks()
    
    def basic_system_checks(self):
        """Basic system checks as fallback"""
        # Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print_status(f"Python {python_version.major}.{python_version.minor} found", "success")
            self.successes.append(f"Python version: {python_version.major}.{python_version.minor}")
        else:
            print_status(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}", "error")
            self.errors.append("Python version < 3.8")
        
        # Node.js
        try:
            node_version = subprocess.run(['node', '--version'], 
                                        capture_output=True, text=True)
            if node_version.returncode == 0:
                print_status(f"Node.js {node_version.stdout.strip()} found", "success")
                self.successes.append(f"Node.js: {node_version.stdout.strip()}")
            else:
                raise Exception()
        except:
            print_status("Node.js not found", "error")
            self.errors.append("Node.js not installed")
        
        # FFmpeg
        try:
            ffmpeg_check = subprocess.run(['ffmpeg', '-version'], 
                                        capture_output=True, text=True)
            if ffmpeg_check.returncode == 0:
                print_status("FFmpeg found", "success")
                self.successes.append("FFmpeg installed")
            else:
                raise Exception()
        except:
            print_status("FFmpeg not found (required for video processing)", "warning")
            self.warnings.append("FFmpeg not installed")
    
    def setup_python_environment(self):
        """Setup Python virtual environment and install packages"""
        print_status("Setting up Python environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 12:
            print_status(f"Python {python_version.major}.{python_version.minor} detected", "warning")
            print_status("This project was designed for Python 3.11", "warning")
            self.warnings.append(f"Python {python_version.major}.{python_version.minor} may have compatibility issues")
        
        # Check if venv exists
        if not self.venv_path.exists():
            print_status("Creating virtual environment...")
            
            # Try to find Python 3.11 first
            python_cmd = None
            for cmd in ['python3.11', 'python3', sys.executable]:
                try:
                    result = subprocess.run([cmd, '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        version_output = result.stdout.strip()
                        if 'python3.11' in cmd or '3.11' in version_output:
                            python_cmd = cmd
                            print_status(f"Using {cmd} for virtual environment", "info")
                            break
                        elif python_cmd is None:
                            python_cmd = cmd  # Fallback to any available Python
                except:
                    continue
            
            if python_cmd is None:
                print_status("No suitable Python found", "error")
                self.errors.append("Could not find Python interpreter")
                return
                
            try:
                subprocess.run([python_cmd, '-m', 'venv', str(self.venv_path)], 
                             check=True)
                print_status("Virtual environment created", "success")
                self.successes.append("Python venv created")
            except subprocess.CalledProcessError as e:
                print_status(f"Failed to create venv: {e}", "error")
                self.errors.append("Failed to create Python venv")
                return
        else:
            print_status("Virtual environment already exists", "success")
            self.successes.append("Python venv exists")
        
        # Install requirements
        pip_path = self.venv_path / "bin" / "pip"
        python_exec = self.venv_path / "bin" / "python"
        
        if not pip_path.exists():
            pip_path = self.venv_path / "Scripts" / "pip.exe"  # Windows fallback
            python_exec = self.venv_path / "Scripts" / "python.exe"
        
        # Check Python version in venv and select appropriate requirements
        requirements_path = self.root_dir / "requirements.txt"
        requirements_py312_path = self.root_dir / "requirements_py312.txt"
        
        try:
            # Get venv Python version
            version_result = subprocess.run([str(python_exec), '--version'], 
                                          capture_output=True, text=True)
            if version_result.returncode == 0 and '3.12' in version_result.stdout:
                # Either fix existing or generate new requirements_py312.txt
                if not requirements_py312_path.exists():
                    print_status("Python 3.12 detected, generating compatible requirements", "info")
                    self.generate_python312_requirements()
                else:
                    # Check if requirements_py312.txt needs fixing
                    self.fix_python312_requirements(requirements_py312_path)
                
                if requirements_py312_path.exists():
                    print_status("Using Python 3.12 compatible requirements", "info")
                    requirements_path = requirements_py312_path
                else:
                    print_status("Could not create Python 3.12 requirements", "warning")
                    print_status("Package installation may fail due to version conflicts", "warning")
        except:
            pass
        
        if requirements_path.exists():
            print_status("Installing Python packages (this may take a few minutes)...")
            try:
                # Upgrade pip first
                subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], 
                             check=True, capture_output=True)
                
                # Install requirements
                result = subprocess.run([str(pip_path), 'install', '-r', str(requirements_path)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print_status("Python packages installed successfully", "success")
                    self.successes.append("Python requirements installed")
                else:
                    print_status(f"Package installation failed: {result.stderr}", "error")
                    self.errors.append("Failed to install Python packages")
                    
                # Always try to install CLIP regardless of main package status
                print_status("Installing CLIP from GitHub...")
                clip_result = subprocess.run([str(pip_path), 'install', 
                                            'git+https://github.com/openai/CLIP.git'],
                                           capture_output=True, text=True)
                if clip_result.returncode == 0:
                    print_status("CLIP installed successfully", "success")
                    self.successes.append("CLIP installed from GitHub")
                else:
                    print_status(f"Failed to install CLIP: {clip_result.stderr}", "warning")
                    self.warnings.append("CLIP installation failed - may need manual installation")
            except Exception as e:
                print_status(f"Failed to install packages: {e}", "error")
                self.errors.append(f"Python package installation error: {e}")
        else:
            print_status("requirements.txt not found", "error")
            self.errors.append("requirements.txt missing")
    
    def setup_node_environment(self):
        """Setup Node.js dependencies"""
        print_status("Setting up Node.js environment...")
        
        package_json = self.root_dir / "package.json"
        node_modules = self.root_dir / "node_modules"
        
        if not package_json.exists():
            print_status("package.json not found", "error")
            self.errors.append("package.json missing")
            return
        
        if node_modules.exists():
            print_status("node_modules already exists", "success")
            self.successes.append("Node modules exist")
        else:
            print_status("Installing Node.js packages...")
            try:
                result = subprocess.run(['npm', 'install'], 
                                      cwd=str(self.root_dir),
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print_status("Node.js packages installed successfully", "success")
                    self.successes.append("Node modules installed")
                else:
                    print_status(f"npm install failed: {result.stderr}", "error")
                    self.errors.append("Failed to install Node modules")
            except Exception as e:
                print_status(f"Failed to run npm install: {e}", "error")
                self.errors.append(f"npm install error: {e}")
    
    def validate_env_file(self):
        """Validate .env file and environment variables"""
        print_status("Validating environment variables...")
        
        env_path = self.root_dir / ".env"
        env_example_path = self.root_dir / ".env.example"
        
        # Create .env.example if it doesn't exist
        if not env_example_path.exists():
            example_content = """# RumiAI Environment Variables

# Required API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
APIFY_TOKEN=your-apify-token-here

# Optional Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
PORT=3001
RUMIAI_TEST_MODE=true
YOLO_FRAME_SKIP=2
CLEANUP_VIDEO=false
CLAUDE_API_URL=https://api.anthropic.com/v1/messages
"""
            with open(env_example_path, 'w') as f:
                f.write(example_content)
            print_status("Created .env.example", "success")
        
        if not env_path.exists():
            print_status(".env file not found", "error")
            print_status("Please copy .env.example to .env and add your API keys", "info")
            self.errors.append(".env file missing")
            return
        
        # Load and validate .env
        env_vars = {}
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        # Check required variables
        required_vars = ['ANTHROPIC_API_KEY', 'APIFY_TOKEN']
        for var in required_vars:
            if var not in env_vars:
                print_status(f"{var} not found in .env", "error")
                self.errors.append(f"{var} missing from .env")
            elif env_vars[var] in ['your-anthropic-api-key-here', 'your-apify-token-here', '']:
                print_status(f"{var} has placeholder value", "error")
                self.errors.append(f"{var} has placeholder value")
            else:
                print_status(f"{var} configured", "success")
                self.successes.append(f"{var} configured")
    
    def verify_prompt_templates(self):
        """Verify all required prompt templates exist"""
        print_status("Verifying prompt templates...")
        
        templates_dir = self.root_dir / "prompt_templates"
        required_templates = [
            'creative_density.txt',
            'emotional_journey.txt',
            'metadata_analysis.txt',
            'person_framing.txt',
            'scene_pacing.txt',
            'speech_analysis.txt',
            'visual_overlay_analysis.txt'
        ]
        
        if not templates_dir.exists():
            print_status("prompt_templates directory not found", "error")
            self.errors.append("prompt_templates directory missing")
            return
        
        missing_templates = []
        for template in required_templates:
            template_path = templates_dir / template
            if template_path.exists():
                print_status(f"Found {template}", "success")
            else:
                print_status(f"Missing {template}", "error")
                missing_templates.append(template)
        
        if missing_templates:
            self.errors.append(f"Missing prompt templates: {', '.join(missing_templates)}")
        else:
            self.successes.append("All prompt templates found")
    
    def check_model_caches(self):
        """Check if model cache directories are writable"""
        print_status("Checking model cache directories...")
        
        cache_dirs = [
            (Path.home() / ".cache" / "ultralytics", "YOLOv8"),
            (Path.home() / ".cache" / "clip", "CLIP"),
            (Path.home() / ".cache" / "whisper", "Whisper"),
            (Path.home() / ".EasyOCR", "EasyOCR")
        ]
        
        for cache_dir, model_name in cache_dirs:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                test_file = cache_dir / ".write_test"
                test_file.touch()
                test_file.unlink()
                print_status(f"{model_name} cache directory is writable", "success")
                self.successes.append(f"{model_name} cache writable")
            except Exception as e:
                print_status(f"{model_name} cache not writable: {e}", "warning")
                self.warnings.append(f"{model_name} cache not writable")
    
    def generate_python312_requirements(self):
        """Generate a Python 3.12 compatible requirements file"""
        try:
            # Use the generator script
            generator_path = self.setup_dir / "generate_py312_requirements.py"
            if generator_path.exists():
                result = subprocess.run([sys.executable, str(generator_path)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.successes.append("Generated Python 3.12 requirements")
                    return True
            
            # Fallback: create manually
            requirements_path = self.root_dir / "requirements.txt"
            if not requirements_path.exists():
                return False
                
            with open(requirements_path, 'r') as f:
                content = f.read()
            
            # Apply Python 3.12 compatible versions
            replacements = [
                ('torch==2.1.0', 'torch==2.2.0'),
                ('torchvision==0.16.0', 'torchvision==0.17.0'),
                ('numpy==1.24.3', 'numpy==1.26.4'),
                ('mediapipe==0.10.8', 'mediapipe==0.10.14'),
                ('ultralytics==8.0.200', 'ultralytics==8.3.0'),
            ]
            
            # Add setuptools for Python 3.12 (required by deep-sort-realtime)
            if '# Python 3.12 compatibility' not in content:
                content = "# Python 3.12 compatibility\nsetuptools>=68.0.0\n\n" + content
            
            for old_ver, new_ver in replacements:
                content = content.replace(old_ver, new_ver)
            
            # Write requirements_py312.txt
            output_path = self.root_dir / "requirements_py312.txt"
            with open(output_path, 'w') as f:
                f.write(content)
            
            print_status("Generated requirements_py312.txt", "success")
            self.successes.append("Generated Python 3.12 requirements")
            return True
            
        except Exception as e:
            print_status(f"Could not generate requirements: {e}", "warning")
            self.warnings.append(f"Could not generate Python 3.12 requirements: {e}")
            return False
    
    def fix_python312_requirements(self, requirements_path):
        """Fix incompatible package versions in requirements_py312.txt"""
        try:
            with open(requirements_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Fix known incompatible versions
            replacements = [
                ('torch==2.1.0', 'torch==2.2.0'),
                ('torchvision==0.16.0', 'torchvision==0.17.0'),
                ('numpy==1.24.3', 'numpy==1.26.4'),
                ('mediapipe==0.10.8', 'mediapipe==0.10.14'),
                ('ultralytics==8.0.200', 'ultralytics==8.3.0'),
            ]
            
            for old_ver, new_ver in replacements:
                if old_ver in content:
                    content = content.replace(old_ver, new_ver)
                    print_status(f"Updated {old_ver} to {new_ver}", "info")
            
            # Ensure setuptools is present for Python 3.12
            if 'setuptools' not in content:
                # Add after the core dependencies comment if it exists
                if '# Core dependencies' in content:
                    content = content.replace('# Core dependencies', '# Core dependencies\nsetuptools>=68.0.0  # Required for pkg_resources in Python 3.12')
                else:
                    content = "setuptools>=68.0.0  # Required for pkg_resources in Python 3.12\n\n" + content
                print_status("Added setuptools for Python 3.12 compatibility", "info")
            
            # Only write if changes were made
            if content != original_content:
                with open(requirements_path, 'w') as f:
                    f.write(content)
                print_status("Fixed Python 3.12 compatibility issues in requirements", "success")
                self.successes.append("Fixed Python 3.12 requirements")
        except Exception as e:
            print_status(f"Could not fix requirements: {e}", "warning")
            self.warnings.append(f"Could not auto-fix requirements: {e}")
    
    def check_script_permissions(self):
        """Check and set executable permissions for shell scripts"""
        print_status("🔐 Setting executable permissions...")
        
        # Skip this check on Windows
        if platform.system() == 'Windows':
            print_status("Windows detected - skipping Unix permission check", "info")
            return
        
        script_path = self.root_dir / "copy_clean.sh"
        
        if not script_path.exists():
            print_status("copy_clean.sh not found", "warning")
            self.warnings.append("copy_clean.sh script not found")
            return
        
        try:
            # Get current file stats
            file_stats = os.stat(script_path)
            
            # Check if user has execute permission
            has_user_exec = bool(file_stats.st_mode & stat.S_IXUSR)
            
            if has_user_exec:
                print_status("copy_clean.sh is already executable", "success")
                self.successes.append("copy_clean.sh has executable permission")
            else:
                # Add execute permission for user
                new_mode = file_stats.st_mode | stat.S_IXUSR
                os.chmod(script_path, new_mode)
                print_status("copy_clean.sh made executable", "success")
                self.successes.append("copy_clean.sh executable permission set")
                
        except Exception as e:
            print_status(f"Failed to check/set permissions: {e}", "warning")
            self.warnings.append(f"Could not set permissions on copy_clean.sh: {e}")
    
    def generate_report(self):
        """Generate setup report"""
        print_status("Generating setup report...")
        
        report_content = f"""RumiAI Setup Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

SUMMARY
-------
✅ Successes: {len(self.successes)}
⚠️  Warnings: {len(self.warnings)}
❌ Errors: {len(self.errors)}

SUCCESSES
---------
"""
        for success in self.successes:
            report_content += f"✅ {success}\n"
        
        if self.warnings:
            report_content += "\nWARNINGS\n--------\n"
            for warning in self.warnings:
                report_content += f"⚠️  {warning}\n"
        
        if self.errors:
            report_content += "\nERRORS\n------\n"
            for error in self.errors:
                report_content += f"❌ {error}\n"
        
        report_content += f"\n{'='*60}\n"
        
        if self.errors:
            report_content += """
NEXT STEPS
----------
1. Fix the errors listed above
2. Run this script again to verify fixes
3. Once all errors are resolved, run: python setup/verify_setup.py
"""
        else:
            report_content += """
NEXT STEPS
----------
1. Run verification: python setup/verify_setup.py
2. Start the service: node test_rumiai_complete_flow.js
"""
        
        with open(self.report_path, 'w') as f:
            f.write(report_content)
        
        print_status(f"Setup report saved to: {self.report_path}", "info")
        print("\n" + report_content)

if __name__ == "__main__":
    bootstrap = RumiAIBootstrap()
    success = bootstrap.run()
    sys.exit(0 if success else 1)