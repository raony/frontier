# Evennia Testing Guide

## Overview
This guide covers how to write unit tests for Evennia projects, including the helper objects available and project-specific testing conventions.

## Test Organization Pattern
- **Location**: Tests should be close to the code they test
- **Structure**: Each package should have a `tests/` subpackage
- **Naming**: Test files should be named `test_*.py` (e.g., `test_commands.py`, `test_objects.py`)

## Running Tests

### Basic Commands
```bash
# From game directory, activate virtualenv first
source .venv/bin/activate

# Run all tests in current directory and subdirectories
evennia test --settings settings.py .

# Run specific test file
evennia test --settings settings.py tests.test_filename

# Run specific test class
evennia test --settings settings.py tests.test_filename.TestClassName

# Run specific test method
evennia test --settings settings.py tests.test_filename.TestClassName.test_method_name
```

### Important Notes
- Always use `--settings settings.py` to use your game settings
- NEVER use `-v` flag (it only shows framework version)
- Tests run against a temporary database

## Available Test Base Classes

### For Game Directory Testing

#### `EvenniaTest`
- **Use**: Full object environment for comprehensive testing
- **Provides**: Complete set of pre-created test objects
- **Available Objects**:
  - `.account` - TestAccount (linked to char1)
  - `.account2` - TestAccount2 (linked to char2)
  - `.char1` - Character "Char" with Developer permissions (not superuser)
  - `.char2` - Character "Char2" with base player permissions
  - `.obj1` - Regular Object "Obj"
  - `.obj2` - Regular Object "Obj2"
  - `.room1` - Room "Room" (contains both chars and objects), description "room_desc"
  - `.room2` - Empty Room "Room2" (no description)
  - `.exit` - Exit "out" from room1 to room2
  - `.script` - Inert Script "Script" (no timing)
  - `.session` - Fake Session (sessid=1, used by account1)

#### `EvenniaCommandTest`
- **Use**: Testing Evennia Commands specifically
- **Inherits**: All objects from `EvenniaTest`
- **Special Method**: `.call()` for command testing
- **Features**: Compare actual command output with expected results

#### `EvenniaTestCase`
- **Use**: Basic testing without pre-created objects
- **Equivalent**: Python's standard `TestCase`

### For Evennia Core Testing
- `BaseEvenniaTest` - Like `EvenniaTest` but enforces default Evennia settings
- `BaseEvenniaCommandTest` - Like `EvenniaCommandTest` but enforces default settings
- `BaseEvenniaTestCase` - Basic testing with enforced default settings

### Mixin Classes
- `EvenniaTestMixin` - Creates test environment objects
- `EvenniaCommandMixin` - Adds `.call()` command testing helper

## Test Writing Patterns

### Basic Test Structure
```python
import unittest
from evennia.utils.test_resources import EvenniaTest

class TestMyFeature(EvenniaTest):
    """Test suite for MyFeature functionality."""

    def setUp(self):
        """Run before each test method."""
        super().setUp()  # Important: call parent setUp
        # Your setup code here

    def tearDown(self):
        """Run after each test method."""
        # Your cleanup code here
        super().tearDown()  # Important: call parent tearDown

    def test_specific_behavior(self):
        """Test a specific behavior."""
        # Arrange
        expected_result = "expected value"

        # Act
        actual_result = self.char1.some_method()

        # Assert
        self.assertEqual(expected_result, actual_result)
```

### Command Testing Pattern
```python
from evennia.utils.test_resources import EvenniaCommandTest
from commands.my_commands import CmdMyCommand

class TestMyCommand(EvenniaCommandTest):
    """Test suite for MyCommand."""

    def test_command_basic_usage(self):
        """Test basic command functionality."""
        self.call(
            CmdMyCommand(),
            "target_argument",
            "Expected output text"
        )

    def test_command_with_multiple_outputs(self):
        """Test command that sends multiple messages."""
        self.call(
            CmdMyCommand(),
            "argument",
            "First message||Second message"  # || separates multiple .msg() calls
        )

    def test_command_partial_match(self):
        """Test with partial expected output."""
        self.call(
            CmdMyCommand(),
            "arg",
            "Beginning of expected output"  # Partial match is sufficient
        )
```

