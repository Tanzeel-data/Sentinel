from app.agents.monitoring_agent import MonitoringAgent


def main():
    print("\n=== SENTINEL MONITORING AGENT ===")

    agent = MonitoringAgent()

    questions = [
        "What is the current server status?",
        "Are there any servers with high resource usage?",
        "Show me the latest errors.",
        "Give me a summary of the logs.",
    ]

    for question in questions:
        print(f"\nUSER: {question}")

        try:
            response = agent.invoke(question)
            print(f"SENTINEL: {response}")

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()