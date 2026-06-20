"""Tests for LinkedList — src/linked_list.py."""

import pytest
from src.linked_list import LinkedList


# ── Empty list ────────────────────────────────────────────────────────────────

def test_empty_list_len_zero():
    """Len of empty list is 0."""
    ll = LinkedList[int]()
    assert len(ll) == 0


def test_empty_list_to_list():
    """to_list() returns [] for an empty list."""
    ll = LinkedList[str]()
    assert ll.to_list() == []


def test_empty_list_iteration():
    """Iterating an empty list yields nothing."""
    ll = LinkedList[int]()
    assert list(ll) == []


def test_empty_list_repr():
    """repr of empty list shows LinkedList([])."""
    ll = LinkedList[int]()
    assert repr(ll) == "LinkedList([])"


def test_empty_list_search():
    """Search on an empty list returns False."""
    ll = LinkedList[int]()
    assert ll.search(42) is False


def test_remove_from_empty_raises():
    """Remove on an empty list raises ValueError."""
    ll = LinkedList[int]()
    with pytest.raises(ValueError, match="Cannot remove from an empty list"):
        ll.remove(1)


# ── Append ────────────────────────────────────────────────────────────────────

def test_append_single():
    """Append one element, verify len and order."""
    ll = LinkedList[int]()
    ll.append(10)
    assert len(ll) == 1
    assert ll.to_list() == [10]


def test_append_multiple():
    """Append several elements, verify order."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert ll.to_list() == [1, 2, 3]
    assert len(ll) == 3


def test_append_different_types():
    """LinkedList works with strings."""
    ll = LinkedList[str]()
    ll.append("hello")
    ll.append("world")
    assert ll.to_list() == ["hello", "world"]


# ── Prepend ───────────────────────────────────────────────────────────────────

def test_prepend_single():
    """Prepend one element."""
    ll = LinkedList[int]()
    ll.prepend(42)
    assert len(ll) == 1
    assert ll.to_list() == [42]


def test_prepend_multiple():
    """Prepend several — last prepended becomes head."""
    ll = LinkedList[int]()
    ll.prepend(1)
    ll.prepend(2)
    ll.prepend(3)
    assert ll.to_list() == [3, 2, 1]
    assert len(ll) == 3


# ── Append + Prepend mixed ────────────────────────────────────────────────────

def test_append_and_prepend_mixed():
    """Mix append and prepend, verify correct order."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.prepend(0)
    ll.append(2)
    ll.prepend(-1)
    assert ll.to_list() == [-1, 0, 1, 2]


# ── Remove ────────────────────────────────────────────────────────────────────

def test_remove_existing():
    """Remove existing element returns True and shortens the list."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    result = ll.remove(2)
    assert result is True
    assert ll.to_list() == [1, 3]
    assert len(ll) == 2


def test_remove_nonexistent():
    """Remove non-existing element returns False and list is unchanged."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    result = ll.remove(99)
    assert result is False
    assert ll.to_list() == [1, 2, 3]
    assert len(ll) == 3


def test_remove_first_occurrence():
    """Remove only deletes the first occurrence."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(1)
    ll.append(3)
    result = ll.remove(1)
    assert result is True
    assert ll.to_list() == [2, 1, 3]


def test_remove_head():
    """Remove the head element."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.remove(1)
    assert ll.to_list() == [2, 3]
    assert len(ll) == 2


def test_remove_tail():
    """Remove the tail element — O(1) tail ref stays correct."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.remove(3)
    assert ll.to_list() == [1, 2]
    assert len(ll) == 2
    # Append after tail removal must still work
    ll.append(4)
    assert ll.to_list() == [1, 2, 4]


def test_remove_only_element():
    """Remove the sole element leaves an empty list."""
    ll = LinkedList[int]()
    ll.append(42)
    ll.remove(42)
    assert len(ll) == 0
    assert ll.to_list() == []
    # Append after emptying must still work
    ll.append(99)
    assert ll.to_list() == [99]


# ── Search ────────────────────────────────────────────────────────────────────

def test_search_existing():
    """Search finds an existing element."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert ll.search(2) is True
    assert ll.search(1) is True
    assert ll.search(3) is True


