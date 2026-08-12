from typing import Any, Dict, Optional


class MemoryStore:
    """
    Lightweight in-memory store for Sentinel workflow context.

    This component keeps the latest relevant investigation context
    available to agents during the current application process.
    """

    def __init__(self):
        self._memory: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store a value under a key."""
        self._memory[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        return self._memory.get(key)

    def delete(self, key: str) -> None:
        """Remove a value from memory."""
        self._memory.pop(key, None)

    def clear(self) -> None:
        """Clear all stored memory."""
        self._memory.clear()

    def get_all(self) -> Dict[str, Any]:
        """Return a copy of the current memory."""
        return self._memory.copy()