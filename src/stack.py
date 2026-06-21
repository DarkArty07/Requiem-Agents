"""
A stack implementation using a singly linked list.

This module provides a Stack class that implements a last-in-first-out (LIFO)
data structure using a singly linked list built from scratch. No Python built-in
list or collections.deque methods are used to trivialize the implementation.
"""


class _Node:
    """A node in a singly linked list.

    Attributes:
        item: The data stored in the node.
        next: Reference to the next node in the list, or None if this is the tail.
    """

    __slots__ = ("item", "next")

    def __init__(self, item, next_node=None):
        self.item = item
        self.next = next_node


class Stack:
    """A last-in-first-out (LIFO) stack implemented with a singly linked list.

    Supports typical stack operations: push, pop, peek, is_empty, and size.

    Examples:
        >>> s = Stack()
        >>> s.is_empty()
        True
        >>> s.push(10)
        >>> s.push(20)
        >>> s.pop()
        20
        >>> s.peek()
        10
        >>> s.size()
        1
    """

    def __init__(self):
        """Initialize an empty stack."""
        self._top = None   # top of the stack (head of the linked list)
        self._size = 0     # number of items in the stack

    def push(self, item):
        """Add an item to the top of the stack.

        Args:
            item: The item to be placed onto the stack.
        """
        new_node = _Node(item, self._top)
        self._top = new_node
        self._size += 1

    def pop(self):
        """Remove and return the top item of the stack.

        Returns:
            The item that was at the top of the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if self._top is None:
            raise IndexError("pop from an empty stack")
        item = self._top.item
        self._top = self._top.next
        self._size -= 1
        return item

    def peek(self):
        """Return the top item of the stack without removing it.

        Returns:
            The item at the top of the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if self._top is None:
            raise IndexError("peek from an empty stack")
        return self._top.item

    def is_empty(self):
        """Check whether the stack is empty.

        Returns:
            True if the stack contains no items, False otherwise.
        """
        return self._top is None

    def size(self):
        """Return the number of items currently in the stack.

        Returns:
            The total count of items in the stack.
        """
        return self._size

    def __bool__(self):
        """Return False if the stack is empty, True otherwise.

        Allows intuitive truthiness checks: ``if stack:`` behaves as expected.
        """
        return not self.is_empty()

    def __len__(self):
        """Return the number of items in the stack.

        Allows use of the built-in ``len()`` function on a Stack instance.
        """
        return self._size

    def __repr__(self):
        """Return a string representation of the stack."""
        items = []
        current = self._top
        while current is not None:
            items.append(repr(current.item))
            current = current.next
        return f"Stack({', '.join(items) if items else ''})"
