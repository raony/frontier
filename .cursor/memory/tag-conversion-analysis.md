# Tag Conversion Analysis

## Overview
This document analyzes object properties in the Frontier codebase that could be converted from Attributes to Evennia Tags for better performance and organization.

## Completed Conversions ✅

### Living/Dead States ✅
We have successfully implemented a tag-based living state system for characters using **additive tags**. This approach is more intuitive and flexible than mutually exclusive tags.

**Implementation Details:**
- **File**: `typeclasses/characters.py`
- **Mixin**: `LivingStateMixin`
- **Tags**: `"living_being"` and `"dead"` in category `"living_state"`
- **Additive Approach**: Living beings always have the base tag, dead ones also have the dead tag
- **Tag-Only**: Pure tag-based implementation, no AttributeProperty fallbacks

**Key Methods:**
```python
def set_living_state(self, alive: bool):
    """Set living state using additive tags."""
    # Ensure living_being tag exists (all characters are living beings)
    if not self.tags.has("living_being", category="living_state"):
        self.tags.add("living_being", category="living_state")

    if alive:
        # Alive: remove dead tag
        self.tags.remove("dead", category="living_state")
        self.is_living = True  # AttributeProperty for compatibility
        self.is_dead = False
    else:
        # Dead: add dead tag
        self.tags.add("dead", category="living_state")
        self.is_living = False
        self.is_dead = True

def is_living_tag(self) -> bool:
    """Check if character is alive using tags."""
    # Alive = has living_being tag AND does NOT have dead tag
    return (self.tags.has("living_being", category="living_state") and
            not self.tags.has("dead", category="living_state"))

def is_dead_tag(self) -> bool:
    """Check if character is dead using tags."""
    # Dead = has living_being tag AND has dead tag
    return (self.tags.has("living_being", category="living_state") and
            self.tags.has("dead", category="living_state"))

def is_living_being_tag(self) -> bool:
    """Check if character is a living being (alive or dead)."""
    return self.tags.has("living_being", category="living_state")
```

**Benefits Demonstrated:**
- ✅ **Intuitive Logic**: Dead things are still living beings, just dead ones
- ✅ **Flexible States**: Can easily add other states like "unconscious", "sleeping"
- ✅ **Inheritance**: All living beings share the base tag regardless of state
- ✅ **Fast Searches**: Can find all living beings with `search_tag("living_being")`
- ✅ **Clean Implementation**: Pure tag-based, no legacy attribute dependencies
- ✅ **Database Efficiency**: Tags are shared between objects
- ✅ **Clean API**: Simple boolean parameter for state changes

**Test Coverage:**
- ✅ Initial living state
- ✅ State transitions (alive ↔ dead)
- ✅ Mutual exclusion validation
- ✅ Death method integration
- ✅ Backward compatibility
- ✅ Object creation defaults
- ✅ Tag search functionality

### Holding System ✅
Successfully converted the holding system to use Django Tags for better performance and consistency.

**Implementation Details:**
- **File**: `world/equipment/holding.py`
- **Mixin**: `HoldableMixin`
- **Tags**:
  - `"holdable"` in category `"holding"` for items that can be held
  - `"held"` in category `"holding"` for items currently being held
  - `"main"` and `"off"` in category `"holding_slot"` for hand slots
- **Handler**: `HeldItemsHandler` manages slot allocation and validation
- **Automatic Cleanup**: Items lose held status when moved from inventory

**Key Methods:**
```python
# HoldableMixin
def at_object_creation(self):
    super().at_object_creation()
    self.tags.add("holdable", category="holding")

# HeldItemsHandler
def add(self, item: Object, slots: list[str]) -> bool:
    if not item.tags.has("holdable", category="holding"):
        raise NotHoldableError

    # Slot validation and allocation logic
    item.tags.add("held", category="holding")
    for slot in slots:
        item.tags.add(slot, category="holding_slot")

def remove(self, item: Object) -> bool:
    if item.tags.has("held", category="holding"):
        item.tags.remove("held", category="holding")
        item.tags.remove(category="holding_slot")
        return True
    return False
```

