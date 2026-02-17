import sys
import traceback

try:
    print("Attempting import...")
    import facebook_scraper
    print("Import successful!")
    print(f"File: {facebook_scraper.__file__}")
except Exception:
    print("Import failed!")
    traceback.print_exc()
