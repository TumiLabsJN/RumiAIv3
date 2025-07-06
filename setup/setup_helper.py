#!/usr/bin/env python3
"""
RumiAI Setup Helper
Provides guidance for setting up RumiAI with the correct Python version.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_versions():
    """Check available Python versions on the system"""
    print("🔍 Checking available Python versions...\n")
    
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Current Python: {current_version}")
    
    # Check for other Python versions
    versions_found = {}
    for version in ['3.11', '3.10', '3.9', '3.12']:
        for cmd in [f'python{version}', f'python{version.replace(".", "")}']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    versions_found[version] = cmd
                    print(f"✅ Python {version} found: {cmd}")
                    break
            except:
                pass
    
    if '3.11' not in versions_found and sys.version_info.minor >= 12:
        print("\n⚠️  Python 3.11 not found, but you have Python 3.12+")
        print("   Some dependencies may not be compatible.\n")
    
    return versions_found

def provide_recommendations():
    """Provide setup recommendations based on Python version"""
    versions = check_python_versions()
    
    print("\n" + "="*60)
    print("📋 RECOMMENDATIONS")
    print("="*60 + "\n")
    
    if '3.11' in versions:
        print("✅ BEST OPTION: Use Python 3.11")
        print(f"   Run: {versions['3.11']} setup/bootstrap.py\n")
    
    elif sys.version_info.minor >= 12:
        print("⚠️  You have Python 3.12+ but the project was designed for Python 3.11")
        print("\nOPTION 1: Install Python 3.11")
        print("   Ubuntu/Debian: sudo apt install python3.11 python3.11-venv")
        print("   macOS: brew install python@3.11")
        print("   Then run: python3.11 setup/bootstrap.py\n")
        
        print("OPTION 2: Try with Python 3.12 (may have issues)")
        print("   1. Delete existing venv: rm -rf venv")
        print("   2. Run: python3 setup/bootstrap.py")
        print("   3. If packages fail, use requirements_py312.txt\n")
        
        print("OPTION 3: Use Docker (most reliable)")
        print("   docker run -it python:3.11 bash")
        print("   Then clone and setup inside container\n")
    
    else:
        print("✅ Your Python version should work")
        print("   Run: python3 setup/bootstrap.py\n")
    
    print("💡 After successful setup, run:")
    print("   python3 setup/verify_setup.py")
    print("   node test_rumiai_complete_flow.js\n")

if __name__ == "__main__":
    print("🚀 RumiAI Setup Helper\n")
    provide_recommendations()