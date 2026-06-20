"""LRU Cache implementation using OrderedDict.

Provides a fixed-capacity Least Recently Used (LRU) cache
with get, put, evict, size, and clear operations.
"""

from typing import Any, Optional
from collections import OrderedDict


class LRUCache:
    """A fixed-capacity LRU cache.

    Uses an OrderedDict internally where the order reflects
    recency of access: the end is most recently used,
    the front (first) is the least recently used.
    """

    def __init__(self, capacity: int) -> None:
        """Initialize the cache with a given capacity.

        Args:
            capacity: Maximum number of items the cache can hold.

        Raises:
            ValueError: If capacity is not positive.
        """
        if capacity <= 0:
            raise ValueError('capacity must be positive')
        self._capacity = capacity
        self._cache: OrderedDict[Any, Any] = OrderedDict()

    def get(self, key: Any) -> Optional[Any]:
        """Retrieve the value associated with the key.

        Marks the key as most recently used.

        Args:
            key: The key to look up.

        Returns:
            The associated value if present, else None.
        """
        if key not in self._cache:
            return None
        # Move to end (most recently used position)
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair.

        If the key already exists, its value is updated and it
        is marked as most recently used. If the key is new and
        the cache is at capacity, the least recently used item
        is evicted before insertion.

        Args:
            key: The key to insert or update.
            value: The value to associate with the key.
        """
        if key in self._cache:
            # Update existing key — move to end
            self._cache[key] = value
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._capacity:
                # Evict the LRU item (first item)
                self._cache.popitem(last=False)
            self._cache[key] = value

    def evict(self) -> Optional[Any]:
        """Manually evict and return the least recently used item's value.

        Returns:
            The value of the evicted item, or None if the cache is empty.
        """
        if not self._cache:
            return None
        _, value = self._cache.popitem(last=False)
        return value

    def size(self) -> int:
        """Return the current number of items in the cache.

        Returns:
            The number of items currently stored.
        """
        return len(self._cache)

    def clear(self) -> None:
        """Remove all items from the cache."""
        self._cache.clear()
