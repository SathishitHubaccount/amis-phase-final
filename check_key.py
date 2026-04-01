import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=KEY)
try:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("✅ Key is VALID and has credits")
    print(f"   Response: {msg.content[0].text}")
except anthropic.AuthenticationError as e:
    print(f"❌ Invalid API key: {e}")
except Exception as e:
    err = str(e)
    if "credit balance is too low" in err or "insufficient" in err.lower():
        print("❌ Key is valid but OUT OF CREDITS")
    else:
        print(f"❌ Error: {e}")
