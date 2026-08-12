import os
import requests
from dotenv import load_dotenv

# Load the same .env file used by Sentinel
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY was not found in the .env file."
    )

URL = "https://generativelanguage.googleapis.com/v1beta/models"

response = requests.get(
    URL,
    params={"key": API_KEY},
    timeout=30,
)

response.raise_for_status()

data = response.json()

models = data.get("models", [])

print("\n" + "=" * 80)
print("SENTINEL - AVAILABLE GEMINI MODELS")
print("=" * 80)

usable_models = []

for model in models:
    name = model.get("name", "")
    display_name = model.get("displayName", "")
    methods = model.get("supportedGenerationMethods", [])

    if "generateContent" in methods:
        model_id = name.replace("models/", "")

        usable_models.append(model_id)

        print(f"\nModel: {model_id}")
        print(f"Display: {display_name}")
        print(f"Methods: {', '.join(methods)}")

print("\n" + "=" * 80)
print(f"TOTAL: {len(usable_models)} models support generateContent")
print("=" * 80)

print("\nModels available to Sentinel:\n")

for model in usable_models:
    print(f"  - {model}")

print("\n" + "=" * 80)