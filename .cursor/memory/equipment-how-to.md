## Equipment System

### Overview
Characters can equip items into slots and inventory now shows equipped gear. Items declare where they can be equipped via `db.equipable`.

### Slots
- head
- body
- legs
- waist
- hands
- feet

### Item requirements
- Set `obj.db.equipable = "<slot>"` (one of the slots above) to make an item wearable.

### Character storage
- `Character.db.equipment` is a dict `{slot: obj_or_None}` initialized on creation/init.
- Helpers on `Character`:
  - `get_equipped() -> dict`
  - `get_equipped_in_slot(slot) -> Optional[obj]`
  - `can_equip(obj) -> (bool, reason)`
  - `equip(obj) -> bool`
  - `unequip(slot_or_obj) -> bool`
  - `get_equipment_display_lines() -> list[str]`

### Commands
- `equip|wear <item>`: equips a carried item to its declared slot.
- `unequip|remove <slot|item>`: removes by slot or by item name.
- `inventory|inv|i`: extended to include an "Equipped" section.

### Implementation notes
- Slot constants and helpers: `typeclasses/equipment.py`.
- Item slot detection: `Object.equipable_slot` (supports `db.equipable` or `db.equipable_slot`).
- Commands in `commands/equip.py`. Registered in `commands/default_cmdsets.py`.