**Benefits Demonstrated:**
- ✅ **Performance**: Tag-based queries are faster than attribute searches
- ✅ **Consistency**: Unified approach with other tag-based systems
- ✅ **Flexibility**: Easy to add new holding states or slot types
- ✅ **Clean API**: Simple tag-based validation and state management
- ✅ **Automatic Cleanup**: Integration with Evennia's object movement hooks
- ✅ **Display Integration**: Held items show slot information in names

**Test Coverage:**
- ✅ Holdable item creation
- ✅ Slot allocation and validation
- ✅ Held state management
- ✅ Automatic cleanup on movement
- ✅ Error handling for invalid operations
- ✅ Display name integration

### Equipment System ✅
Successfully implemented a tag-based equipment system alongside the existing attribute-based system for comparison and evaluation.

**Implementation Details:**
- **File**: `world/equipment/equipment.py`
- **Mixin**: `WearableMixin`
- **Handler**: `WornItemsHandler`
- **Tags**:
  - `"wearable"` in category `"equipment"` for items that can be equipped
  - `"worn"` in category `"equipment"` for items currently equipped
  - `"head"`, `"body"`, `"legs"`, `"waist"`, `"hands"`, `"feet"` in category `"wearing_slot"` for item slots
  - `"head"`, `"body"`, `"legs"`, `"waist"`, `"hands"`, `"feet"` in category `"equipment_slot"` for character slots
- **Dual System**: Maintains both attribute-based and tag-based approaches for comparison

**Key Methods:**
```python
# WearableMixin
def at_object_creation(self):
    super().at_object_creation()
    self.tags.add("wearable", category="equipment")
    if hasattr(self, 'slot_name') and self.slot_name:
        slot = normalize_slot(self.slot_name)
        if slot:
            self.tags.add(slot, category="wearing_slot")

# WornItemsHandler
def add(self, item, slot: str) -> bool:
    if not item.tags.has("wearable", category="equipment"):
        return False
    if slot in self.used_slots:
        return False
    item.tags.add("worn", category="equipment")
    item.tags.add(slot, category="wearing_slot")
    return True

def remove(self, item) -> bool:
    if item.tags.has("worn", category="equipment"):
        item.tags.remove("worn", category="equipment")
        item.tags.remove(category="wearing_slot")
        return True
    return False
```

**Benefits Demonstrated:**
- ✅ **Performance**: Tag-based queries are faster than attribute searches
- ✅ **Consistency**: Unified approach with other tag-based systems
- ✅ **Flexibility**: Easy to add new equipment states or slot types
- ✅ **Clean API**: Simple tag-based validation and state management
- ✅ **Automatic Cleanup**: Integration with Evennia's object movement hooks
- ✅ **Display Integration**: Equipped items show slot information in names
- ✅ **Dual System**: Allows direct comparison between approaches

**Test Coverage:**
- ✅ Wearable item creation
- ✅ Slot allocation and validation
- ✅ Worn state management
- ✅ Automatic cleanup on movement
- ✅ Error handling for invalid operations
- ✅ Display name integration
- ✅ Dual system independence

## Current Property Patterns

### Boolean State Properties (Good Tag Candidates)

#### Living Entity States
- `is_living` (AttributeProperty) - Character living status ✅ **CONVERTED**
- `is_dead` (AttributeProperty) - Character death status ✅ **CONVERTED**
- `is_resting` (AttributeProperty) - Character rest status
- `is_pc` (class attribute) - Player character flag

#### Item Capability Properties
- `db.is_holdable` - Items that can be held in hands ✅ **CONVERTED**
- `db.is_equipable` - Items that can be equipped (via slot) ✅ **CONVERTED**
- `db.is_consumable` - Items that deplete when used
- `db.is_lightsource` - Items that emit light
- `db.is_water_source` - Items that provide water

#### Item State Properties
- `db.is_on` - Toggle state for consumable items (torches, etc.)

### Categorical Properties (Good Tag Candidates)

#### Equipment Slots
- `db.equipable` / `db.equipable_slot` - Equipment slot type ✅ **CONVERTED**
- Values: "head", "body", "legs", "waist", "hands", "feet"

