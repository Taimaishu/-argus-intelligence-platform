#!/usr/bin/env python3
"""
Create Argus USB Deployment Package

This script prepares a portable USB deployment of Argus Intelligence Platform
that works on both Windows 10 and Linux.

Usage:
    python3 create_usb_deployment.py /path/to/usb
    python3 create_usb_deployment.py --zip  # Create zip file instead
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import zipfile


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_step(step, total, text):
    """Print step progress."""
    print(f"[{step}/{total}] {text}")


def check_requirements():
    """Check if required tools are available."""
    print_step(1, 6, "Checking requirements...")

    # Check npm
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("  ✓ npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ✗ npm not found - needed to build frontend")
        return False

    # Check python
    try:
        subprocess.run([sys.executable, "--version"], capture_output=True, check=True)
        print(f"  ✓ Python found: {sys.executable}")
    except subprocess.CalledProcessError:
        print("  ✗ Python not found")
        return False

    return True


def build_frontend():
    """Build frontend for production."""
    print_step(2, 6, "Building frontend...")

    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print(f"  ✗ Frontend directory not found: {frontend_dir}")
        return False

    # Install dependencies
    print("  Installing dependencies...")
    result = subprocess.run(
        ["npm", "install"],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ npm install failed: {result.stderr}")
        return False

    # Build
    print("  Building production bundle...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ npm build failed: {result.stderr}")
        return False

    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists():
        print(f"  ✗ Build output not found: {dist_dir}")
        return False

    print(f"  ✓ Frontend built successfully")
    return True


def create_deployment_structure(target_path):
    """Create deployment directory structure."""
    print_step(3, 6, f"Creating deployment structure at {target_path}...")

    target = Path(target_path)
    target.mkdir(parents=True, exist_ok=True)

    # Create directories
    dirs = [
        target / "backend",
        target / "frontend-dist",
        target / "storage" / "database",
        target / "storage" / "uploads",
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {dir_path.relative_to(target)}")

    return True


def copy_backend(target_path):
    """Copy backend files."""
    print_step(4, 6, "Copying backend files...")

    source = Path(__file__).parent / "backend"
    target = Path(target_path) / "backend"

    # Copy backend directory
    if target.exists():
        shutil.rmtree(target)

    print("  Copying backend directory...")
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.log',
            '.pytest_cache',
            'venv',
            'storage',
            '*.db',
            '*.db-shm',
            '*.db-wal'
        )
    )

    # Copy requirements.txt
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        shutil.copy(req_file, target.parent / "requirements.txt")

    print(f"  ✓ Backend files copied")
    return True


def copy_frontend(target_path):
    """Copy built frontend files."""
    print_step(5, 6, "Copying frontend files...")

    source = Path(__file__).parent / "frontend" / "dist"
    target = Path(target_path) / "frontend-dist"

    if not source.exists():
        print(f"  ✗ Frontend dist not found: {source}")
        return False

    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(source, target)

    print(f"  ✓ Frontend files copied")
    return True


def copy_launchers(target_path):
    """Copy launcher scripts."""
    print_step(6, 6, "Copying launcher scripts and documentation...")

    source_dir = Path(__file__).parent
    target = Path(target_path)

    files_to_copy = [
        "START_ARGUS_USB.bat",
        "START_ARGUS_USB.sh",
        "CREATE_USB_DEPLOYMENT.md",
        "README.md",
    ]

    for filename in files_to_copy:
        source_file = source_dir / filename
        if source_file.exists():
            shutil.copy(source_file, target / filename)
            print(f"  ✓ Copied {filename}")

            # Make shell scripts executable
            if filename.endswith('.sh'):
                os.chmod(target / filename, 0o755)

    # Create .env template
    env_template = target / "backend" / ".env.template"
    with open(env_template, 'w') as f:
        f.write("""# Argus Configuration Template
# Copy this file to .env and customize

# Environment
DEBUG=False
ENVIRONMENT=production

# Storage (set by launcher script)
STORAGE_PATH=./storage_external
DATABASE_PATH=./storage/database/research_tool.db
UPLOAD_DIR=./storage/uploads

# API Keys (users enter via UI, leave empty)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Security
API_KEY=change-this-to-a-random-string
SECRET_KEY=change-this-to-another-random-string

