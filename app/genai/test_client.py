import logging

from app.genai.client import get_gemini_client


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)


def main():
    client = get_gemini_client()

    print("\n=== GEMINI CONFIGURATION ===")
    print("Models:")
    for model in client.models:
        print(" -", model)

    print("\n=== GEMINI TEST ===")

    response = client.invoke(
        "Reply with exactly: Sentinel Gemini test successful."
    )

    print("\nResponse:")
    print(response)


if __name__ == "__main__":
    main()