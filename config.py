import os
import sys

# Load all required API keys from Replit Secrets (os.environ)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

# Validate that all keys are present
missing = []
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not DEEPSEEK_API_KEY:
    missing.append("DEEPSEEK_API_KEY")
if not ELEVENLABS_API_KEY:
    missing.append("ELEVENLABS_API_KEY")
if not PIXABAY_API_KEY:
    missing.append("PIXABAY_API_KEY")

if missing:
    print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
    print("Please add them to Replit Secrets.")
    sys.exit(1)

# Optional constants
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
PIXABAY_VIDEO_PER_PAGE = 5
PIXABAY_MUSIC_PER_PAGE = 1