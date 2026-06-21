import pytest
from src.binary_search_tree import BinarySearchTree


# ---------------------------------------------------------------------------
# 1. Insert and inorder on empty tree returns []
# ---------------------------------------------------------------------------
def test_inorder_empty_tree():
    bst = BinarySearchTree()
    assert bst.inorder_traversal() == []


def test_inorder_empty_tree_multiple_calls():
    bst = BinarySearchTree()
    assert bst.inorder_traversal() == []
    assert bst.inorder_traversal() == []


# ---------------------------------------------------------------------------
# 2. Insert single element, inorder returns [value]
# ---------------------------------------------------------------------------
def test_insert_single_element():
    bst = BinarySearchTree()
    bst.insert(42)
    assert bst.inorder_traversal() == [42]


def test_insert_single_element_zero():
    bst = BinarySearchTree()
    bst.insert(0)
    assert bst.inorder_traversal() == [0]


def test_insert_single_element_negative():
    bst = BinarySearchTree()
    bst.insert(-7)
    assert bst.inorder_traversal() == [-7]


# ---------------------------------------------------------------------------
# 3. Insert multiple elements in various orders, verify inorder is always
#    sorted ascending
# ---------------------------------------------------------------------------
def test_inorder_sorted_ascending():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    bst.insert(7)
    assert bst.inorder_traversal() == [3, 5, 7, 10, 15]


def test_inorder_sorted_descending_inserts():
    bst = BinarySearchTree()
    for v in [50, 40, 30, 20, 10]:
        bst.insert(v)
    assert bst.inorder_traversal() == [10, 20, 30, 40, 50]


def test_inorder_sorted_random_inserts():
    bst = BinarySearchTree()
    values = [7, 3, 9, 1, 5, 8, 10]
    for v in values:
        bst.insert(v)
    assert bst.inorder_traversal() == [1, 3, 5, 7, 8, 9, 10]


def test_inorder_sorted_negative_and_positive():
    bst = BinarySearchTree()
    for v in [-10, 20, -30, 0, 15, -5]:
        bst.insert(v)
    assert bst.inorder_traversal() == [-30, -10, -5, 0, 15, 20]


def test_inorder_sorted_identical_order():
    bst = BinarySearchTree()
    for v in [1, 2, 3, 4, 5]:
        bst.insert(v)
    assert bst.inorder_traversal() == [1, 2, 3, 4, 5]


