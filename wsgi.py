"""
WSGI entry point for PythonAnywhere.

Copy the contents of this file into the WSGI configuration file
on PythonAnywhere, BUT change 'yourusername' to your actual username.
"""

import sys

# ⚠️ CHANGE 'yourusername' to your actual PythonAnywhere username!
path = '/home/yourusername/attendance'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
