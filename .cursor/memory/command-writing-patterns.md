# Command Writing Patterns and Rules

This document defines the standard patterns and conventions for writing command classes in the Frontier codebase, based on established examples like `CmdFill` and `CmdEmpty`.

## Basic Command Structure

### Class Definition
```python
from commands.command import Command
from world.utils import DisplayNameWrapper

class CmdExample(Command):
    """Brief description of what the command does.

    Usage:
      example <arg1>=<arg2>
      example <arg1>

    Examples:
      example sword from stone
      example water=cup
    """

    key = "example"
    aliases = ["ex", "examp"]  # Optional
    locks = "cmd:all()"        # or "cmd:perm(Builder)" for admin commands

    def func(self):
        # Command implementation
        pass
```

### Required Command Attributes
- **`key`** - Primary command name
- **`locks`** - Permission string (usually `"cmd:all()"` or `"cmd:perm(Builder)"`)
- **Docstring** - Must include usage examples and brief description
- **`func()`** method - Contains the command logic

## Argument Parsing Patterns

### Standard Argument Access
```python
def func(self):
    caller = self.caller  # Always get caller first

    # For commands with = syntax: "command arg1=arg2"
    arg1_name = self.lhs   # Left-hand side (before =)
    arg2_name = self.rhs   # Right-hand side (after =)

    # For commands with raw args: "command some text here"
    raw_args = self.args   # Everything after command name
```

### Argument Validation Pattern
```python
# Required arguments validation
if not arg1_name or not arg2_name:
    return caller.msg("Usage: command <arg1>=<arg2>")

# Optional second argument pattern
if not arg1_name:
    return caller.msg("Usage: command <arg1>=<arg2> or command <arg1>")
```

## Object Search and Validation

### Standard Object Search Pattern
```python
# ALWAYS use caller.search_item() - this is the established pattern
obj = caller.search_item(obj_name)
if not obj:
    return caller.msg(f"You don't see {obj_name}.")

# NEVER use caller.search() with candidates - use search_item instead
# For optional objects (like destination)
if dest_name:
    dest = caller.search_item(dest_name)
    if not dest:
        return caller.msg(f"You don't see {dest_name}.")
else:
    dest = caller.location  # Default to current room
```

### Typeclass Validation Pattern
```python
# Check if object is the right type
if not obj.is_typeclass(RequiredClass, exact=False):
    return caller.msg(f"You can't use {self.get_display_name(obj)} that way.")

# Multiple valid types
if not (obj.is_typeclass(Type1, exact=False) or obj.is_typeclass(Type2, exact=False)):
    return caller.msg(f"You can't use {self.get_display_name(obj)} for this.")
```

### State Validation Pattern
```python
# Check object state before proceeding
if obj.is_full:
    return caller.msg(f"{self.get_display_name(obj)} is full.")

if not obj.can_perform_action():
    return caller.msg(f"You can't do that with {self.get_display_name(obj)}.")
```

## Display Name Usage

### Self.get_display_name() Method
**ALWAYS use `self.get_display_name(obj)` for object names in messages**

```python
# Correct usage
caller.msg(f"You can't fill {self.get_display_name(dest)}.")
caller.msg(f"{self.get_display_name(obj)} is too heavy.")

# WRONG - Don't use obj.get_display_name() directly
caller.msg(f"You can't fill {obj.get_display_name(caller)}.")
```

The `self.get_display_name(obj)` method automatically passes `command_narration=True`, which provides appropriate display names for command contexts.

### DisplayNameWrapper for msg_contents
**Use `DisplayNameWrapper` for objects in `msg_contents` mapping**

```python
from world.utils import DisplayNameWrapper

caller.location.msg_contents(
    "$You() fill the $obj(dest) from $obj(source).",
    from_obj=caller,
    mapping={
        "dest": DisplayNameWrapper(dest, command_narration=True),
        "source": DisplayNameWrapper(source, command_narration=True),
    },
)
```

## Message Broadcasting with msg_contents

### Standard Broadcasting Pattern
```python
# Basic pattern for action messages
caller.location.msg_contents(
    "$You() perform action on $obj(target).",
    from_obj=caller,
    mapping={"target": DisplayNameWrapper(target, command_narration=True)},
)

# Pattern with multiple objects
caller.location.msg_contents(
    "$You() $conj(move) $obj(item) from $obj(source) to $obj(dest).",
    from_obj=caller,
    mapping={
        "item": DisplayNameWrapper(item, command_narration=True),
        "source": DisplayNameWrapper(source, command_narration=True),
        "dest": DisplayNameWrapper(dest, command_narration=True),
    },
)
```

### Message String Conventions
- Use `$You()` for the actor (automatically conjugates for self/others)
- Use `$conj(verb)` for verbs that need conjugation
- Use `$obj(name)` for mapped objects
- Use descriptive mapping keys (`"dest"`, `"source"`, `"item"`, etc.)

### Conditional Messages
```python
# Conditional message content based on object type
floor_msg = "floor" if dest.is_typeclass(Room, exact=False) else "$obj(dest)"
caller.location.msg_contents(
    f"$You() empty the $obj(source) into the {floor_msg}",
    from_obj=caller,
    mapping={
        "source": DisplayNameWrapper(source, command_narration=True),
        "dest": DisplayNameWrapper(dest, command_narration=True),
    }
)
```

## Complete Command Example