def test_search_nonexistent():
    """Search returns False for missing element."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert ll.search(99) is False


# ── to_list ───────────────────────────────────────────────────────────────────

def test_to_list_preserves_order():
    """to_list returns elements in insertion order after mixed ops."""
    ll = LinkedList[int]()
    ll.append(2)
    ll.prepend(1)
    ll.append(3)
    ll.prepend(0)
    ll.remove(2)
    assert ll.to_list() == [0, 1, 3]


# ── __len__ ───────────────────────────────────────────────────────────────────

def test_len_tracks_operations():
    """len() stays correct through appends, prepends, and removes."""
    ll = LinkedList[int]()
    assert len(ll) == 0
    ll.append(1)
    assert len(ll) == 1
    ll.prepend(0)
    assert len(ll) == 2
    ll.remove(0)
    assert len(ll) == 1
    ll.remove(1)
    assert len(ll) == 0


# ── __iter__ ──────────────────────────────────────────────────────────────────

def test_iteration():
    """for-in loop yields elements in order."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    collected = []
    for item in ll:
        collected.append(item)
    assert collected == [1, 2, 3]


# ── __repr__ ──────────────────────────────────────────────────────────────────

def test_repr():
    """repr returns LinkedList([...]) format."""
    ll = LinkedList[int]()
    ll.append(5)
    ll.append(10)
    assert repr(ll) == "LinkedList([5, 10])"


# ── Stress / edge cases ───────────────────────────────────────────────────────

def test_large_list():
    """1000 appends and verifies length and first/last."""
    ll = LinkedList[int]()
    for i in range(1000):
        ll.append(i)
    assert len(ll) == 1000
    as_list = ll.to_list()
    assert as_list[0] == 0
    assert as_list[-1] == 999
    assert len(as_list) == 1000


def test_float_type():
    """LinkedList works with floats."""
    ll = LinkedList[float]()
    ll.append(3.14)
    ll.append(2.71)
    ll.prepend(1.61)
    assert ll.to_list() == [1.61, 3.14, 2.71]
    assert ll.search(2.71) is True
    assert ll.search(99.9) is False


def test_remove_all_elements_one_by_one():
    """Removing all elements one by one ends with empty list."""
    ll = LinkedList[int]()
    for i in range(5):
        ll.append(i)
    for i in range(5):
        assert ll.remove(i) is True
    assert len(ll) == 0
    assert ll.to_list() == []


# ── reverse ───────────────────────────────────────────────────────────────────

def test_reverse_empty():
    """Reversing an empty list does not raise and remains empty."""
    ll = LinkedList[int]()
    ll.reverse()
    assert ll.to_list() == []
    assert len(ll) == 0


def test_reverse_single():
    """Reversing a single-element list leaves it unchanged."""
    ll = LinkedList[int]()
    ll.append(42)
    ll.reverse()
    assert ll.to_list() == [42]
    assert len(ll) == 1


def test_reverse_two_elements():
    """Reversing [A, B] produces [B, A]."""
    ll = LinkedList[str]()
    ll.append("A")
    ll.append("B")
    ll.reverse()
    assert ll.to_list() == ["B", "A"]


def test_reverse_multiple():
    """Reversing [1, 2, 3, 4, 5] produces [5, 4, 3, 2, 1]."""
    ll = LinkedList[int]()
    for i in range(1, 6):
        ll.append(i)
    ll.reverse()
    assert ll.to_list() == [5, 4, 3, 2, 1]


def test_reverse_is_in_place():
    """reverse() does not change the number of nodes (len unchanged)."""
    ll = LinkedList[int]()
    for i in range(10):
        ll.append(i)
    original_len = len(ll)
    ll.reverse()
    # Verify in-place by checking head pointer changed
    assert len(ll) == original_len


def test_reverse_twice():
    """Reversing twice returns to the original order."""
    ll = LinkedList[int]()
    for i in range(1, 6):
        ll.append(i)
    original = ll.to_list()
    ll.reverse()
    ll.reverse()
    assert ll.to_list() == original


def test_reverse_preserves_tail_append():
    """After reverse(), append() still works correctly at the new tail."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.reverse()  # [3, 2, 1]
    ll.append(4)  # should append at tail → [3, 2, 1, 4]
    assert ll.to_list() == [3, 2, 1, 4]
    assert len(ll) == 4


def test_reverse_preserves_head_prepend():
    """After reverse(), prepend() still works correctly at the new head."""
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.reverse()  # [3, 2, 1]
    ll.prepend(99)  # should prepend at head → [99, 3, 2, 1]
    assert ll.to_list() == [99, 3, 2, 1]
    assert len(ll) == 4
