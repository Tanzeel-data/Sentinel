from app.memory import MemoryStore


def main():
    print("=== SENTINEL MEMORY TEST ===")

    memory = MemoryStore()

    memory.set(
        "current_incident",
        {
            "server_id": "SRV-002",
            "hostname": "db-prod-1",
            "cpu": 88.5,
            "memory": 92.3,
        },
    )

    memory.set(
        "error_summary",
        {
            "server_id": "SRV-001",
            "service": "Auth-Service",
            "error_count": 1614,
        },
    )

    print("\n=== STORED MEMORY ===")
    print(memory.get_all())

    print("\n=== CURRENT INCIDENT ===")
    print(memory.get("current_incident"))

    print("\n=== ERROR SUMMARY ===")
    print(memory.get("error_summary"))

    print("\n=== MEMORY TEST PASSED ===")


if __name__ == "__main__":
    main()