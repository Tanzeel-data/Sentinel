import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in .env")


MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


print("\n" + "=" * 80)
print("SENTINEL - GEMINI GENERATION COMPATIBILITY TEST")
print("=" * 80)


for model in MODELS:

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Reply with exactly: SENTINEL TEST OK"
                    }
                ]
            }
        ]
    }

    try:

        response = requests.post(
            url,
            params={"key": API_KEY},
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()

            text = (
                data["candidates"][0]["content"]["parts"][0]["text"]
            )

            print(f"\n[OK] {model}")
            print(f"     Response: {text}")

        else:
            data = response.json()

            error = data.get("error", {})

            print(f"\n[FAILED] {model}")
            print(f"     Status: {response.status_code}")
            print(f"     Reason: {error.get('status')}")
            print(f"     Message: {error.get('message')}")

    except Exception as exc:

        print(f"\n[ERROR] {model}")
        print(f"       {exc}")


print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)