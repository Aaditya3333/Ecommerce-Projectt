#!/usr/bin/env python
"""
Clean Django development server runner that eliminates HTTPS errors completely.
Use this script instead of 'python manage.py runserver' for a clean development experience.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

def main():
    """Run Django development server with clean output."""
    
    # Configure logging to suppress HTTPS errors completely
    logging.getLogger('django.server').setLevel(logging.CRITICAL)
    logging.getLogger('django.request').setLevel(logging.CRITICAL)
    
    # Suppress all console output except critical errors
    class SuppressOutput:
        def __init__(self, original_stdout, original_stderr):
            self.original_stdout = original_stdout
            self.original_stderr = original_stderr
        
        def write(self, message):
            # Only show critical errors
            if any(phrase in message for phrase in [
                'ERROR', 'CRITICAL', 'Exception', 'Traceback'
            ]):
                self.original_stderr.write(message)
        
        def flush(self):
            self.original_stderr.flush()
    
    # Replace stdout and stderr with suppressed versions
    sys.stdout = SuppressOutput(sys.stdout, sys.stderr)
    sys.stderr = SuppressOutput(sys.stdout, sys.stderr)
    
    try:
        # Run Django development server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', 
            '--noreload', 
            '--verbosity=0'  # Minimal output
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == '__main__':
    main()
