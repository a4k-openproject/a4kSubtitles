# Add vendor directory to sys.path for local dependencies if not already present
import os, sys
vendor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vendor')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)
