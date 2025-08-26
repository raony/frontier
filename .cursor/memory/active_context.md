# Active Context - Current Development

## Recent Changes

### Container System Implementation (Completed)
- **Created `ContainerMixin`** in `typeclasses/container.py` - provides container functionality using Django tags
- **Added `Container` class** that inherits from `ContainerMixin` and `Object` for ready-to-use containers
- **Container identification**: Uses `tags.add("container", category="container")` for identification
- **Capacity management**: Supports both item count limits and weight limits
- **Container features**:
  - Item count capacity (default 10 items)
  - Weight capacity (default 5000g)
  - Lock/unlock functionality
  - Container descriptions
  - Nested container support
  - Container status reporting
  - Container display formatting
- **Container API methods**:
  - `is_container()` - Check if object is a container
  - `can_hold_item(item)` - Check if container can hold item
  - `get_container_status()` - Get detailed container status
  - `get_container_display()` - Get formatted container display
  - `empty_container()` - Empty all contents
  - `search_container()` - Search within container
- **Comprehensive test coverage** in `tests/test_container_system.py` with 16/16 tests passing

### Container System API
- **Container identification**: `obj.tags.has("container", category="container")`
- **Capacity checking**: `container.can_hold_item(item)` - checks both count and weight limits
- **Status reporting**: `container.get_container_status()` - returns dict with items/weight info
- **Display integration**: Container info automatically included in object descriptions
- **Weight integration**: Works seamlessly with existing weight system
- **Default settings**: 10 items, 5000g weight limit, 200g container weight

### Usage Examples
```python
# Create a container
container = create_object(Container, key="chest", location=room)

# Check container capacity
if container.can_hold_item(item):
    item.move_to(container)

# Get container status
status = container.get_container_status()
print(f"Items: {status['items']['current']}/{status['items']['maximum']}")

# Empty container
container.empty_container(character)

# Custom container class
class TreasureChest(ContainerMixin, Object):
    container_capacity_default = 5
    container_weight_limit_default = 2000
    weight_default = 500
```

### Equipment System Tag Implementation (Completed)
- **Implemented tag-based equipment system** alongside existing attribute-based system for comparison
- **Added `WearableMixin`** to `world/equipment/equipment.py` - provides tag-based equipment functionality
- **Created `WornItemsHandler`** for managing worn items using tags:
  - Uses `category="equipment"` for wearable and worn states
  - Uses `category="wearing_slot"` for slot tags (head, body, legs, waist, hands, feet)
  - Uses `category="equipment_slot"` for character equipment slots
- **Updated all equipment item typeclasses** in `typeclasses/items.py` to include `WearableMixin`
- **Enhanced character equipment API** with tag-based methods:
  - `equip_tag(item, slot)` - Equip item using tag system
  - `unequip_tag(slot_or_item)` - Unequip item using tag system
  - `get_equipment_display_lines_tag()` - Get equipment display using tags
  - `get_equipped_in_slot_tag(slot)` - Get item in slot using tags
- **Added new commands** for tag-based equipment system:
  - `equip_tag <item> to <slot>` - Equip item using tag system
  - `unequip_tag <slot>` - Unequip item using tag system
  - `equipment_tag` - Show equipment using tag system
  - `equipment_compare` - Compare both systems side by side
- **Comprehensive test coverage** in `tests/test_equipment_tags.py` with 10/10 tests passing

### Equipment System API (Dual System)
- **Attribute-based system** (existing):
  - `equip(item)` - Equip item to default slot
  - `unequip(slot_or_item)` - Unequip item
  - `get_equipment_display_lines()` - Get equipment display
  - `get_equipped_in_slot(slot)` - Get item in slot
- **Tag-based system** (new):
  - `equip_tag(item, slot)` - Equip item to specific slot
  - `unequip_tag(slot_or_item)` - Unequip item
  - `get_equipment_display_lines_tag()` - Get equipment display
  - `get_equipped_in_slot_tag(slot)` - Get item in slot

### Tag Categories for Equipment
- **`"wearable"`** in category `"equipment"` - Items that can be equipped
- **`"worn"`** in category `"equipment"` - Items currently equipped
- **`"head"`, `"body"`, `"legs"`, `"waist"`, `"hands"`, `"feet"`** in category `"wearing_slot"` - Item's equipment slot
- **`"head"`, `"body"`, `"legs"`, `"waist"`, `"hands"`, `"feet"`** in category `"equipment_slot"` - Character's available slots

