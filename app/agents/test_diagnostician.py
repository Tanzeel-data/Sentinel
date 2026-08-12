from app.agents.diagnostician import Diagnostician


def main():
    print("=" * 70)
    print("SENTINEL DIAGNOSTICIAN")
    print("=" * 70)

    agent = Diagnostician()

    questions = [
        "Why might there be infrastructure problems right now?",
        "Investigate the relationship between the current resource usage and error activity.",
        "What is the most likely cause of the current infrastructure issues?",
    ]

    for question in questions:
        print(f"\nUSER: {question}")
        print("-" * 70)

        try:
            response = agent.invoke(question)
            print(response)

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()