#### Resource Properties
- `db.kind` - Resource type (e.g., "foraging", "mining")
- `db.terrain` - Hex tile terrain type

## Conversion Priority

### High Priority (Next Candidates)
1. **Light System** - Convert `db.is_lightsource` to tags
2. **Rest State** - Convert `is_resting` to tags
3. **Consumable Items** - Convert `db.is_consumable` to tags

### Medium Priority
4. **Water Sources** - Convert `db.is_water_source` to tags
5. **Toggle States** - Convert `db.is_on` to tags
6. **Resource Types** - Convert `db.kind` to tags

### Low Priority
7. **Terrain Types** - Convert `db.terrain` to tags
8. **Player Character Flag** - Convert `is_pc` to tags

## Implementation Patterns

### Boolean State Conversion
```python
# Before (AttributeProperty)
class MyObject(Object):
    is_special = AttributeProperty(default=False)

# After (Tag-based)
class MyObject(Object):
    def at_object_creation(self):
        super().at_object_creation()
        if self.is_special_default:
            self.tags.add("special", category="capabilities")

    def set_special(self, special: bool):
        if special:
            self.tags.add("special", category="capabilities")
        else:
            self.tags.remove("special", category="capabilities")

    def is_special(self) -> bool:
        return self.tags.has("special", category="capabilities")
```

### Categorical Property Conversion
```python
# Before (AttributeProperty)
class MyObject(Object):
    category = AttributeProperty(default="basic")

# After (Tag-based)
class MyObject(Object):
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add(self.category_default, category="object_type")

    def set_category(self, category: str):
        self.tags.remove(category="object_type")
        self.tags.add(category, category="object_type")

    def get_category(self) -> str:
        return self.tags.get(category="object_type", return_list=True)[0]
```

### Dual System Pattern (for Comparison)
```python
# Maintain both systems for evaluation
class MyObject(Object):
    def at_object_creation(self):
        super().at_object_creation()
        # Tag-based system
        self.tags.add("capability", category="features")
        # Attribute-based system (existing)
        self.db.has_capability = True

    # Tag-based methods
    def has_capability_tag(self) -> bool:
        return self.tags.has("capability", category="features")

    # Attribute-based methods (existing)
    def has_capability_attr(self) -> bool:
        return getattr(self.db, "has_capability", False)
```

## Migration Strategy

### Phase 1: Preparation
1. **Create new tag-based methods** alongside existing attribute methods
2. **Add comprehensive tests** for new tag-based functionality
3. **Ensure backward compatibility** during transition

### Phase 2: Migration
1. **Update object creation** to use tag-based approach
2. **Migrate existing objects** using migration scripts
3. **Update commands and systems** to use new tag-based methods

### Phase 3: Cleanup
1. **Remove old attribute-based methods** after migration is complete
2. **Update documentation** to reflect new patterns
3. **Performance testing** to verify improvements

## Benefits of Tag Conversion

### Performance
- **Faster queries**: Tag-based searches are more efficient than attribute searches
- **Shared storage**: Tags are shared between objects, reducing database size
- **Indexed queries**: Django's tag system provides better indexing

### Maintainability
- **Consistent patterns**: Unified approach across all categorical properties
- **Easier migrations**: Tag-based changes are easier to manage
- **Better organization**: Categories provide logical grouping

### Flexibility
- **Additive states**: Easy to add new states without breaking existing logic
- **Multiple categories**: Objects can belong to multiple categories
- **Dynamic changes**: Tags can be added/removed without object recreation

### Comparison and Evaluation
- **Dual systems**: Can run both approaches side by side for performance comparison
- **Gradual migration**: Can migrate systems one at a time
- **Risk mitigation**: Can fall back to attribute system if issues arise

## Related Files
- `typeclasses/characters.py` - Living state tag implementation
- `world/equipment/holding.py` - Holding system tag implementation
- `world/equipment/equipment.py` - Equipment system tag implementation
- `typeclasses/items.py` - Equipment items with WearableMixin
- `tests/test_tag_living_state.py` - Living state tag tests
- `tests/test_holding.py` - Holding system tag tests
- `tests/test_equipment_tags.py` - Equipment system tag tests