### Object Testing Pattern
```python
from evennia.utils.test_resources import EvenniaTest
from evennia import create_object

class TestMyObject(EvenniaTest):
    """Test suite for custom objects."""

    def test_object_creation(self):
        """Test object creation and initialization."""
        obj = create_object("typeclasses.objects.MyObject", key="TestObj")
        self.assertIsNotNone(obj)
        self.assertEqual(obj.key, "TestObj")

        # Cleanup
        obj.delete()

    def test_object_interaction(self):
        """Test interaction between objects."""
        # Use pre-created objects from EvenniaTest
        result = self.char1.search(self.obj1.key)
        self.assertEqual(result, self.obj1)

    def test_object_location(self):
        """Test location-based functionality."""
        # char1 and obj1 are both in room1 by default
        self.assertEqual(self.char1.location, self.room1)
        self.assertEqual(self.obj1.location, self.room1)
```

## Directory Structure Examples

```
world/
├── physical/
│   ├── __init__.py
│   ├── container.py
│   ├── weight.py
│   └── tests/
│       ├── __init__.py
│       ├── test_container.py
│       └── test_weight.py
├── living/
│   ├── __init__.py
│   ├── metabolism.py
│   ├── people.py
│   └── tests/
│       ├── __init__.py
│       ├── test_metabolism.py
│       └── test_people.py
└── commands/
    ├── __init__.py
    ├── examine.py
    ├── forage.py
    └── tests/
        ├── __init__.py
        ├── test_examine.py
        └── test_forage.py
```

## Common Assert Methods
- `assertEqual(a, b)` - Check if a equals b
- `assertNotEqual(a, b)` - Check if a does not equal b
- `assertTrue(x)` - Check if x is True
- `assertFalse(x)` - Check if x is False
- `assertIsNone(x)` - Check if x is None
- `assertIsNotNone(x)` - Check if x is not None
- `assertIn(a, b)` - Check if a is in b
- `assertNotIn(a, b)` - Check if a is not in b
- `assertRaises(exception, callable, *args)` - Check if callable raises exception

## Best Practices

### Test Organization
1. One test file per module being tested
2. Group related tests in test classes
3. Use descriptive test method names
4. Keep tests focused on single behaviors

### Test Data
1. Use pre-created objects from `EvenniaTest` when possible
2. Create minimal test data for specific needs
3. Clean up created objects in `tearDown` if needed
4. Avoid dependencies between test methods

### Command Testing
1. Test both success and failure cases
2. Test edge cases and invalid inputs
3. Use `.call()` method for command testing
4. Test permissions and access control

### Performance
1. Use `--nomigrations` for faster test runs (requires django-test-without-migrations)
2. Focus tests on business logic, not framework features
3. Mock external dependencies when appropriate

## Examples from Documentation

### Basic Object Test
```python
from evennia.utils.test_resources import EvenniaTest

class TestObject(EvenniaTest):
    def test_object_search_character(self):
        """Check that char1 can search for char2 by name"""
        self.assertEqual(self.char1.search(self.char2.key), self.char2)

    def test_location_search(self):
        """Check so that char1 can find the current location by name"""
        self.assertEqual(self.char1.search(self.char1.location.key), self.char1.location)
```

### Command Test Example
```python
from evennia.utils.test_resources import EvenniaCommandTest
from commands import command as mycommand

class TestSet(EvenniaCommandTest):
    def test_mycmd_char(self):
        """Tests the look command by simple call, using Char2 as a target"""
        self.call(mycommand.CmdMyLook(), "Char2", "Char2(#7)")

    def test_mycmd_room(self):
        """Tests the look command by simple call, with target as room"""
        self.call(mycommand.CmdMyLook(), "Room",
                  "Room(#1)\nroom_desc\nExits: out(#3)\n"
                  "You see: Obj(#4), Obj2(#5), Char2(#7)")
```

## Quick Reference

### Test File Template
```python
"""
Tests for [module_name].
"""
import unittest
from evennia.utils.test_resources import EvenniaTest, EvenniaCommandTest
from evennia import create_object

class Test[ClassName](EvenniaTest):
    """Test suite for [ClassName]."""

    def setUp(self):
        super().setUp()
        # Additional setup

    def test_[specific_behavior](self):
        """Test [specific behavior]."""
        # Test implementation
        pass
```

### Running Tests Quickly
```bash
# Setup
source .venv/bin/activate

# Run all tests
evennia test --settings settings.py .

# Run specific package
evennia test --settings settings.py world.physical.tests

# Run with faster execution (no migrations)
evennia test --settings settings.py --nomigrations .
```
