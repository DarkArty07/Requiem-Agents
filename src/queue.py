from typing import Any


class Queue:
    class _Node:
        def __init__(self, value: Any, next=None):
            self.value = value
            self.next = next

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def enqueue(self, item: Any) -> None:
        new_node = self._Node(item)
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def dequeue(self) -> Any:
        if self.is_empty():
            raise IndexError('dequeue from empty queue')
        node = self.head
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return node.value

    def front(self) -> Any:
        if self.is_empty():
            raise IndexError('front from empty queue')
        return self.head.value

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size
