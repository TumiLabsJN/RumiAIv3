#!/usr/bin/env python3
"""
Generate Python 3.12 compatible requirements file
"""

import sys
from pathlib import Path

# Python 3.12 compatible versions
PY312_VERSIONS = {
    'torch': '2.2.0',
    'torchvision': '0.17.0',
    'numpy': '1.26.4',
    'mediapipe': '0.10.14',
    'ultralytics': '8.3.0',
    'scipy': '1.11.4',  # This version works with Python 3.12
}

def generate_py312_requirements():
    """Generate a Python 3.12 compatible requirements file"""
    
    # Read original requirements.txt
    requirements_path = Path(__file__).parent.parent / 'requirements.txt'
    if not requirements_path.exists():
        print("Error: requirements.txt not found")
        return False
    
    with open(requirements_path, 'r') as f:
        lines = f.readlines()
    
    # Add setuptools at the beginning if not present
    has_setuptools = any('setuptools' in line for line in lines)
    
    # Process each line
    new_lines = []
    
    # Add setuptools first if needed
    if not has_setuptools:
        new_lines.append('# Core dependencies')
        new_lines.append('setuptools>=68.0.0  # Required for pkg_resources in Python 3.12')
        # Skip the original "# Core dependencies" line
        skip_next_core_deps = True
    else:
        skip_next_core_deps = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            if skip_next_core_deps and line == '# Core dependencies':
                skip_next_core_deps = False
                continue  # Skip this line as we already added it
            new_lines.append(line)
            continue
        
        # Check if this package needs version update
        updated = False
        for package, new_version in PY312_VERSIONS.items():
            if line.startswith(f'{package}=='):
                new_lines.append(f'{package}=={new_version}')
                if 'Updated for Python 3.12' not in line:
                    new_lines[-1] += '  # Updated for Python 3.12 compatibility'
                updated = True
                break
        
        if not updated:
            new_lines.append(line)
    
    # Write new requirements_py312.txt
    output_path = Path(__file__).parent.parent / 'requirements_py312.txt'
    with open(output_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Generated {output_path}")
    return True

if __name__ == "__main__":
    generate_py312_requirements()