## Time & Ticking

- Use Evennia gametime settings: `TIME_FACTOR = 6.0` (game runs 6× faster than real time). Optionally set `TIME_GAME_EPOCH`.
- Query and schedule via `evennia.utils.gametime` and `gametime.schedule(...)` for time-based events.
- Character metabolism defines one tick as one in-game hour: `get_metabolism_interval()` returns `(3600 / TIME_FACTOR) / metabolism`.
- Avoid custom world-clock scripts; rely on Evennia’s built-in time facilities.
# System Patterns and Conventions

## General
- Base framework: Evennia (Twisted + Django). Game code extends Evennia via typeclasses, commands, and hooks.
- Keep custom code under `commands/`, `typeclasses/`, `world/`, and `server/conf/`.
- Use Evennia import paths and settings to register new modules when moving/renaming files.

## Typeclasses
- Extend Evennia defaults, e.g. `DefaultCharacter`, `DefaultRoom`, `DefaultExit`, `DefaultObject`, `DefaultScript`.
- Create using `evennia.create_object()` to ensure correct hooks and DB connections.
- Prefer `AttributeProperty` for persistent attributes on typeclasses. When we say "character attribute" we mean an Evennia Attribute (backed by `self.db.<name>` via `AttributeProperty`), not a Python attribute.
- Use `AttributeProperty` also for non-character entities when values should be @set-able in-game (e.g., `Exit.tiredness_cost`).

## Commands and CmdSets
- Implement commands in `commands/*.py` and group them into CmdSets in `commands/default_cmdsets.py` (and others).
- Attach CmdSets on objects/characters or globally in settings as needed.
- Follow Evennia command API: `key`, `aliases`, `locks`, `help_category`, and `func()`.
- CmdSet strategy:
  - Keep `CharacterCmdSet` inheriting from Evennia defaults for baseline commands.
  - Add living-only gameplay commands to `AliveCmdSet`; add when alive, remove when dead.
  - `DeadCmdSet` should override/block commands not allowed while dead (e.g., `look`, `say`, `pose`, `whisper`, `get`, `give`, `drop`, `inventory`, `ooc`).
  - Admin maintenance commands (e.g., `resetchar`) can live in the baseline cmdset but must be permission-gated (`locks`).

## World content
- `world/prototypes.py`: Prototypes for spawning via `evennia.prototypes.spawner.spawn`.
- `world/help_entries.py`: File-based help entries; activate via `settings.FILE_HELP_ENTRY_MODULES`.
- `world/hexmap.py` + `world/models.py`: Hex map with DB persistence (`HexMap.load_all/save_all` backed by `HexTile`).

## Web/Django overrides
- Extend Evennia URL patterns: `web/urls.py`, `web/website/urls.py`, `web/webclient/urls.py`.
- Override templates/static by mirroring Evennia paths under `web/templates/` and `web/static/`.

## Settings
- `server/conf/settings.py` imports from `evennia.settings_default` and overrides selectively.
- Use `EVENNIA_DIR`, `GAME_DIR` helpers for referencing locations.

## Testing
- Tests use `evennia.utils.test_resources.EvenniaTest`.
- Run via `evennia test --settings settings.py .` from game dir.
- Prefer executing commands in tests with `obj.execute_cmd(...)`; for scripts, attach/start via handlers (e.g., `start_metabolism_script()`).

## Operations
- Init DB: `evennia migrate`
- Start: `evennia start`
- Stop/Restart: `evennia stop` / `evennia restart`
- Reload: `evennia reload`

### Local environment
- Activate the virtualenv before using the `evennia` CLI in terminal:
  - `source .venv/bin/activate`
  - Then run commands like `evennia test --settings settings.py .`

### Persistence & Restart Safety (Important)
- Do NOT store live object instances inside Evennia Attributes (e.g., `self.db.*`). Store primitive values (ids, strings) instead.
  - Example: For equipment mappings, store `object.id` (int) and resolve with `search_object(f"#{id}")` when needed.
- Avoid writing new Attributes (`self.db.* = ...`) during `at_init`, `at_object_post_creation`, or connection sync events; these can run during server start/AMP sync and cause DB errors.
  - Prefer lazy initialization: return transient defaults in getters, and only persist after the server is fully up or within explicit player actions.
- When attaching/removing CmdSets, use `persistent=True` (not `permanent=True`), per Evennia’s updated API/deprecation.
- When normalizing legacy Attribute data, do it on-demand and guard writes to avoid altering Attributes during sensitive initialization.

### Equipment System Patterns
- Slots are defined centrally in `typeclasses/equipment.py`.
- Items expose `equipable_slot` via either `obj.db.equipable` or mixins like `EquippableHead`.
- Characters maintain `db.equipment` as `{slot: object_id or None}`; never store object instances.
- Keep mapping consistent when items leave inventory (clear slot on `at_object_leave`).

## Code style
## Gameplay patterns established
- Survival needs: `hunger`, `thirst`, `tiredness`, and `metabolism` as AttributeProperties; metabolism independent of tiredness.
- Movement block when dead via `Character.at_pre_move` returning `False`.
- Exit traversal applies `tiredness_cost` (AttributeProperty) in `Exit.at_post_traverse`.
- Rest/sleep mechanics: `rest` toggles resting on; `stand` ends resting; metabolism decreases tiredness when resting.
- Food/liquid: typeclass gating (`FoodMixin`, `LiquidContainerMixin`) required for `eat`/`drink`.
- Pythonic, readable, explicit names. Keep business logic in typeclasses/commands; configuration in `server/conf`.

### Status display
- Public label helpers on `LivingMixin`: `get_hunger_label()`, `get_thirst_label()`, `get_tiredness_label()` map internal values to text-only levels.
- `status` command (in `commands/status.py`) shows: Hunger, Thirst, Tiredness using labels only (no numbers).

Related memories: `project_context.md`, `evennia-how-to.md`, `active_context.md`.
