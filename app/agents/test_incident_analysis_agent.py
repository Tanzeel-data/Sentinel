from app.agents.incident_analysis_agent import IncidentAnalysisAgent


def main():
    print("\n=== SENTINEL INCIDENT ANALYSIS AGENT ===\n")

    agent = IncidentAnalysisAgent()

    questions = [
        "Are there any active infrastructure incidents?",
        "Analyze the current server telemetry and identify the most important issue.",
        "Is there a relationship between resource usage and the current errors?",
    ]

    for question in questions:
        print(f"USER: {question}")

        try:
            response = agent.invoke(question)
            print(f"SENTINEL:\n{response}\n")
        except Exception as exc:
            print(f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()