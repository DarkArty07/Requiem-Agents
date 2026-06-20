from typing import Generic, TypeVar, Iterator

T = TypeVar('T')


class Stack(Generic[T]):
    """A generic stack (LIFO) data structure.

    Implements a last-in, first-out stack using a list as the underlying
    storage. Provides the standard stack operations with O(1) amortized
    time complexity for push and O(1) for pop and peek.

    Example:
        >>> s = Stack[int]()
        >>> s.push(1)
        >>> s.push(2)
        >>> s.pop()
        2
        >>> s.peek()
        1
        >>> s.is_empty()
        False
        >>> s.size()
        1
        >>> list(s)
        [1]
        >>> s
        Stack([1])
    """

    def __init__(self) -> None:
        """Initialize an empty stack."""
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push an item onto the top of the stack.

        Args:
            item: The item to be added to the stack.
        """
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item of the stack.

        Returns:
            The item at the top of the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError('Stack is empty')
        return self._items.pop()

    def peek(self) -> T:
        """Return the top item of the stack without removing it.

        Returns:
            The item at the top of the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError('Stack is empty')
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check if the stack is empty.

        Returns:
            True if the stack contains no items, False otherwise.
        """
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of items in the stack.

        Returns:
            The current size of the stack.
        """
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the stack from top to bottom (LIFO order).

        Yields:
            Items from the stack starting at the top (most recently pushed)
            and ending at the bottom.
        """
        for i in range(len(self._items) - 1, -1, -1):
            yield self._items[i]

    def __repr__(self) -> str:
        """Return a string representation of the stack showing top first.

        Returns:
            A string like `Stack([3, 2, 1])` where 3 is the top.
        """
        return f'Stack({list(self._items)[::-1]})'
