"""
Simple test script to verify Anthropic API key is working
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

print("=" * 80)
print("ANTHROPIC API KEY TEST")
print("=" * 80)
print(f"API Key loaded: {api_key[:25]}...{api_key[-15:]}")
print(f"API Key length: {len(api_key)} characters")
print("=" * 80)

# Try to make a simple API call
try:
    client = Anthropic(api_key=api_key)

    print("\nSending test message to Claude API...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello in exactly 5 words."}
        ]
    )

    print("\n✅ SUCCESS! API key is working correctly!")
    print("=" * 80)
    print("Claude's response:")
    print(message.content[0].text)
    print("=" * 80)
    print(f"\nToken usage:")
    print(f"  Input tokens: {message.usage.input_tokens}")
    print(f"  Output tokens: {message.usage.output_tokens}")
    print("=" * 80)

except Exception as e:
    print("\n❌ ERROR! API key test failed!")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("=" * 80)
