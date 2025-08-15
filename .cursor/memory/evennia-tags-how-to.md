# Evennia Tags System

## Overview
Tags in Evennia are short text labels that can be attached to objects for organization, grouping, and quick property lookup. They work similarly to luggage tags - you attach them to identify properties or categories of objects.

## Key Concepts

### What Tags Are
- Short text labels attached to objects
- Used for organization and grouping
- More efficient than Attributes since they're shared between objects
- Tags don't carry values - existence of the tag itself is what matters
- An object either has a tag or doesn't

### Tag Properties
- **key**: The name of the tag (main search property)
- **category**: Allows retrieving specific subsets of tags (e.g., "zones", "outdoor locations")
- **data**: Optional text field with information about the tag group
- **model**: Internal field for model object description
- **tagtype**: Top-level category for Aliases and Permissions

## Usage Methods

### In-Game Commands
```
tag obj = tagname
tag/search furniture
```

### TagHandler (Code)
```python
# Add tags
obj.tags.add("mytag")
obj.tags.add("mytag", category="foo")

# Check tags
obj.tags.has("mytag", category="foo")
obj.tags.all()  # returns list of Tags

# Remove tags
obj.tags.remove("mytag")
obj.tags.clear()  # removes all tags
```

### TagProperty (Class Definition)
```python
from evennia import TagProperty

class Sword(DefaultObject):
    can_be_wielded = TagProperty(category='combat')
    has_sharp_edge = TagProperty(category='combat')
```

### TagCategoryProperty (Class Definition)
```python
from evennia import TagCategoryProperty

class Sword(DefaultObject):
    damage_type = TagCategoryProperty("piercing", "slashing")
    crafting_element = TagCategoryProperty("blade", "hilt", "pommel")
```

## Searching Tags

### Using evennia.search_tag()
```python
import evennia

# Search for objects
objs = evennia.search_tag("furniture")
objs = evennia.search_tag("furniture", category="luxurious")
objs = evennia.search_tag(category="forest")

# Search for scripts
weather = evennia.search_tag_script("weather")

# Search for accounts
accounts = evennia.search_tag_account("guestaccount")
```

### Category Behavior
- Not specifying a category gives the tag a category of `None`
- `None` is considered a unique key + category combination
- Searching for "furniture" only returns objects with category `None`
- Must explicitly specify category to get "luxurious" furniture

## Special Tag Types

### Aliases
```python
boy.aliases.add("rascal")
boy.aliases.all()
```

### Permissions
```python
boy.permissions.add("Builders")
boy.permissions.remove("Builders")
```

## Best Practices

### When to Use Tags
- Grouping objects by properties (e.g., all sharp objects, all outdoor rooms)
- Quick lookups for game mechanics (e.g., weather affecting outdoor areas)
- Categorizing objects for spells or effects
- Organizing objects by zones or areas

