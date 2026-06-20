import pytest
from src.lru_cache import LRUCache


# ──────────────────────────────────────────────
# (1) Basic put and get
# ──────────────────────────────────────────────
class TestBasicPutAndGet:
    def test_put_and_get_single_item(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_put_and_get_multiple_items(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_put_with_none_value(self):
        cache = LRUCache(3)
        cache.put("null", None)
        assert cache.get("null") is None


# ──────────────────────────────────────────────
# (2) Get returns None for missing key
# ──────────────────────────────────────────────
class TestGetMissingKey:
    def test_get_missing_key_returns_none(self):
        cache = LRUCache(3)
        assert cache.get("nonexistent") is None

    def test_get_missing_key_after_clear(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.clear()
        assert cache.get("a") is None

    def test_get_missing_key_after_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # evicts "a"
        assert cache.get("a") is None


# ──────────────────────────────────────────────
# (3) Update existing key with put
# ──────────────────────────────────────────────
class TestUpdateExistingKey:
    def test_update_value(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("a", 100)
        assert cache.get("a") == 100

    def test_update_marks_as_mru(self):
        """Updating a key should move it to MRU position."""
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 100)  # updates and moves "a" to MRU
        cache.put("c", 3)    # should evict "b" (now LRU), not "a"
        assert cache.get("a") == 100
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_update_preserves_size(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)
        cache.put("c", 3)
        assert cache.size() == 3


# ──────────────────────────────────────────────
# (4) LRU eviction on capacity overflow
# ──────────────────────────────────────────────
class TestEvictionOnOverflow:
    def test_evict_oldest_when_full(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # evicts "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_multiple_evictions(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # evicts "a"
        cache.put("d", 4)  # evicts "b"
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_eviction_order_preserved(self):
        cache = LRUCache(3)
        cache.put(1, "a")
        cache.put(2, "b")
        cache.put(3, "c")
        cache.put(4, "d")  # evicts (1, "a")
        cache.put(5, "e")  # evicts (2, "b")
        assert cache.get(1) is None
        assert cache.get(2) is None
        assert cache.get(3) == "c"
        assert cache.get(4) == "d"
        assert cache.get(5) == "e"


# ──────────────────────────────────────────────
# (5) Get marks item as most recently used
# ──────────────────────────────────────────────
class TestGetMarksMRU:
    def test_get_prevents_eviction(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access "a" — moves it to MRU
        assert cache.get("a") == 1
        # "b" is now LRU, adding "d" should evict "b"
        cache.put("d", 4)
        assert cache.get("b") is None
        assert cache.get("a") == 1
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_multiple_gets_affect_order(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access "c", "a" — now "b" is LRU
        cache.get("c")
        cache.get("a")
        cache.put("d", 4)  # evicts "b"
        assert cache.get("b") is None
        assert cache.get("a") == 1
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_get_on_nonexistent_does_not_affect_order(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("nonexistent") is None
        # Order should be unchanged — "a" is LRU
        cache.put("c", 3)  # evicts "a"
        assert cache.get("a") is None


# ──────────────────────────────────────────────
# (6) Evict from empty cache returns None
# ──────────────────────────────────────────────
class TestEvictEmpty:
    def test_evict_from_empty(self):
        cache = LRUCache(3)
        assert cache.evict() is None

    def test_evict_after_clear(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.clear()
        assert cache.evict() is None

    def test_evict_after_manual_eviction_all(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.evict()
        cache.evict()
        assert cache.evict() is None


# ──────────────────────────────────────────────
# (7) Evict removes and returns the LRU item
# ──────────────────────────────────────────────
class TestEvictLRU:
    def test_evict_returns_value(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.evict() == 1  # "a" is LRU
        assert cache.get("a") is None
        assert cache.size() == 2

    def test_evict_multiple_times(self):
        cache = LRUCache(3)
        cache.put("x", 10)
        cache.put("y", 20)
        cache.put("z", 30)
        assert cache.evict() == 10
        assert cache.evict() == 20
        assert cache.evict() == 30
        assert cache.size() == 0

    def test_evict_updates_lru(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.evict()  # removes "a"
        # Now "b" is LRU
        assert cache.evict() == 2


# ──────────────────────────────────────────────
# (8) Size returns correct count
# ──────────────────────────────────────────────
class TestSize:
    def test_size_empty(self):
        cache = LRUCache(5)
        assert cache.size() == 0

    def test_size_after_puts(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.size() == 3

    def test_size_after_eviction(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # evicts "a"
        assert cache.size() == 3  # still at capacity

    def test_size_after_manual_evict(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.evict()
        assert cache.size() == 1

    def test_size_after_evict_to_empty(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.evict()
        assert cache.size() == 0

    def test_size_after_clear(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.size() == 0


# ──────────────────────────────────────────────
# (9) Clear empties the cache
# ──────────────────────────────────────────────
class TestClear:
    def test_clear_empties_cache(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.size() == 0
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_clear_then_reuse(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.clear()
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.size() == 2


# ──────────────────────────────────────────────
# (10) Capacity of 1 edge case
# ──────────────────────────────────────────────
class TestCapacityOne:
    def test_put_and_get_single(self):
        cache = LRUCache(1)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_put_evicts_previous(self):
        cache = LRUCache(1)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.size() == 1

    def test_update_same_key(self):
        cache = LRUCache(1)
        cache.put("a", 1)
        cache.put("a", 100)
        assert cache.get("a") == 100
        assert cache.size() == 1

    def test_get_prevents_eviction_with_capacity_one(self):
        cache = LRUCache(1)
        cache.put("a", 1)
        cache.get("a")  # mark MRU (same effect since only one item)
        cache.put("b", 2)  # evicts "a" anyway (capacity 1)
        assert cache.get("a") is None
        assert cache.get("b") == 2


# ──────────────────────────────────────────────
# (11) Negative capacity raises ValueError
# ──────────────────────────────────────────────
class TestNegativeCapacity:
    def test_negative_capacity_raises(self):
        with pytest.raises(ValueError, match="capacity must be positive"):
            LRUCache(-1)

    def test_negative_large_capacity_raises(self):
        with pytest.raises(ValueError):
            LRUCache(-100)


# ──────────────────────────────────────────────
# (12) Zero capacity raises ValueError
# ──────────────────────────────────────────────
class TestZeroCapacity:
    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError, match="capacity must be positive"):
            LRUCache(0)


# ──────────────────────────────────────────────
# (13) Stress test: 1000 puts then 1000 gets
# verifying LRU order preserved
# ──────────────────────────────────────────────
class TestStress:
    def test_1000_puts_and_gets(self):
        N = 1000
        cache = LRUCache(N)

        # Put N items
        for i in range(N):
            cache.put(i, f"val_{i}")

        assert cache.size() == N

        # Verify all items present
        for i in range(N):
            assert cache.get(i) == f"val_{i}"

        # Add one more to trigger eviction of the first (key=0)
        cache.put(N, f"val_{N}")
        assert cache.size() == N
        assert cache.get(0) is None, "Key 0 should have been evicted (oldest)"

        # Remaining items should be keys 1..N
        for i in range(1, N + 1):
            assert cache.get(i) == f"val_{i}"

    def test_stress_eviction_order(self):
        """Insert more than capacity and verify strict LRU ordering."""
        N = 100
        cache = LRUCache(N)

        # Insert N items
        for i in range(N):
            cache.put(i, i)

        # Access first half to make them MRU
        for i in range(N // 2):
            cache.get(i)

        # Insert N more items — each should evict the oldest untouched
        # After the gets above, order is [N//2, N//2+1, ..., N-1, 0, 1, ..., N//2-1]
        for j in range(N, N + N):
            cache.put(j, j)

        # The first N//2 evicted should be the untouched ones: N//2 .. N-1
        for i in range(N // 2, N):
            assert cache.get(i) is None, f"Key {i} should have been evicted"

        # The remaining should be [0..N//2-1] and [N..N+N-1]
        assert cache.size() == N
        for i in range(N // 2):
            assert cache.get(i) == i
        for j in range(N, N + N):
            assert cache.get(j) == j
