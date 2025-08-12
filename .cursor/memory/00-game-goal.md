# Game Goal — Frontier

We are building a survival-focused MUD. The primary loop is to explore, manage survival needs, and make decisions under resource pressure.

## Core survival stats (on Character)
- Thirst (0–100): 0 = fully hydrated, 100 = dehydrated (critical). Ticks up over time; faster with heat/exertion.
- Hunger (0–100): 0 = well-fed, 100 = starving (critical). Ticks up over time; faster with exertion.
- Fatigue (0–100): 0 = fresh, 100 = exhausted. Increases from movement/combat/work; recovers by resting.
- Sleepiness (0–100): 0 = well-rested, 100 = sleep-deprived. Increases with time awake; recovers by sleeping.

Thresholds and effects
- Warn at 50, strong penalties at 75, collapse/death risk at 100 (esp. thirst/hunger). Apply debuffs to movement, accuracy, and command cooldowns.

## Player actions and recovery
- Drink: reduces Thirst based on liquid quality/volume. Uses `commands/drink.py` and `commands/liquid.py`.
- Eat: reduces Hunger based on nutrition. Uses `commands/eat.py`.
- Rest: reduces Fatigue gradually; slower than sleep; usable in most rooms. Uses `commands/rest.py`.
- Sleep: reduces Sleepiness faster; ideally in safe rooms or with a `bed` object. Wake on danger.
- Move/Explore: walking between `rooms` via `exits` consumes small Fatigue and accelerates Hunger/Thirst gain.

## World requirements
- Water sources: containers, wells, rivers; `liquid` handling covers drinking/refilling.
- Food sources: edible items with nutrition/spoilage.
- Sleep spots: rooms flagged sleep-friendly or `bed` objects for better recovery.
- Exploration network: `rooms`/`exits` enabling travel; movement cost hooks on traversal.

## Implementation notes (Evennia)
- Character stats: store as `AttributeProperty` on `typeclasses.characters.Character`.
- Terminology rule: When we say "character attribute" we mean an Evennia Attribute (persisted via `AttributeProperty` / `self.db.<name>`), not a plain Python attribute.
- Periodic ticking: per-character `Script` or global ticker to increase needs every N seconds and apply thresholds/effects.
- Commands: ensure `eat`, `drink`, `rest`, `sleep` are in active CmdSets (see `commands/default_cmdsets.py`).
- Items: food/liquid objects expose `nutrition`, `hydration`, `portions`; consuming decrements and applies effects.
- Movement cost: hook movement command or `at_after_move` to add Fatigue and accelerate need gain.

## MVP success criteria
- Needs tick automatically; threshold messages and penalties applied.
- Players can find food/water and places to rest/sleep.
- Critical states (fainting/death) behave consistently and are communicated.
- Tests cover ticking, consumption, thresholds, and recovery.

Note: Keep this file first in `.cursor/memory/` so it’s read at session start to anchor design decisions.
