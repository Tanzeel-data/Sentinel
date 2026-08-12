from app.agents.verify import VerifyAgent


def main():
    print("=" * 70)
    print("SENTINEL VERIFY AGENT")
    print("=" * 70)

    agent = VerifyAgent()

    test_cases = [
        "Verify whether the high resource usage issue on SRV-002 has been resolved.",

        "Verify whether the Auth-Service error issue on SRV-001 has been resolved.",

        "Verify the current infrastructure state and determine whether the previously identified issues are resolved.",
    ]

    for question in test_cases:
        print()
        print("USER:", question)
        print("-" * 70)

        try:
            response = agent.invoke(question)
            print(response)

        except Exception as exc:
            print(f"Verification failed: {exc}")


if __name__ == "__main__":
    main()