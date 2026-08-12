from app.agents.router import SentinelRouter


def main():
    print("=== SENTINEL ROUTER TEST ===")

    router = SentinelRouter()

    queries = [
        "What is the current server status?",
        "Are there any servers with high resource usage?",
        "Show me the latest errors.",
        "Are there any active infrastructure incidents?",
        "What is the most important issue right now?",
        "Is there a relationship between resource usage and the errors?",
    ]

    for query in queries:
        print()
        print(f"USER: {query}")

        route = router._route(query)

        print(f"ROUTE: {route}")

        try:
            response = router.invoke(query)

            print("SENTINEL:")
            print(response)

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()