# Pytest Structured Report

## (1) Final Summary Line

```
1 failed, 178 passed in 0.45s
```

## (2) Failed Tests

### `tests/test_lru_cache.py::TestStress::test_stress_eviction_order`

Last 5 lines of traceback/error message:
```
E           assert None == 0
E            +  where None = get(0)
E            +    where get = <src.lru_cache.LRUCache object at 0x7003182d7fd0>.get

tests/test_lru_cache.py:396: AssertionError
```

## (3) Test Result Counts

| Status  | Count |
|---------|-------|
| Passed  | 178   |
| Failed  | 1     |
| Errors  | 0     |

---

**Note:** There is 1 failed test. No error tests detected.
