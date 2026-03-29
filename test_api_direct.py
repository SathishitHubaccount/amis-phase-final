"""
Direct API key test - bypassing .env file
"""
from anthropic import Anthropic

import os
from dotenv import load_dotenv
load_dotenv()

# Load API key from environment
API_KEY = os.getenv("ANTHROPIC_API_KEY")

print("=" * 80)
print("DIRECT API KEY TEST (bypassing .env file)")
print("=" * 80)
print(f"API Key: {API_KEY[:25]}...{API_KEY[-15:]}")
print("=" * 80)

try:
    client = Anthropic(api_key=API_KEY)

    print("\nSending test message to Claude API...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello in exactly 5 words."}
        ]
    )

    print("\nSUCCESS! API key is working!")
    print("=" * 80)
    print("Response:", message.content[0].text)
    print("=" * 80)
    print(f"Token usage: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
    print("=" * 80)

except Exception as e:
    print("\nERROR! API key test failed!")
    print("=" * 80)
    print(f"Error: {str(e)}")
    print("=" * 80)