### Usage Examples
```python
# Tag-based equipment system
char.equip_tag(helmet, "head")           # Equip helmet to head slot
char.unequip_tag("head")                  # Unequip head slot
char.get_equipment_display_lines_tag()    # Get equipment display

# Commands
equip_tag helmet to head                  # Equip helmet to head
unequip_tag head                          # Unequip head slot
equipment_tag                             # Show equipment (tag system)
equipment_compare                         # Compare both systems
```

### Holding System Tag Conversion (Completed)
- **Converted holding system to use Django Tags** instead of AttributeProperty
- **Updated `HoldableMixin`** to use `tags.add("holdable", category="holding")` on object creation
- **Enhanced `HeldItemsHandler`** to work with tag-based slot management:
  - Uses `category="holding_slot"` for slot tags (main, off)
  - Uses `category="holding"` for holdable and held states
  - Improved slot validation and management
- **Updated `HolderMixin`** to use tag-based slot initialization
- **Enhanced display methods** to show holding status in item names
- **Comprehensive test coverage** in `tests/test_holding.py` with 65/65 tests passing

### Holding System API (Updated)
- **Tag-based holdable detection**: `item.tags.has("holdable", category="holding")`
- **Tag-based held state**: `item.tags.has("held", category="holding")`
- **Slot management**: Uses `category="holding_slot"` for main/off hand slots
- **Automatic cleanup**: Items automatically lose held status when moved from inventory
- **Display integration**: Held items show slot information in their names

### Weight System Implementation (Completed)
- **Added `WeightMixin`** to `typeclasses/objects.py` - provides weight functionality to all objects
- **Updated base `Object` class** to include `WeightMixin` by default
- **Added weight properties** to all item typeclasses with realistic default weights:
  - Basic objects: 100g default
  - Food items: 50g (simple), 200g (portioned), 800g (roasted chicken)
  - Equipment: 50g (hands), 100g (waist), 150g (head), 200g (feet), 300g (legs), 500g (body)
  - Tools: 300g (torch), 150g (liquid containers)
- **Created weight commands** in `commands/weight.py`:
  - `weight` / `wt` - show inventory weight or specific item weight
  - `setweight` - Builder command to set item weights
- **Added commands to command sets** in `commands/default_cmdsets.py`
- **Created comprehensive tests** in `tests/test_weight_system.py`
- **Test reorganization**: Removed hold/release tests from `test_hold_and_light.py`, renamed to `test_light.py`

### Weight System API
- **`get_weight()`** - Returns weight in grams (int)
- **`set_weight(weight)`** - Sets weight in grams (int, non-negative)
- **`weight_default`** - Class attribute for default weight
- **`db.weight`** - Persistent attribute storing weight value

### Usage Examples
```python
# In-game commands
weight                    # Show total inventory weight
weight apple             # Show specific item weight
weight all               # List all items with weights
setweight sword = 1200   # Set item weight (Builder only)

# In code
obj.get_weight()         # Get weight in grams
obj.set_weight(500)      # Set weight to 500g
obj.weight_default = 200 # Set default for new instances
```

## Current Focus - World Package Architecture Migration
- **World package reorganization completed** - Systems moved to specialized subpackages
- **Living systems package** (`world/living/`) - metabolism, food, people, living commands
- **Physical systems package** (`world/physical/`) - weight, liquids, physical commands
- **Handler pattern adoption** - Complex attribute management through dedicated handler classes
- **Modular command organization** - Commands grouped with related systems (`AliveCmdSet`, physical commands)
- **Improved code organization** - Better separation of concerns and maintainability
- Container system successfully implemented with tag-based approach
- Equipment system successfully implemented with dual approach (tags + attributes)
- Holding system successfully converted to tag-based approach
- Weight system is now fully implemented and tested

## Next Steps
- Fix failing tests (light system and weight system)
- Consider weight-based carrying capacity limits
- Add weight to character encumbrance calculations
- Integrate weight with movement/travel systems
- Add weight-based crafting requirements
- Continue tag system conversion for other boolean properties
- Evaluate performance differences between tag and attribute systems

## Related Files

### World Package Architecture
- `world/living/base.py` - LivingMixin core functionality
- `world/living/metabolism.py` - MetabolismMixin and handlers (hunger, thirst, tiredness)
- `world/living/food.py` - FoodHandler and FoodMixin for consumables
- `world/living/people.py` - Person class combining all living traits
- `world/living/perception.py` - PerceptionMixin for sensory capabilities
- `world/living/commands/__init__.py` - AliveCmdSet and LivingBuilderCmdSet
- `world/living/commands/` - Living-specific commands (eat, drink, rest, stand, etc.)
- `world/physical/weight.py` - WeightHandler and WeightMixin
- `world/physical/liquid.py` - Water, LiquidContainer, and liquid systems
- `world/physical/commands/` - Physical commands (fill, empty)
- `world/utils.py` - Shared utilities (null_func)

