#!/usr/bin/env python3
"""
Deployment CLI Entry Point

This script provides a command-line interface for managing deployment steps and strategies.
It uses Google Fire to create a CLI from the DeploymentCLI class.

Usage:
    python deploy.py <command> [arguments]
    
Examples:
    # List available steps and strategies
    python deploy.py info
    
    # List available steps
    python deploy.py list_steps
    
    # List available strategies
    python deploy.py list_strategies
    
    # Install a step
    python deploy.py install_step docker-deploy
    
    # Uninstall a step
    python deploy.py uninstall_step docker-deploy
    
    # Install a strategy
    python deploy.py install_strategy docker-deploy
    
    # Uninstall a strategy
    python deploy.py uninstall_strategy docker-deploy
    
    # Validate a step
    python deploy.py validate_step native-backend-deploy
    
    # Get step metadata
    python deploy.py get_step_metadata native-frontend-deploy
    
    # Set custom project root and log level
    python deploy.py --project_root=/path/to/project --log_level=DEBUG install_step docker-deploy
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import deployment modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from deployment.cli import main
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure you have installed the required dependencies:")
    print("  pip install fire")
    sys.exit(1)


if __name__ == "__main__":
    main()
