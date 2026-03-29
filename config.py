"""
AMIS Configuration
Set your API key in .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── LLM Configuration ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found. Please create a .env file with your API key.\n"
        "See .env.example for template."
    )
MODEL_NAME = "claude-sonnet-4-20250514"
TEMPERATURE = 0.3  # Low temperature for consistent analytical decisions
MAX_TOKENS = 4096

# ── Agent Configuration ──
VERBOSE = True  # Set to True to see agent's thinking process
