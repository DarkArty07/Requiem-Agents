from src.calculator import Calculator

assert Calculator.add(2, 3) == 5
assert Calculator.subtract(5, 2) == 3
assert Calculator.multiply(4, 3) == 12
assert Calculator.divide(10, 2) == 5.0

try:
    Calculator.divide(1, 0)
    assert False, "Should have raised"
except ZeroDivisionError as e:
    assert str(e) == 'Cannot divide by zero'

# Verify they are static methods
import inspect
assert isinstance(inspect.getattr_static(Calculator, 'add'), staticmethod)
assert isinstance(inspect.getattr_static(Calculator, 'subtract'), staticmethod)
assert isinstance(inspect.getattr_static(Calculator, 'multiply'), staticmethod)
assert isinstance(inspect.getattr_static(Calculator, 'divide'), staticmethod)

print('All assertions passed.')
