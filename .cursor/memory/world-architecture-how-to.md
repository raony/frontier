# World Package Architecture Guide

This document describes the new modular architecture of the `world/` package, which organizes game systems into specialized subpackages for better maintainability and separation of concerns.

## Package Structure

```
world/
├── living/           # Living being systems
│   ├── __init__.py
│   ├── base.py      # LivingMixin core functionality
│   ├── metabolism.py # Hunger, thirst, tiredness systems
│   ├── food.py      # Food consumption mechanics
│   ├── people.py    # Person class definition
│   ├── perception.py # Sensory capabilities
│   ├── consumables.py # (empty - future expansion)
│   └── commands/    # Living-specific commands
│       ├── __init__.py # AliveCmdSet and LivingBuilderCmdSet
│       ├── eat.py
│       ├── drink.py
│       ├── rest.py
│       ├── stand.py
│       ├── kill.py
│       ├── reset.py
│       └── darkvision.py
├── physical/         # Physical world systems
│   ├── __init__.py
│   ├── weight.py    # Weight system handlers
│   ├── liquid.py    # Liquid and container systems
│   └── commands/    # Physical interaction commands
│       ├── __init__.py
│       ├── fill.py
│       └── empty.py
├── hexmap.py        # Core game content (unchanged)
├── prototypes.py
├── help_entries.py
├── models.py
├── time_service.py
├── utils.py
└── ...
```

## Design Principles

### 1. Separation of Concerns
- **Living systems** handle biology, survival, consciousness
- **Physical systems** handle matter, physics, containers
- **Core world** handles game mechanics, content, utilities

### 2. Handler Pattern
Both packages extensively use handler classes for complex attribute management:

```python
# Example: MetabolismHandler for hunger/thirst/tiredness
class MetabolismHandler:
    def __init__(self, obj, attribute, thresholds, increase_modifier):
        self.obj = obj
        self.attribute = attribute
        # ... handler setup

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # Complex logic with validation, persistence, notifications
```

### 3. Mixin Architecture
System functionality is provided through mixins that can be combined:

```python
# LivingMixin combines multiple capabilities
class LivingMixin(MetabolismMixin, PerceptionMixin):
    # Adds living being functionality to any object

# Person combines all traits
class Person(LivingMixin, ObjectParent, HolderMixin, WearerMixin, SkillableMixin, DefaultCharacter):
    pass
```

### 4. Command Organization
Commands are grouped by domain and packaged with related systems:

```python
# world/living/commands/__init__.py
class AliveCmdSet(default_cmds.CharacterCmdSet):
    """Commands available only to living characters."""
    def at_cmdset_creation(self):
        self.add(CmdEat())
        self.add(CmdDrink())
        self.add(CmdRest())
        self.add(CmdStand())
```

## Living Systems (`world/living/`)

### Core Classes

**`LivingMixin`** - Base class for all living beings
- Combines `MetabolismMixin` and `PerceptionMixin`
- Manages life/death states using tags
- Handles command set loading/unloading for alive/dead states
- Integrates weight system for living beings

**`Person`** - Ready-to-use character class
- Combines all major traits: living, holder, wearer, skilled
- Extends `DefaultCharacter` for Evennia integration

### Metabolism System

**Handler Classes:**
- `MetabolismHandler` - Base class for survival needs
- `HungerManager` - Hunger tracking with food consumption
- `ThirstManager` - Thirst tracking with liquid consumption
- `TirednessManager` - Fatigue with rest/recovery mechanics

**Features:**
- Configurable thresholds and progression rates
- Automatic notifications at threshold levels
- Status labels for display (`"hungry"`, `"thirsty"`, etc.)
- Death when any need reaches 100%
- Rest mechanics for tiredness recovery

### Food System

**`FoodHandler`** - Manages consumable food items
- Tracks calories and consumption state
- Handles partial eating with waste calculation
- Weight reduction as food is consumed
- Display name changes based on consumption state

**`FoodMixin`** - Adds food functionality to objects
- Lazy-loaded food handler
- Automatic food tagging
- Display integration

### Command Architecture

Commands are organized into command sets by functionality:

- **`AliveCmdSet`** - Core living commands (eat, drink, rest, stand)
- **`LivingBuilderCmdSet`** - Admin commands (reset, kill, darkvision)

## Physical Systems (`world/physical/`)

### Weight System

**`WeightHandler`** - Manages object weight
- Individual weight tracking
- Recursive total weight calculation (includes contents)
- Weight modification methods
- Integration with display names for weight indicators

**`WeightMixin`** - Adds weight to any object
- Lazy-loaded weight handler
- Automatic weight initialization
- Display integration with weight indicators (░▒█)

### Liquid System

**`Water`** - Liquid objects with physics
- Weight-based quantity tracking
- Location-aware display (drops, puddles, everywhere)
- Liquid mixing and drainage
- Potable/non-potable liquid types

**`LiquidContainerMixin`** - Container functionality for liquids
- Capacity management
- Fill/empty operations
- Liquid transfer mechanics
- Fill state display

**`LiquidContainer`** - Ready-to-use liquid container
- Configurable capacity
- Status display integration
- Fill state descriptions

## Integration Patterns

### Tag-Based State Management
Both packages use Django tags for categorical and state properties:

```python
# Living state tags
self.tags.add("living_being", category="living_state")
self.tags.add("dead", category="living_state")
self.tags.add("resting", category="living_state")

# Food identification
self.tags.add("food", category="food")
```

### Attribute Categories
Persistent data is organized by categories:

```python
# Metabolism attributes
category="metabolism"  # hunger, thirst, tiredness values

# Physical attributes
category="physical"    # weight, liquid properties

# Food attributes
category="food"        # calories, waste proportion
```

### Lazy Property Loading
Handlers use lazy properties for performance:

```python
@lazy_property
def weight(self):
    return WeightHandler(self)

@lazy_property
def hunger(self):
    return HungerManager(self)
```

## Usage Examples

### Creating Living Beings
```python
from world.living.people import Person

# Create a person with all living systems
person = create_object(Person, key="villager", location=room)
# Automatically has: metabolism, weight, perception, equipment, skills
```

### Food and Consumption
```python
from world.living.food import FoodMixin
from typeclasses.objects import Object

class Apple(FoodMixin, Object):
    default_weight = 150  # grams

apple = create_object(Apple, key="apple", location=person)
person.execute_cmd("eat apple")  # Uses food handler system
```

### Liquid Containers
```python
from world.physical.liquid import LiquidContainer, Water

# Create container and water
waterskin = create_object(LiquidContainer, key="waterskin", location=person)
water = create_object(Water, key="water", location=well)

# Fill container
person.execute_cmd("fill waterskin from well")  # Uses liquid system
```

### Weight Management
```python
# All objects automatically have weight
sword.weight.value = 1200  # 1.2kg
total_weight = person.weight.total  # Includes all carried items

# Weight affects display
person.execute_cmd("look sword")  # Shows weight indicator
```

## Migration Notes

This architecture represents a migration from monolithic systems to modular packages:

1. **Handler Pattern** - Complex attribute management moved to dedicated handler classes
2. **Package Organization** - Related functionality grouped into logical packages
3. **Mixin Composition** - Functionality provided through composable mixins
4. **Command Grouping** - Commands packaged with their related systems
5. **Tag-Based States** - Categorical properties use Django tags for performance

## Related Memory Files
- `system_patterns.md` - General patterns and conventions
- `project_context.md` - High-level project structure
- `active_context.md` - Current development status
