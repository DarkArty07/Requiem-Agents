import pytest
from src.queue import Queue


def test_enqueue_dequeue_single():
    q = Queue()
    q.enqueue(42)
    assert q.dequeue() == 42


def test_fifo_order():
    q = Queue()
    items = ['a', 'b', 'c', 'd']
    for item in items:
        q.enqueue(item)
    for expected in items:
        assert q.dequeue() == expected


def test_front_returns_without_removing():
    q = Queue()
    q.enqueue('first')
    q.enqueue('second')
    front = q.front()
    assert front == 'first'
    assert q.size() == 2
    assert q.dequeue() == 'first'


def test_front_empty_raises_indexerror():
    q = Queue()
    with pytest.raises(IndexError, match='front from empty queue'):
        q.front()


def test_dequeue_empty_raises_indexerror():
    q = Queue()
    with pytest.raises(IndexError, match='dequeue from empty queue'):
        q.dequeue()


def test_is_empty():
    q = Queue()
    assert q.is_empty() is True
    q.enqueue('x')
    assert q.is_empty() is False
    q.dequeue()
    assert q.is_empty() is True


def test_size():
    q = Queue()
    assert q.size() == 0
    q.enqueue('a')
    assert q.size() == 1
    q.enqueue('b')
    assert q.size() == 2
    q.dequeue()
    assert q.size() == 1
    q.dequeue()
    assert q.size() == 0


def test_interleaved_enqueue_dequeue():
    q = Queue()
    q.enqueue('A')
    q.enqueue('B')
    assert q.dequeue() == 'A'
    q.enqueue('C')
    assert q.dequeue() == 'B'
    assert q.dequeue() == 'C'


def test_stress_1000_items():
    q = Queue()
    n = 1000
    for i in range(n):
        q.enqueue(i)
    for i in range(n):
        assert q.dequeue() == i
