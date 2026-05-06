import sys
import os

def check_dependencies():
    missing = []
    try:
        import telegram
    except ImportError:
        missing.append("python-telegram-bot")
    
    try:
        import torch
    except ImportError:
        missing.append("torch")
        
    try:
        import transformers
    except ImportError:
        missing.append("transformers")

    if missing:
        print("❌ Missing dependencies:", ", ".join(missing))
        print("Run: pip install " + " ".join(missing))
        sys.exit(1)

check_dependencies()