# CORS (adjust if needed)
CORS_ORIGINS=["http://localhost:5173"]

# Features
FEATURE_EPSTEIN_MODE=True
FEATURE_URL_EXTRACTION=False
""")
    print(f"  ✓ Created .env.template")

    return True


def create_readme(target_path):
    """Create README for USB deployment."""
    readme_path = Path(target_path) / "USB_README.txt"

    with open(readme_path, 'w') as f:
        f.write("""
Argus Intelligence Platform - USB Portable Edition
===================================================

QUICK START:

  Windows:
    1. Double-click START_ARGUS_USB.bat
    2. Follow the prompts
    3. Browser will open automatically

  Linux:
    1. Open terminal in this directory
    2. Run: ./START_ARGUS_USB.sh
    3. Follow the prompts
    4. Browser will open automatically

FIRST TIME SETUP:

  1. The setup wizard will guide you through API key configuration
  2. You'll need at least one API key from:
     - OpenAI (recommended): https://platform.openai.com/api-keys
     - Anthropic: https://console.anthropic.com/account/keys
     - Or use Ollama (free, local): https://ollama.ai

STORAGE OPTIONS:

  When prompted, choose where to store data:

  1. USB Drive - Simple, but limited by USB size
  2. External HDD - Recommended for large datasets
  3. System Temp - Temporary, cleared on restart
  4. Custom Path - Specify your own location

REQUIREMENTS:

  - Python 3.10 or higher
  - 2GB+ RAM
  - 500MB+ free space (more for documents)

STOPPING ARGUS:

  - Windows: Press any key in the launcher window
  - Linux: Press Enter in the terminal

DOCUMENTATION:

  See CREATE_USB_DEPLOYMENT.md for detailed information

SUPPORT:

  - Issues: https://github.com/anthropics/argus/issues
  - Docs: See CREATE_USB_DEPLOYMENT.md

""")
    print(f"  ✓ Created USB_README.txt")


def create_zip(source_path, output_name="argus-usb-portable.zip"):
    """Create zip file of deployment."""
    print(f"\nCreating zip file: {output_name}")

    source = Path(source_path)

    with zipfile.ZipFile(output_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in source.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(source.parent)
                zipf.write(file, arcname)
                print(f"  Added: {arcname}")

    print(f"\n✓ Created {output_name}")
    print(f"  Size: {os.path.getsize(output_name) / 1024 / 1024:.1f} MB")


def main():
    """Main deployment function."""
    print_header("Argus USB Deployment Creator")

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 create_usb_deployment.py /path/to/usb")
        print("  python3 create_usb_deployment.py --zip")
        sys.exit(1)

    create_zip_file = sys.argv[1] == "--zip"
    target_path = "argus-usb-deployment" if create_zip_file else sys.argv[1]

    # Check requirements
    if not check_requirements():
        print("\n✗ Requirements check failed")
        sys.exit(1)

    # Build frontend
    if not build_frontend():
        print("\n✗ Frontend build failed")
        sys.exit(1)

    # Create structure
    if not create_deployment_structure(target_path):
        print("\n✗ Failed to create deployment structure")
        sys.exit(1)

    # Copy files
    if not copy_backend(target_path):
        print("\n✗ Failed to copy backend files")
        sys.exit(1)

    if not copy_frontend(target_path):
        print("\n✗ Failed to copy frontend files")
        sys.exit(1)

    if not copy_launchers(target_path):
        print("\n✗ Failed to copy launcher scripts")
        sys.exit(1)

    create_readme(target_path)

    # Create zip if requested
    if create_zip_file:
        create_zip(target_path)
        print(f"\nCleaning up temporary directory...")
        shutil.rmtree(target_path)

    # Success message
    print_header("Deployment Complete!")

    if create_zip_file:
        print(f"✓ Zip file created: argus-usb-portable.zip")
        print(f"\nExtract the zip file to your USB drive and run the launcher script.")
    else:
        print(f"✓ Deployment created at: {target_path}")
        print(f"\nNext steps:")
        print(f"  Windows: Run {target_path}/START_ARGUS_USB.bat")
        print(f"  Linux:   Run {target_path}/START_ARGUS_USB.sh")

    print(f"\nSee USB_README.txt and CREATE_USB_DEPLOYMENT.md for instructions.")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
