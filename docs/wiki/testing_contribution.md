# How to add tests

## Create testing class

This class should inherit from `TestCase` class in unittests.

```python
from unittests import TestCase

class MyTests(TestCase):
    pass
```

## Use fixtures

`TestCase` class has 4 fixtures are frequently used.

### 1- setUpClass

It is class method and running once before all tests.

```python
@classmethod
def setUpClass(cls):
    pass
```

### 2- tearDownClass

It is class method and running once after all tests.

```python
@classmethod
def tearDownClass(cls):
    pass
```

### 3- setUp

It is member method and running before each test.

```python
def setUp(self):
    pass
```

### 4- tearDown

It is member method and running after each test.

```python
def tearDown(self):
    pass
```

## Write a test

### Test name

It should start with `test` followed by test ID, then test name.

### Test description

It should be in the docstring after the test method definition.

### Test scenario

It should be also in the docstring and has the steps for this test.

### Test code

It is should contain the logic of the test.

## Example

1- We have an add method in a module `myadd.py`.

```python
def add_two_numbers(a, b):
    return a + b
```

2- Write the test.

```python
from myadd import add_two_numbers
from unittests import TestCase

class AddTest(TestCase):
    def test01_test_add(self):
        """Test case for adding two numbers.

        **Test Scenario**

        - Add two numbers.
        - Check that the result is the adding of these two numbers.
        """
        # Add two numbers.
        x = 5
        y = 8
        z = add_two_numbers(x, y)

        # Check that the result is the adding of these two numbers.
        self.assertEqual(z, 13)
```

## How to run

We are using [pytest markers](https://docs.pytest.org/en/stable/example/markers.html) to classify the tests to two main categories (unittests, integration)

### Unittests only

```bash
pytest -sv -m "unittests" /path/to/tests
```

### Integration tests only

```bash
pytest -sv -m "integration" /path/to/tests
```

### All tests

```bash
pytest -sv /path/to/tests
```

### Single file

```bash
pytest -sv /path/to/file.py
```

### Single test

```bash
pytest -sv /path/to/file.py::ClassName::method_name
```

## Generate tests docs

In jsng shell.

```python
j.sals.testdocs.generate_tests_docs(source="~/js-ng/tests/", target="~/js-ng/docs/tests")
```

## Important Notes

1- Instead of using comments in the test code, logs can be used for better tracking to the test steps.

2- Also [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html) can be used instead of unittests one.
