from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar('T')


class LinkedList(Generic[T]):
    """A singly-linked list implementation with O(1) append, prepend, and length.

    Attributes:
        _head: Reference to the first node, or None if the list is empty.
        _tail: Reference to the last node, or None if the list is empty.
        _size: Number of elements currently stored in the list.

    Examples:
        >>> ll = LinkedList[int]()
        >>> ll.append(1)
        >>> ll.append(2)
        >>> ll.prepend(0)
        >>> len(ll)
        3
        >>> list(ll)
        [0, 1, 2]
        >>> ll.remove(1)
        True
        >>> repr(ll)
        'LinkedList([0, 2])'
    """

    class _Node:
        """Internal node representing a single element in the linked list.

        Attributes:
            data: The payload stored in this node.
            next: Reference to the next node, or None if this node is the tail.
        """
        __slots__ = ('data', 'next')

        def __init__(self, data: T, next: Optional['LinkedList._Node'] = None) -> None:
            """Initialize a node with data and an optional next reference.

            Args:
                data: The payload stored in this node.
                next: Reference to the next node, or None if this is the tail.
            """
            self.data = data
            self.next = next

    def __init__(self) -> None:
        """Initialize an empty linked list.

        The head and tail are set to None and the size counter is set to 0.
        """
        self._head: Optional[LinkedList._Node] = None
        self._tail: Optional[LinkedList._Node] = None
        self._size: int = 0

    def append(self, data: T) -> None:
        """Add an element at the end of the list.

        Operates in O(1) time by making use of the tail reference.

        Args:
            data: The element to append.
        """
        new_node = LinkedList._Node(data)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def prepend(self, data: T) -> None:
        """Add an element at the beginning of the list.

        Operates in O(1) time.

        Args:
            data: The element to prepend.
        """
        new_node = LinkedList._Node(data, next=self._head)
        self._head = new_node
        if self._tail is None:
            self._tail = new_node
        self._size += 1

    def remove(self, data: T) -> bool:
        """Remove the first occurrence of a value from the list.

        Args:
            data: The value to remove.

        Returns:
            True if the value was found and removed, False if the value was not present.

        Raises:
            ValueError: If the list is empty.
        """
        if self._head is None:
            raise ValueError("Cannot remove from an empty list")

        prev: Optional[LinkedList._Node] = None
        current: Optional[LinkedList._Node] = self._head

        while current is not None:
            if current.data == data:
                # Remove the node
                if prev is None:
                    # Removing the head
                    self._head = current.next
                else:
                    prev.next = current.next

                if current is self._tail:
                    # Removing the tail
                    self._tail = prev

                self._size -= 1
                return True
            prev = current
            current = current.next

        return False

    def search(self, data: T) -> bool:
        """Check if a value exists in the list.

        Args:
            data: The value to search for.

        Returns:
            True if the value is present, False otherwise.
        """
        current = self._head
        while current is not None:
            if current.data == data:
                return True
            current = current.next
        return False

    def reverse(self) -> None:
        """Reverse the linked list in-place.

        Traverses the list once, reversing each node's next pointer, then
        swaps the head and tail references. Operates in O(n) time and O(1)
        space. If the list is empty or has a single element, returns early.

        Examples:
            >>> ll = LinkedList[int]()
            >>> ll.append(1); ll.append(2); ll.append(3)
            >>> ll.reverse()
            >>> ll.to_list()
            [3, 2, 1]
        """
        if self._head is None or self._head is self._tail:
            return

        old_head = self._head
        prev: Optional[LinkedList._Node] = None
        current: Optional[LinkedList._Node] = self._head

        while current is not None:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node

        self._tail = old_head
        self._head = prev

    def to_list(self) -> list[T]:
        """Convert the linked list to a Python list, preserving order.

        Returns:
            A list containing all elements in the order they appear in the linked list.
        """
        result: list[T] = []
        current = self._head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self) -> int:
        """Return the number of elements in the list.

        Returns:
            The current size of the list.
        """
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Iterate over the elements of the list.

        Yields:
            Each element in the list in order.
        """
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        """Return a string representation of the linked list.

        Returns:
            A string in the format `LinkedList([elem1, elem2, ...])`.
        """
        return f"LinkedList({self.to_list()})"
