import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure explicit UTF-8 load of .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise ValueError(f"GROQ_API_KEY missing or failed to load from {env_path}")