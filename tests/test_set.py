import pytest
from src.set import Set


class TestSetAdd:
    """Tests for the add method of the Set class."""

    def test_add_single_element(self):
        s = Set()
        s.add(1)
        assert s.contains(1) is True
        assert s.size() == 1

    def test_add_multiple_elements(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)
        assert s.contains(1) is True
        assert s.contains(2) is True
        assert s.contains(3) is True
        assert s.size() == 3

    def test_add_duplicate_elements(self):
        s = Set()
        s.add(1)
        s.add(1)
        assert s.size() == 1
        assert s.contains(1) is True

    def test_add_mixed_duplicates(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.add(1)
        s.add(3)
        s.add(2)
        assert s.size() == 3
        assert s.contains(1) is True
        assert s.contains(2) is True
        assert s.contains(3) is True


class TestSetRemove:
    """Tests for the remove method of the Set class."""

    def test_remove_existing_element(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.remove(1)
        assert s.contains(1) is False
        assert s.size() == 1
        assert s.contains(2) is True

    def test_remove_nonexistent_element_raises(self):
        s = Set()
        with pytest.raises(KeyError):
            s.remove(1)

    def test_remove_duplicate_removal(self):
        s = Set()
        s.add(1)
        s.remove(1)
        assert s.contains(1) is False
        assert s.size() == 0
        with pytest.raises(KeyError):
            s.remove(1)

    def test_remove_all_elements(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)
        s.remove(1)
        s.remove(2)
        s.remove(3)
        assert s.size() == 0


class TestSetContains:
    """Tests for the contains method of the Set class."""

    def test_contains_present_element(self):
        s = Set()
        s.add(42)
        assert s.contains(42) is True

    def test_contains_absent_element(self):
        s = Set()
        s.add(1)
        assert s.contains(2) is False

    def test_contains_after_removal(self):
        s = Set()
        s.add(1)
        s.remove(1)
        assert s.contains(1) is False

    def test_contains_empty_set(self):
        s = Set()
        assert s.contains(1) is False


class TestSetSize:
    """Tests for the size method of the Set class."""

    def test_size_empty_set(self):
        s = Set()
        assert s.size() == 0

    def test_size_after_adds(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)
        assert s.size() == 3

    def test_size_after_removes(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)
        s.remove(2)
        assert s.size() == 2

    def test_size_with_duplicates(self):
        s = Set()
        s.add(1)
        s.add(1)
        s.add(2)
        assert s.size() == 2

    def test_size_after_clear_all(self):
        s = Set()
        s.add(1)
        s.add(2)
        s.remove(1)
        s.remove(2)
        assert s.size() == 0


class TestSetUnion:
    """Tests for the union method of the Set class."""

    def test_union_overlapping_sets(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s1.add(3)
        s2 = Set()
        s2.add(3)
        s2.add(4)
        s2.add(5)
        result = s1.union(s2)
        assert result.contains(1) is True
        assert result.contains(2) is True
        assert result.contains(3) is True
        assert result.contains(4) is True
        assert result.contains(5) is True
        assert result.size() == 5

    def test_union_disjoint_sets(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s2 = Set()
        s2.add(3)
        s2.add(4)
        result = s1.union(s2)
        assert result.contains(1) is True
        assert result.contains(2) is True
        assert result.contains(3) is True
        assert result.contains(4) is True
        assert result.size() == 4

    def test_union_with_empty_set(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        empty = Set()
        result = s1.union(empty)
        assert result.contains(1) is True
        assert result.contains(2) is True
        assert result.size() == 2

    def test_union_empty_with_nonempty(self):
        s1 = Set()
        s2 = Set()
        s2.add(1)
        s2.add(2)
        result = s1.union(s2)
        assert result.contains(1) is True
        assert result.contains(2) is True
        assert result.size() == 2

    def test_union_both_empty(self):
        s1 = Set()
        s2 = Set()
        result = s1.union(s2)
        assert result.size() == 0

    def test_union_does_not_mutate_originals(self):
        s1 = Set()
        s1.add(1)
        s2 = Set()
        s2.add(2)
        s1.union(s2)
        assert s1.size() == 1
        assert s1.contains(1) is True
        assert s2.size() == 1
        assert s2.contains(2) is True


class TestSetIntersection:
    """Tests for the intersection method of the Set class."""

    def test_intersection_overlapping_sets(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s1.add(3)
        s2 = Set()
        s2.add(2)
        s2.add(3)
        s2.add(4)
        result = s1.intersection(s2)
        assert result.contains(2) is True
        assert result.contains(3) is True
        assert result.size() == 2

    def test_intersection_disjoint_sets(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s2 = Set()
        s2.add(3)
        s2.add(4)
        result = s1.intersection(s2)
        assert result.size() == 0

    def test_intersection_with_empty_set(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        empty = Set()
        result = s1.intersection(empty)
        assert result.size() == 0

    def test_intersection_empty_with_nonempty(self):
        s1 = Set()
        s2 = Set()
        s2.add(1)
        s2.add(2)
        result = s1.intersection(s2)
        assert result.size() == 0

    def test_intersection_both_empty(self):
        s1 = Set()
        s2 = Set()
        result = s1.intersection(s2)
        assert result.size() == 0

    def test_intersection_identical_sets(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s1.add(3)
        s2 = Set()
        s2.add(1)
        s2.add(2)
        s2.add(3)
        result = s1.intersection(s2)
        assert result.contains(1) is True
        assert result.contains(2) is True
        assert result.contains(3) is True
        assert result.size() == 3

    def test_intersection_does_not_mutate_originals(self):
        s1 = Set()
        s1.add(1)
        s1.add(2)
        s2 = Set()
        s2.add(2)
        s2.add(3)
        s1.intersection(s2)
        assert s1.size() == 2
        assert s1.contains(1) is True
        assert s2.size() == 2
        assert s2.contains(3) is True
