from app.agents.remediation import RemediationAgent


def main():
    agent = RemediationAgent()

    print("=" * 70)
    print("SENTINEL REMEDIATION AGENT")
    print("=" * 70)

    questions = [
        "What remediation should be recommended for the current infrastructure issues?",

        "What should we do about the server with elevated CPU and memory usage?",

        "What remediation is appropriate for the repeated Auth-Service errors?",
    ]

    for question in questions:
        print()
        print(f"USER: {question}")
        print("-" * 70)

        try:
            response = agent.invoke(question)
            print(response)

        except Exception as exc:
            print(f"Remediation failed: {exc}")


if __name__ == "__main__":
    main()