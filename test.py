print("Hello, Rubi! Python is running.")
import sys
print(f"Python executable: {sys.executable}")
import os
print(f"Current working directory: {os.getcwd()}")
try:
    import flask
    print(f"Flask version: {flask.__version__}")
except ImportError:
    print("Flask is NOT installed or cannot be imported.")