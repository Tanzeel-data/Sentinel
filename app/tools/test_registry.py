from app.tools.registry import get_tools


def main():
    tools = get_tools()

    print("\n=== SENTINEL TOOLS ===")

    for tool in tools:
        print(f"- {tool.name}")
        print(f"  {tool.description.splitlines()[0]}")

    print(f"\nTotal tools: {len(tools)}")


if __name__ == "__main__":
    main()