### Legacy Systems (Pre-Architecture)
- `world/equipment/equipment.py` - WearableMixin and WornItemsHandler
- `typeclasses/characters.py` - Updated with tag-based equipment methods
- `typeclasses/items.py` - All equipment items now include WearableMixin
- `commands/equip.py` - New tag-based equipment commands
- `commands/default_cmdsets.py` - Added new equipment commands
- `tests/test_equipment_tags.py` - Comprehensive equipment tag system tests
- `world/equipment/holding.py` - Updated holding system with tag-based approach
- `typeclasses/objects.py` - WeightMixin and base Object class
- `commands/weight.py` - Weight commands
- `commands/hold.py` - Hold command (updated for tag system)
- `tests/test_weight_system.py` - Weight system tests
- `tests/test_holding.py` - Updated holding system tests
- `tests/test_light.py` - Light system tests (renamed from test_hold_and_light.py)

---

## Previous Context

### Tag System Conversion (Completed)
- **Converted from Evennia Tags to Django Tags** for better performance and querying
- **Updated all typeclasses** to use new tag system
- **Created migration scripts** for existing data
- **Updated commands and systems** to work with new tag format
- **Comprehensive testing** of tag functionality

### Equipment System (Completed)
- **Slot-based equipment system** with head, body, legs, waist, hands, feet
- **Equipment commands**: `equip`, `unequip`, enhanced `inventory`
- **Equipment mixins** for different slot types
- **Equipment persistence** using object IDs in character attributes

### Survival System (Completed)
- **Hunger, thirst, tiredness** as persistent attributes
- **Metabolism system** with configurable rates
- **Rest mechanics** for recovery
- **Food and liquid consumption** systems

### Light System (Completed)
- **LightSourceMixin** for light-emitting objects
- **Room light aggregation** including sunlight
- **Light commands**: `light`, `extinguish`, `darkvision`
- **Torch system** with fuel consumption

### Time System (Completed)
- **Game time** running 6× faster than real time
- **Time-based events** and scheduling
- **Time commands** for players and builders
- **Integration** with metabolism and other systems

### Resource System (Completed)
- **Forageable resources** with abundance and quality
- **Resource depletion** mechanics
- **Foraging command** with skill integration
- **Resource spawning** and management

### Hex Map System (Completed)
- **Hexagonal coordinate system** for world mapping
- **Hex tile objects** with terrain types
- **Hex map utilities** for navigation
- **Weather system** integration

### Skills System (Completed)
- **Skill-based actions** with levels and experience
- **Skill commands** for players and builders
- **Skill integration** with foraging and other activities
- **Skill persistence** and progression

### Web Interface (Completed)
- **Django admin integration** for game management
- **Web client customization** for better UX
- **Template overrides** for consistent styling
- **Static asset management** for custom CSS/JS

### Testing Framework (Completed)
- **Comprehensive test suite** for all systems
- **Evennia test utilities** integration
- **Test coverage** for commands, typeclasses, and systems
- **Automated testing** setup

---

## Development Patterns

### Code Style
- **Pythonic, readable, explicit names**
- **Business logic in typeclasses/commands**
- **Configuration in server/conf**
- **Comprehensive documentation**

### Evennia Integration
- **Extend Evennia defaults** via typeclasses
- **Use Evennia utilities** and patterns
- **Follow Evennia command API**
- **Leverage Evennia's built-in systems**

### Database Patterns
- **Use AttributeProperty for persistent attributes**
- **Use Django Tags for categorical and state properties**
- **Store primitive values, not object instances**
- **Lazy initialization for complex attributes**
- **Migration-safe attribute handling**

### Testing Approach
- **Unit tests for all systems**
- **Integration tests for commands**
- **Evennia test utilities**
- **Comprehensive coverage**

---

## Project Status
- **Core systems implemented and tested**
- **Equipment system implemented with dual approach (tags + attributes)**
- **Holding system converted to tag-based approach**
- **Weight system completed**
- **All major gameplay mechanics functional**
- **Ready for content creation and refinement**
- **Equipment tests: 10/10 passing, Overall: 86/88 passing**

## Next Development Priorities
1. **Fix failing tests** (light system, weight system)
2. **Weight-based carrying capacity**
3. **Advanced crafting system**
4. **Combat mechanics**
5. **NPC and AI systems**
6. **World generation and content**
7. **Continue tag system conversion for other properties**
8. **Performance comparison between tag and attribute systems**
