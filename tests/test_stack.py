"""Tests for Stack class."""
import pytest
import sys
sys.path.insert(0, '/home/prometeo/Requiem')

from src.stack import Stack

# 1. push adds items and increases size
def test_push_increases_size():
    s = Stack()
    assert s.size() == 0
    s.push(1)
    assert s.size() == 1
    s.push(2)
    assert s.size() == 2

# 2. pop removes and returns the top item in LIFO order
def test_pop_returns_last_pushed():
    s = Stack()
    s.push(10)
    s.push(20)
    s.push(30)
    assert s.pop() == 30
    assert s.pop() == 20
    assert s.pop() == 10

# 3. pop on empty stack raises exception
def test_pop_on_empty_raises_exception():
    s = Stack()
    with pytest.raises(IndexError, match="pop from an empty stack"):
        s.pop()

# 4. peek returns top item without removing it
def test_peek_returns_top_without_removing():
    s = Stack()
    s.push('a')
    s.push('b')
    assert s.peek() == 'b'
    assert s.size() == 2

# 5. peek on empty stack raises exception
def test_peek_on_empty_raises_exception():
    s = Stack()
    with pytest.raises(IndexError, match="peek from an empty stack"):
        s.peek()

# 6. is_empty returns True for new stack and False after push
def test_is_empty():
    s = Stack()
    assert s.is_empty() is True
    s.push(1)
    assert s.is_empty() is False
    s.pop()
    assert s.is_empty() is True

# 7. size returns correct count after multiple operations
def test_size_after_multiple_operations():
    s = Stack()
    assert s.size() == 0
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.size() == 3
    s.pop()
    assert s.size() == 2
    s.push(4)
    assert s.size() == 3
    s.pop()
    s.pop()
    assert s.size() == 1
    s.pop()
    assert s.size() == 0

# 8. interleaved push/pop sequences
def test_interleaved_push_pop():
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 1
    assert s.is_empty()

# 9. pushing None or falsy values
def test_push_none():
    s = Stack()
    s.push(None)
    assert s.size() == 1
    assert s.pop() is None

def test_push_falsy_values():
    s = Stack()
    s.push(0)
    s.push(False)
    s.push('')
    assert s.pop() == ''
    assert s.pop() is False
    assert s.pop() == 0

# 10. large number of elements (e.g., 1000)
def test_large_number_of_elements():
    s = Stack()
    n = 1000
    for i in range(n):
        s.push(i)
    assert s.size() == n
    for i in range(n-1, -1, -1):
        assert s.pop() == i
    assert s.is_empty()