"""
Wrapper script that properly sets sys.path before running the Streamlit app.
This ensures the studymate_rag package can be imported.
"""
import sys
from pathlib import Path

# Get the absolute path to the src directory
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run the app
from studymate_rag.ui.app import main

if __name__ == "__main__":
    main()
