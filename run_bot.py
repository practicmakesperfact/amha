"""
Simple startup script for AMHABINGO Bot (Polling Mode).
This ensures the Python path is set correctly.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
from backend.run_polling import main

if __name__ == "__main__":
    main()
