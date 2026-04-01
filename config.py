"""
AMIS Configuration
Set your API key in .env file
"""
import os
from dotenv import load_dotenv

# Fix: platform.system() hangs on this machine due to slow DNS/hostname lookup.
# The anthropic SDK calls get_platform() → platform.uname() → socket.gethostname()
# which stalls. Pre-patch it to return immediately.
try:
    import anthropic._base_client as _abc
    _abc.get_platform = lambda: "Windows"
    _abc.get_architecture = lambda: "x64"
    _abc.get_python_runtime = lambda: "CPython"
    _abc.get_python_version = lambda: "3.13.0"
    _abc.platform_headers.cache_clear()
except Exception:
    pass

# Load environment variables from .env file
load_dotenv(override=True)

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
