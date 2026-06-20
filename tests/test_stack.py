'''Tests for Stack — src/stack.py.'''

import inspect

import pytest
from src.stack import Stack


# ── Empty stack ───────────────────────────────────────────────────────────────

def test_is_empty_true():
    '''Verify a new stack reports empty.'''
    s = Stack[int]()
    assert s.is_empty() is True


def test_size_zero():
    '''Size of a new stack is 0.'''
    s = Stack[int]()
    assert s.size() == 0


def test_pop_empty_raises():
    '''Pop from an empty stack raises IndexError.'''
    s = Stack[int]()
    with pytest.raises(IndexError, match='Stack is empty'):
        s.pop()


def test_peek_empty_raises():
    '''Peek at an empty stack raises IndexError.'''
    s = Stack[int]()
    with pytest.raises(IndexError, match='Stack is empty'):
        s.peek()


def test_iteration_empty_stack():
    '''Iterating an empty stack yields nothing.'''
    s = Stack[int]()
    assert list(s) == []


def test_repr_empty():
    '''repr of empty stack is Stack([]).'''
    s = Stack[int]()
    assert repr(s) == 'Stack([])'


# ── Single element ────────────────────────────────────────────────────────────

def test_push_single():
    '''Push one item updates size and peek.'''
    s = Stack[int]()
    s.push(42)
    assert s.size() == 1
    assert s.peek() == 42


def test_is_empty_false():
    '''Non-empty stack reports not empty.'''
    s = Stack[int]()
    s.push(1)
    assert s.is_empty() is False


# ── Multiple elements ─────────────────────────────────────────────────────────

def test_push_multiple():
    '''Push 1,2,3 yields size 3 and peek 3.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.size() == 3
    assert s.peek() == 3


def test_pop_returns_top():
    '''Pop returns the most recently pushed element.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.pop() == 3


def test_pop_removes_element():
    '''After pop, size decreases.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    s.pop()
    assert s.size() == 2


def test_peek_returns_top():
    '''Peek returns top item without removing it.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.peek() == 3
    assert s.size() == 3


def test_is_empty_after_pop_all():
    '''Stack becomes empty after popping all elements.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    s.pop()
    s.pop()
    s.pop()
    assert s.is_empty() is True


def test_size_after_operations():
    '''Mixed operations produce correct size.'''
    s = Stack[int]()
    s.push(5)
    s.push(10)
    s.pop()
    s.push(3)
    assert s.size() == 2


def test_iteration_yields_lifo_order():
    '''Iteration yields items in LIFO order.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    result = [item for item in s]
    assert result == [3, 2, 1]


def test_iteration_uses_yield():
    '''The __iter__ method returns a generator.'''
    s = Stack[int]()
    s.push(1)
    it = iter(s)
    assert inspect.isgenerator(it) is True


def test_repr_nonempty():
    '''repr of non-empty stack shows top-to-bottom order.'''
    s = Stack[int]()
    s.push(1)
    s.push(2)
    s.push(3)
    assert repr(s) == 'Stack([3, 2, 1])'


def test_string_type():
    '''Stack works with str type.'''
    s = Stack[str]()
    s.push('hello')
    assert s.pop() == 'hello'


def test_large_stack():
    '''Push 1000 items, verify size and iteration order.'''
    s = Stack[int]()
    for i in range(1000):
        s.push(i)
    assert s.size() == 1000
    items = [x for x in s]
    assert items[0] == 999
