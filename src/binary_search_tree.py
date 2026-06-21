from typing import Optional, List


class BinarySearchTree:
    """A binary search tree implementation."""

    class _Node:
        """Internal node class for the BST."""

        def __init__(self, value: int) -> None:
            self.value: int = value
            self.left: Optional["BinarySearchTree._Node"] = None
            self.right: Optional["BinarySearchTree._Node"] = None

    def __init__(self) -> None:
        self.root: Optional["BinarySearchTree._Node"] = None

    def insert(self, value: int) -> None:
        """Insert a value into the BST. Duplicates are ignored."""
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional["_Node"], value: int) -> "_Node":
        if node is None:
            return BinarySearchTree._Node(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        # If equal, do nothing (ignore duplicate)
        return node

    def search(self, value: int) -> bool:
        """Return True if the value exists in the BST, False otherwise."""
        return self._search(self.root, value)

    def _search(self, node: Optional["_Node"], value: int) -> bool:
        if node is None:
            return False
        if value == node.value:
            return True
        elif value < node.value:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)

    def delete(self, value: int) -> None:
        """Delete a value from the BST. No-op if not found."""
        self.root = self._delete(self.root, value)

    def _delete(self, node: Optional["_Node"], value: int) -> Optional["_Node"]:
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            # Node to delete found
            # Case 1: Leaf or one child (right missing)
            if node.left is None:
                return node.right
            # Case 2: One child (left missing)
            if node.right is None:
                return node.left
            # Case 3: Two children -> inorder successor (smallest in right subtree)
            successor = self._min_value_node(node.right)
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        return node

    def _min_value_node(self, node: "_Node") -> "_Node":
        """Find the node with the minimum value in the subtree rooted at node."""
        current = node
        while current.left is not None:
            current = current.left
        return current

    def inorder_traversal(self) -> List[int]:
        """Return a list of values in ascending order (left-root-right)."""
        result: List[int] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional["_Node"], result: List[int]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.value)
        self._inorder(node.right, result)