```python
from commands.command import Command
from world.physical.liquid import LiquidContainer, Water
from world.utils import DisplayNameWrapper

class CmdFill(Command):
    """Fill one liquid container from another.

    Usage:
      fill <dest>=<source>

    Examples:
      fill waterskin=well
      fill cup=pitcher
    """

    key = "fill"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        dest_name = self.lhs
        source_name = self.rhs

        # Argument validation
        if not dest_name or not source_name:
            return caller.msg("Usage: fill <dest>=<source>")

        # Object search
        dest = caller.search_item(dest_name)
        if not dest:
            return caller.msg(f"You don't see {dest_name}.")

        source = caller.search_item(source_name)
        if not source:
            return caller.msg(f"You don't see {source_name}.")

        # Typeclass validation
        if not dest.is_typeclass(LiquidContainer, exact=False):
            return caller.msg(f"You can't fill {self.get_display_name(dest)}.")

        # State validation
        if dest.is_full:
            return caller.msg(f"{self.get_display_name(dest)} is full.")

        if not (source.is_typeclass(Water, exact=False) or
                source.is_typeclass(LiquidContainer, exact=False)):
            return caller.msg(f"You can't fill {self.get_display_name(dest)} with {self.get_display_name(source)}.")

        # Handle liquid container sources
        if source.is_typeclass(LiquidContainer, exact=False):
            source = source.liquid

        # Perform action
        dest.fill(source)

        # Broadcast message
        caller.location.msg_contents(
            "$You() fill the $obj(dest) from $obj(source).",
            from_obj=caller,
            mapping={
                "dest": DisplayNameWrapper(dest, command_narration=True),
                "source": DisplayNameWrapper(source, command_narration=True),
            },
        )
```

## Error Handling Patterns

### Early Return Pattern
**Always use early returns for error conditions**

```python
# Good - early returns
if not args:
    return caller.msg("Usage: command <args>")

if not obj:
    return caller.msg("You don't see that.")

# Continue with main logic...

# Bad - nested if statements
if args:
    if obj:
        # deeply nested logic
```

### Standard Error Messages
```python
# Object not found
return caller.msg(f"You don't see {obj_name}.")

# Wrong object type
return caller.msg(f"You can't {action} {self.get_display_name(obj)}.")

# Invalid state
return caller.msg(f"{self.get_display_name(obj)} is {state}.")

# Permission denied
return caller.msg("You don't have permission to do that.")

# Usage errors
return caller.msg("Usage: command <syntax>")
```

## Command Organization Patterns

### Package Structure
Commands should be organized by domain:
- `world/living/commands/` - Living being commands (`eat`, `drink`, `rest`)
- `world/physical/commands/` - Physical interaction commands (`fill`, `empty`)
- `commands/` - General gameplay commands (`look`, `get`, `drop`)

### Command Set Integration
```python
# In package __init__.py
from .fill import CmdFill
from .empty import CmdEmpty

class PhysicalCmdSet(default_cmds.CharacterCmdSet):
    key = "PhysicalCommands"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdFill())
        self.add(CmdEmpty())

__all__ = ["CmdFill", "CmdEmpty", "PhysicalCmdSet"]
```

## Testing Considerations

Commands should be testable with the following patterns:
```python
# In tests
def test_command_basic_usage(self):
    result = self.character.execute_cmd("fill cup=well")
    # Assert expected behavior

def test_command_error_conditions(self):
    result = self.character.execute_cmd("fill")
    # Assert error message shown
```

## When Applying Standards to Existing Commands

### **What to Change (Architecture)**
1. **Object Search Method**: `caller.quiet_search()` → `caller.search_item()`
2. **Display Names**: `obj.get_display_name(caller)` → `self.get_display_name(obj)`
3. **Message Mapping**: Add `DisplayNameWrapper(obj, command_narration=True)` to mapping
4. **Import Statements**: Add `from world.utils import DisplayNameWrapper`

### **What NOT to Change (Preserve Working Logic)**
1. **Error Messages**: Keep existing error message text exactly as written
2. **Unique Syntax**: Preserve special command patterns (e.g., switch-based syntax)
3. **Specialized Systems**: Keep MsgObj, perception features, sound effects
4. **Validation Logic**: Don't change working container/liquid/game mechanics
5. **Command Structure**: Preserve unique argument parsing if it works

### **Understanding Specialized Systems**
- **MsgObj**: Provides multi-sensory feedback (visual + sound) for immersion
- **Perception System**: Some commands use sophisticated sensory feedback
- **Container System**: Has complex validation that should be preserved
- **Liquid System**: Uses drain/fill mechanics that work correctly

### **Architectural vs. Content Changes**
- **Architectural**: How objects are searched, displayed, and mapped
- **Content**: What messages say, game logic, validation rules
- **Rule**: Change architecture, preserve content that works

## Key Rules Summary

1. **Always get `caller = self.caller` first**
2. **Use `self.lhs` and `self.rhs` for `=` syntax parsing**
3. **ALWAYS use `caller.search_item()` for object search - NEVER use `caller.search()` with candidates**
4. **Use `self.get_display_name(obj)` for object names in messages**
5. **Use `DisplayNameWrapper` with `command_narration=True` in `msg_contents`**
6. **Use early returns for error conditions**
7. **Always validate arguments, objects, and states before action**
8. **Use `caller.location.msg_contents()` for broadcasting actions**
9. **PRESERVE working error messages and game logic**
10. **PRESERVE specialized systems like MsgObj and perception features**

These patterns ensure consistency, readability, and proper integration with the Evennia framework and the Frontier game's display and messaging systems while preserving working functionality.