### When NOT to Use Tags
- Storing object-specific information (use Attributes instead)
- Storing values or data (Tags are boolean - exist or don't exist)
- Information that changes frequently

### Performance Benefits
- Tags are shared between objects with the same tag
- Very fast database lookups
- Efficient for bulk operations on tagged objects

## Common Use Cases

### Combat System
```python
# Tag all weapons
sword.tags.add("weapon", category="combat")
dagger.tags.add("weapon", category="combat")

# Find all weapons
weapons = evennia.search_tag("weapon", category="combat")
```

### Weather System
```python
# Tag outdoor rooms
garden.tags.add("outdoor", category="weather")
forest.tags.add("outdoor", category="weather")

# Weather affects all outdoor areas
outdoor_rooms = evennia.search_tag("outdoor", category="weather")
```

### Guild System
```python
# Tag guild members
fighter.tags.add("fighter_guild", category="guild")
warrior.tags.add("fighter_guild", category="guild")

# Find all guild members
fighters = evennia.search_tag("fighter_guild", category="guild")
```

## Auto-Sync Behavior

### TagProperty and TagCategoryProperty
- If you delete a tag via TagHandler, it gets re-added when property is accessed
- If you add a new tag via TagHandler, it gets included in the property
- Use `del obj.property` to re-sync with database defaults

```python
# Tag gets re-added automatically
obj.tags.remove("mytag", "category")
obj.mytag  # tag is re-created!

# New tag gets included
obj.tags.add("newtag", "category")
obj.category_property  # includes "newtag"

# Re-sync with defaults
del obj.category_property
obj.category_property  # only shows default keys
```

## Additive Tags (Recommended Approach)

Instead of mutually exclusive tags, consider using **additive tags** where objects have a base tag plus state-specific tags. This approach is more intuitive and flexible.

### Example: Living Beings
```python
# Base tag: "living_being" (all living entities have this)
# State tag: "dead" (only dead living beings have this)

# States:
# - Alive: has "living_being" tag, does NOT have "dead" tag
# - Dead: has both "living_being" AND "dead" tags
# - Not living: has neither tag

def is_alive(self) -> bool:
    return (self.tags.has("living_being", category="living_state") and
            not self.tags.has("dead", category="living_state"))

def is_dead(self) -> bool:
    return (self.tags.has("living_being", category="living_state") and
            self.tags.has("dead", category="living_state"))

def is_living_being(self) -> bool:
    return self.tags.has("living_being", category="living_state")
```

**Benefits:**
- **Intuitive**: Dead things are still living beings, just dead ones
- **Flexible**: Easy to add new states (unconscious, sleeping, etc.)
- **Inheritance**: All living beings share the base tag
- **Fast Queries**: Can find all living beings with one search

## Mutually Exclusive Tags

Evennia tags don't have built-in mutual exclusion, so you need to implement this pattern manually. Here are several approaches:

### Approach 1: TagCategoryProperty with Single Value
```python
from evennia import TagCategoryProperty

class Character(DefaultCharacter):
    # Only one state can be active at a time
    living_state = TagCategoryProperty("alive", "dead", "unconscious")

    def set_state(self, new_state: str):
        """Set the living state, ensuring mutual exclusion."""
        if new_state not in ["alive", "dead", "unconscious"]:
            raise ValueError(f"Invalid state: {new_state}")

        # Remove all existing state tags
        self.tags.remove("alive", category="state")
        self.tags.remove("dead", category="state")
        self.tags.remove("unconscious", category="state")

        # Add the new state tag
        self.tags.add(new_state, category="state")

    def is_alive(self) -> bool:
        return self.tags.has("alive", category="state")

    def is_dead(self) -> bool:
        return self.tags.has("dead", category="state")
```

### Approach 2: Custom Property with Validation
```python
from evennia import TagProperty

class Character(DefaultCharacter):
    # Individual tag properties with validation
    is_alive = TagProperty(category="state")
    is_dead = TagProperty(category="state")
    is_unconscious = TagProperty(category="state")

    def set_alive(self):
        """Set character as alive, removing other states."""
        self.tags.remove("dead", category="state")
        self.tags.remove("unconscious", category="state")
        self.tags.add("alive", category="state")

    def set_dead(self):
        """Set character as dead, removing other states."""
        self.tags.remove("alive", category="state")
        self.tags.remove("unconscious", category="state")
        self.tags.add("dead", category="state")

    def set_unconscious(self):
        """Set character as unconscious, removing other states."""
        self.tags.remove("alive", category="state")
        self.tags.remove("dead", category="state")
        self.tags.add("unconscious", category="state")
```

### Approach 3: State Manager Mixin
```python
class MutuallyExclusiveStateMixin:
    """Mixin for managing mutually exclusive state tags."""

    def set_state(self, state_name: str, category: str = "state"):
        """Set a state tag, removing all others in the same category."""
        # Remove all existing tags in this category
        existing_tags = self.tags.get(category=category)
        for tag in existing_tags:
            self.tags.remove(tag, category=category)

        # Add the new state tag
        self.tags.add(state_name, category=category)

    def get_state(self, category: str = "state") -> str:
        """Get the current state tag in the given category."""
        tags = self.tags.get(category=category)
        return tags[0] if tags else None

    def has_state(self, state_name: str, category: str = "state") -> bool:
        """Check if object has a specific state tag."""
        return self.tags.has(state_name, category=category)

class Character(MutuallyExclusiveStateMixin, DefaultCharacter):
    def set_alive(self):
        self.set_state("alive", category="state")

    def set_dead(self):
        self.set_state("dead", category="state")

    def is_alive(self) -> bool:
        return self.has_state("alive", category="state")
```

### Approach 4: Enum-Based State Management
```python
from enum import Enum

class LivingState(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    UNCONSCIOUS = "unconscious"

class Character(DefaultCharacter):
    def set_living_state(self, state: LivingState):
        """Set living state with automatic mutual exclusion."""
        # Remove all existing living state tags
        for enum_state in LivingState:
            self.tags.remove(enum_state.value, category="state")

        # Add the new state
        self.tags.add(state.value, category="state")

    def get_living_state(self) -> LivingState:
        """Get current living state."""
        for enum_state in LivingState:
            if self.tags.has(enum_state.value, category="state"):
                return enum_state
        return LivingState.ALIVE  # Default
```

## Best Practices for Mutually Exclusive Tags

### 1. Use Categories for Grouping
```python
# Group related states in the same category
self.tags.add("alive", category="living_state")
self.tags.add("dead", category="living_state")  # This replaces "alive"

# Different categories can coexist
self.tags.add("alive", category="living_state")
self.tags.add("resting", category="activity_state")  # These can coexist
```

### 2. Implement Validation Methods
```python
def validate_state_transition(self, from_state: str, to_state: str) -> bool:
    """Validate if a state transition is allowed."""
    valid_transitions = {
        "alive": ["dead", "unconscious"],
        "dead": ["alive"],  # Resurrection
        "unconscious": ["alive", "dead"]
    }
    return to_state in valid_transitions.get(from_state, [])
```

### 3. Use Property Decorators for Clean Access
```python
@property
def is_alive(self) -> bool:
    return self.tags.has("alive", category="state")

@is_alive.setter
def is_alive(self, value: bool):
    if value:
        self.set_state("alive", category="state")
    else:
        self.set_state("dead", category="state")
```

### 4. Database Consistency
```python
def at_object_creation(self):
    """Ensure consistent initial state."""
    super().at_object_creation()
    # Set default state if none exists
    if not self.tags.get(category="state"):
        self.tags.add("alive", category="state")
```

## Common Mutually Exclusive Patterns

### Equipment Slots
```python
# Only one item per slot
def equip_to_slot(self, item, slot: str):
    # Remove any existing item in this slot
    existing = evennia.search_tag(slot, category="equipped", location=self)
    for obj in existing:
        obj.tags.remove(slot, category="equipped")

    # Add new item to slot
    item.tags.add(slot, category="equipped")
```

### Game States
```python
# Character can only be in one game state at a time
game_states = ["exploring", "combat", "trading", "resting"]

def set_game_state(self, state: str):
    if state not in game_states:
        raise ValueError(f"Invalid game state: {state}")

    # Remove all existing game states
    for existing_state in game_states:
        self.tags.remove(existing_state, category="game_state")

    # Add new state
    self.tags.add(state, category="game_state")
```
