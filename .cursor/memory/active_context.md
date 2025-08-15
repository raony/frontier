# Active Context - Current Development

## Recent Changes

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

## Current Focus
- Weight system is now fully implemented and tested
- All existing items have appropriate default weights
- Commands are available for players and builders
- System follows Evennia patterns with persistent attributes
- All tests passing (65/65)

## Next Steps
- Consider weight-based carrying capacity limits
- Add weight to character encumbrance calculations
- Integrate weight with movement/travel systems
- Add weight-based crafting requirements

## Related Files
- `typeclasses/objects.py` - WeightMixin and base Object class
- `typeclasses/food.py` - Food weight defaults
- `typeclasses/items.py` - Equipment weight defaults
- `typeclasses/liquid.py` - Container weight defaults
- `commands/weight.py` - Weight commands
- `commands/default_cmdsets.py` - Command registration
- `tests/test_weight_system.py` - Weight system tests
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

### Holding System (Completed)
- **Hand-based holding system** with main/off hand slots
- **Holding commands**: `hold`, `release`
- **HoldableMixin** for items that can be held
- **HeldItemsHandler** for managing held items

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
- **Weight system completed**
- **All major gameplay mechanics functional**
- **Ready for content creation and refinement**
- **All tests passing (65/65)**

## Next Development Priorities
1. **Weight-based carrying capacity**
2. **Advanced crafting system**
3. **Combat mechanics**
4. **NPC and AI systems**
5. **World generation and content**
