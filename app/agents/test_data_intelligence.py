from app.agents.data_intelligence import DataIntelligenceAgent


def main():
    print("=" * 70)
    print("SENTINEL DATA INTELLIGENCE AGENT")
    print("=" * 70)

    agent = DataIntelligenceAgent()

    questions = [
        "Which servers currently have elevated resource usage?",
        "What are the most significant error patterns in the infrastructure?",
        "Give me a concise overview of the current infrastructure telemetry.",
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