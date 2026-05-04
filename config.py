import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
YOUTUBE_CLIENT_SECRET = "youtube_secret.json"

# Configuración del canal
CHANNEL_NICHE = "legal explanations"
VIDEO_LANGUAGE = "English"
VIDEOS_PER_DAY = 1
