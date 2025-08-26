# Equipment Package

This package contains equipment-related systems for the Frontier MUD game.

## Contents

### holding.py
The holding system allows characters to hold items in their hands. It includes:

- **HoldableMixin**: Mixin for items that can be held
- **HoldableItem**: Base typeclass for holdable items
- **HeldItemsHandler**: Handler for managing held items
- **HolderMixin**: Mixin for entities that can hold objects
- **Exception classes**: Various exceptions for error handling

### Key Features

- Tag-based holding system using Evennia's tag system
- Support for main hand and off hand slots
- Weight-based holding restrictions
- Automatic cleanup when items leave inventory
- Display name integration showing holding status

## Usage

```python
from world.equipment import HolderMixin, HoldableMixin

# For characters that can hold items
class Character(HolderMixin, ...):
    pass

# For items that can be held
class Weapon(HoldableMixin, ...):
    pass
```

## Related Files

- `typeclasses/equipment.py` - Equipment system for wearable items
- `commands/hold.py` - Commands for holding/using items
- `commands/equip.py` - Commands for equipping wearable items