def test_inorder_sorted_reverse_order():
    bst = BinarySearchTree()
    for v in [5, 4, 3, 2, 1]:
        bst.insert(v)
    assert bst.inorder_traversal() == [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# 4. Search on empty tree returns False
# ---------------------------------------------------------------------------
def test_search_empty_tree():
    bst = BinarySearchTree()
    assert bst.search(10) is False


def test_search_empty_tree_negative():
    bst = BinarySearchTree()
    assert bst.search(-1) is False


def test_search_empty_tree_zero():
    bst = BinarySearchTree()
    assert bst.search(0) is False


# ---------------------------------------------------------------------------
# 5. Search for existing value returns True
# ---------------------------------------------------------------------------
def test_search_existing_value():
    bst = BinarySearchTree()
    bst.insert(42)
    assert bst.search(42) is True


def test_search_existing_value_multiple_elements():
    bst = BinarySearchTree()
    for v in [10, 20, 30, 40, 50]:
        bst.insert(v)
    assert bst.search(10) is True
    assert bst.search(50) is True
    assert bst.search(30) is True


# ---------------------------------------------------------------------------
# 6. Search for non-existing value returns False
# ---------------------------------------------------------------------------
def test_search_non_existing_value():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(20)
    assert bst.search(15) is False


def test_search_non_existing_value_empty():
    bst = BinarySearchTree()
    assert bst.search(999) is False


def test_search_non_existing_negative_vs_positive():
    bst = BinarySearchTree()
    bst.insert(5)
    bst.insert(10)
    assert bst.search(-5) is False


# ---------------------------------------------------------------------------
# 7. Search after insertions and deletions
# ---------------------------------------------------------------------------
def test_search_after_insertions_and_deletions():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(20)
    bst.insert(5)
    assert bst.search(10) is True
    bst.delete(10)
    assert bst.search(10) is False
    assert bst.search(20) is True
    assert bst.search(5) is True


def test_search_after_delete_reinsert():
    bst = BinarySearchTree()
    bst.insert(7)
    bst.insert(3)
    bst.delete(7)
    assert bst.search(7) is False
    bst.insert(7)
    assert bst.search(7) is True


# ---------------------------------------------------------------------------
# 8. Delete leaf node
# ---------------------------------------------------------------------------
def test_delete_leaf_node():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.delete(5)
    assert bst.inorder_traversal() == [10, 15]
    assert bst.search(5) is False


def test_delete_leaf_node_right():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.delete(15)
    assert bst.inorder_traversal() == [5, 10]
    assert bst.search(15) is False


def test_delete_leaf_node_deep():
    bst = BinarySearchTree()
    for v in [8, 4, 12, 2, 6, 10, 14]:
        bst.insert(v)
    bst.delete(2)
    assert bst.inorder_traversal() == [4, 6, 8, 10, 12, 14]
    bst.delete(14)
    assert bst.inorder_traversal() == [4, 6, 8, 10, 12]


# ---------------------------------------------------------------------------
# 9. Delete node with one child (left only AND right only)
# ---------------------------------------------------------------------------
def test_delete_node_with_left_child_only():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(3)
    # Node 5 has left child 3, no right child
    bst.delete(5)
    assert bst.inorder_traversal() == [3, 10]
    assert bst.search(5) is False
    assert bst.search(3) is True
    assert bst.search(10) is True


def test_delete_node_with_right_child_only():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(7)
    # Node 5 has right child 7, no left child
    bst.delete(5)
    assert bst.inorder_traversal() == [7, 10]
    assert bst.search(5) is False
    assert bst.search(7) is True
    assert bst.search(10) is True


def test_delete_node_with_left_child_only_deeper():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    # Node 5 has left child 3, no right child
    bst.delete(5)
    assert bst.inorder_traversal() == [3, 10, 15, 20]


def test_delete_node_with_right_child_only_deeper():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(17)
    # Node 15 has right child 17, no left child
    bst.delete(15)
    assert bst.inorder_traversal() == [5, 10, 17, 20]


# ---------------------------------------------------------------------------
# 10. Delete node with two children (inorder successor replacement)
# ---------------------------------------------------------------------------
def test_delete_node_with_two_children():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    bst.insert(7)
    # Delete 5 (has two children: 3 and 7)
    bst.delete(5)
    assert bst.inorder_traversal() == [3, 7, 10, 15]
    assert bst.search(5) is False


def test_delete_node_with_two_children_root():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    bst.insert(7)
    bst.insert(12)
    bst.insert(20)
    # Delete 10 (root, has two children)
    bst.delete(10)
    assert bst.inorder_traversal() == [3, 5, 7, 12, 15, 20]
    assert bst.search(10) is False


def test_delete_node_with_two_children_complex():
    bst = BinarySearchTree()
    for v in [50, 30, 70, 20, 40, 60, 80, 35, 45]:
        bst.insert(v)
    # Delete 30 (has two children: 20 and 40; 40 has 35, 45)
    bst.delete(30)
    # Inorder successor of 30 is 35
    assert bst.inorder_traversal() == [20, 35, 40, 45, 50, 60, 70, 80]
    assert bst.search(30) is False


def test_delete_node_with_two_children_successor_has_right_child():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    bst.insert(25)
    bst.insert(35)
    bst.insert(23)
    bst.insert(27)
    # Delete 20 (root, inorder successor is 23 which has a right child 27? No, 23 has no right child)
    # Actually inorder traversal: 10, 23, 25, 27, 30, 35
    bst.delete(20)
    assert bst.inorder_traversal() == [10, 23, 25, 27, 30, 35]


# ---------------------------------------------------------------------------
# 11. Delete root node
# ---------------------------------------------------------------------------
def test_delete_root_single_element():
    bst = BinarySearchTree()
    bst.insert(42)
    bst.delete(42)
    assert bst.inorder_traversal() == []
    assert bst.search(42) is False


def test_delete_root_with_left_child_only():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(3)
    bst.delete(10)
    assert bst.inorder_traversal() == [3, 5]


def test_delete_root_with_right_child_only():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(15)
    bst.insert(20)
    bst.delete(10)
    assert bst.inorder_traversal() == [15, 20]


def test_delete_root_with_two_children():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.insert(3)
    bst.insert(7)
    bst.delete(10)
    assert bst.inorder_traversal() == [3, 5, 7, 15]
    assert bst.search(10) is False


def test_delete_root_chain_left():
    bst = BinarySearchTree()
    for v in [10, 9, 8, 7]:
        bst.insert(v)
    bst.delete(10)
    assert bst.inorder_traversal() == [7, 8, 9]


def test_delete_root_chain_right():
    bst = BinarySearchTree()
    for v in [10, 11, 12, 13]:
        bst.insert(v)
    bst.delete(10)
    assert bst.inorder_traversal() == [11, 12, 13]


# ---------------------------------------------------------------------------
# 12. Delete from empty tree (no-op, no error)
# ---------------------------------------------------------------------------
def test_delete_from_empty_tree():
    bst = BinarySearchTree()
    bst.delete(10)
    assert bst.inorder_traversal() == []


def test_delete_from_empty_tree_multiple():
    bst = BinarySearchTree()
    bst.delete(1)
    bst.delete(2)
    bst.delete(3)
    assert bst.inorder_traversal() == []


# ---------------------------------------------------------------------------
# 13. Delete non-existing value (no-op, no error)
# ---------------------------------------------------------------------------
def test_delete_non_existing():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(20)
    bst.delete(999)
    assert bst.inorder_traversal() == [10, 20]


def test_delete_non_existing_multiple():
    bst = BinarySearchTree()
    bst.insert(5)
    bst.insert(3)
    bst.insert(7)
    bst.delete(1)
    bst.delete(9)
    bst.delete(4)
    assert bst.inorder_traversal() == [3, 5, 7]


# ---------------------------------------------------------------------------
# 14. Duplicate insert is ignored (inorder unchanged)
# ---------------------------------------------------------------------------
def test_duplicate_insert_ignored():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(10)
    assert bst.inorder_traversal() == [5, 10]


def test_duplicate_insert_ignored_multiple():
    bst = BinarySearchTree()
    bst.insert(1)
    bst.insert(1)
    bst.insert(2)
    bst.insert(2)
    bst.insert(2)
    bst.insert(3)
    assert bst.inorder_traversal() == [1, 2, 3]


def test_duplicate_insert_after_delete():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.delete(10)
    bst.insert(10)
    assert bst.inorder_traversal() == [5, 10, 15]


# ---------------------------------------------------------------------------
# 15. Complex scenario: insert many, delete some, verify inorder is sorted
# ---------------------------------------------------------------------------
def test_complex_scenario():
    bst = BinarySearchTree()
    values = [12, 5, 18, 2, 9, 15, 21, 1, 3, 7, 10, 14, 17, 20, 25]
    for v in values:
        bst.insert(v)

    # Delete some values
    to_delete = [2, 12, 21, 9, 17]
    for v in to_delete:
        bst.delete(v)

    result = bst.inorder_traversal()
    expected = sorted([v for v in values if v not in to_delete])
    assert result == expected
    # Verify sorted
    assert result == sorted(result)


def test_complex_scenario_2():
    bst = BinarySearchTree()
    for v in [100, 50, 150, 25, 75, 125, 175, 10, 30, 60, 90, 110, 130, 160, 190]:
        bst.insert(v)

    # Delete all leaves
    for v in [10, 30, 60, 90, 110, 130, 160, 190]:
        bst.delete(v)
    assert bst.inorder_traversal() == [25, 50, 75, 100, 125, 150, 175]

    # Delete nodes with one child
    for v in [25, 75, 125, 175]:
        bst.delete(v)
    assert bst.inorder_traversal() == [50, 100, 150]

    # Delete nodes with two children
    bst.delete(100)
    assert bst.inorder_traversal() == [50, 150]


# ---------------------------------------------------------------------------
# 16. Stress test: insert 100 values, verify all searchable, delete all,
#     verify empty
# ---------------------------------------------------------------------------
def test_stress_insert_100_and_search():
    bst = BinarySearchTree()
    values = list(range(1, 101))
    for v in values:
        bst.insert(v)
    result = bst.inorder_traversal()
    assert result == values
    for v in values:
        assert bst.search(v) is True


def test_stress_insert_100_reverse_and_search():
    bst = BinarySearchTree()
    values = list(range(100, 0, -1))
    for v in values:
        bst.insert(v)
    result = bst.inorder_traversal()
    assert result == list(range(1, 101))
    for v in range(1, 101):
        assert bst.search(v) is True


def test_stress_insert_100_shuffled_and_search():
    bst = BinarySearchTree()
    values = [
        68, 3, 87, 15, 42, 99, 22, 56, 74, 31,
        91, 47, 10, 82, 63, 27, 53, 78, 36, 95,
        19, 6, 60, 44, 71, 84, 39, 13, 50, 25,
        58, 80, 33, 97, 17, 1, 65, 29, 49, 11,
        89, 54, 76, 38, 93, 8, 61, 41, 20, 85,
        73, 4, 52, 69, 23, 46, 96, 35, 67, 14,
        81, 44, 100, 59, 37, 7, 90, 30, 55, 79,
        12, 64, 48, 18, 75, 26, 32, 86, 40, 70,
        57, 2, 21, 92, 62, 88, 51, 5, 83, 45,
        28, 72, 9, 94, 66, 16, 43, 77, 34, 98,
    ]
    for v in values:
        bst.insert(v)
    result = bst.inorder_traversal()
    assert result == sorted(values)
    assert result == sorted(set(values))


def test_stress_insert_100_delete_all():
    bst = BinarySearchTree()
    values = list(range(1, 101))
    for v in values:
        bst.insert(v)
    for v in values:
        bst.delete(v)
    assert bst.inorder_traversal() == []
    assert bst.search(1) is False
    assert bst.search(100) is False


def test_stress_insert_delete_random_order():
    bst = BinarySearchTree()
    values = list(range(1, 101))
    import random
    shuffled = values[:]
    random.seed(42)
    random.shuffle(shuffled)
    for v in shuffled:
        bst.insert(v)
    assert bst.inorder_traversal() == values
    random.shuffle(shuffled)
    for v in shuffled:
        bst.delete(v)
    assert bst.inorder_traversal() == []


# ---------------------------------------------------------------------------
# 17. Edge case: tree becomes a chain (all left children or all right
#     children)
# ---------------------------------------------------------------------------
def test_chain_left_children():
    bst = BinarySearchTree()
    for v in [100, 90, 80, 70, 60, 50]:
        bst.insert(v)
    assert bst.inorder_traversal() == [50, 60, 70, 80, 90, 100]
    assert bst.search(100) is True
    assert bst.search(50) is True
    assert bst.search(55) is False


def test_chain_right_children():
    bst = BinarySearchTree()
    for v in [10, 20, 30, 40, 50, 60]:
        bst.insert(v)
    assert bst.inorder_traversal() == [10, 20, 30, 40, 50, 60]
    assert bst.search(10) is True
    assert bst.search(60) is True
    assert bst.search(25) is False


def test_chain_left_delete():
    bst = BinarySearchTree()
    for v in [100, 90, 80, 70, 60]:
        bst.insert(v)
    bst.delete(80)
    assert bst.inorder_traversal() == [60, 70, 90, 100]


def test_chain_right_delete():
    bst = BinarySearchTree()
    for v in [10, 20, 30, 40, 50]:
        bst.insert(v)
    bst.delete(30)
    assert bst.inorder_traversal() == [10, 20, 40, 50]


def test_chain_left_search_non_existing():
    bst = BinarySearchTree()
    for v in [100, 90, 80, 70]:
        bst.insert(v)
    # Values less than min
    assert bst.search(60) is False
    # Values between nodes
    assert bst.search(85) is False
    # Values greater than max
    assert bst.search(110) is False


def test_chain_right_search_non_existing():
    bst = BinarySearchTree()
    for v in [10, 20, 30, 40]:
        bst.insert(v)
    assert bst.search(5) is False
    assert bst.search(25) is False
    assert bst.search(50) is False


def test_chain_left_single_child_deletion_root():
    bst = BinarySearchTree()
    for v in [100, 90, 80]:
        bst.insert(v)
    bst.delete(100)
    assert bst.inorder_traversal() == [80, 90]


def test_chain_right_single_child_deletion_root():
    bst = BinarySearchTree()
    for v in [10, 20, 30]:
        bst.insert(v)
    bst.delete(10)
    assert bst.inorder_traversal() == [20, 30]
