# Evennia How-To (Frontier)

Practical notes for working with this codebase using Evennia.

## Setup and running
- Create/upgrade DB: `evennia migrate`
- Start server: `evennia start`
- Connect: telnet `localhost:4000` or webclient `http://localhost:4001/`
- Run tests: `evennia test --settings settings.py .`

## Commands
- Add/Edit in `commands/*.py`. Example custom commands: `drink`, `eat`, `rest`, `liquid`.
- Group in CmdSets under `commands/default_cmdsets.py` or similar, and ensure they are loaded (either by character typeclass or via settings).
- Command pattern: define `key`, `aliases`, `locks`, `help_category`, and implement `func()`.

## Typeclasses
- Edit `typeclasses/*.py` to extend game entities, e.g. `Character`, `Room`, `Exit`, `Object`, `Script`.
- Use `AttributeProperty` for persistent attributes on entities (see `typeclasses/characters.py`).
- Spawn/create using `evennia.create_object()` to get proper initialization.

## World content
- Prototypes: `world/prototypes.py` for `evennia.prototypes.spawner.spawn`.
- Help entries: `world/help_entries.py` controlled by `settings.FILE_HELP_ENTRY_MODULES`.

## Web customizations
- URL inclusion: `web/urls.py` extends default Evennia patterns; same for `web/website/urls.py`, `web/webclient/urls.py`.
- Override templates/static by mirroring path under `web/templates/` and `web/static/`.

## Settings
- Base file `server/conf/settings.py` imports `evennia.settings_default`.
- Override relevant values there; reference `GAME_DIR` and `EVENNIA_DIR` when needed.

## Useful docs
- Latest docs: https://www.evennia.com/docs/latest/
- Tutorials: https://github.com/evennia/evennia/wiki/Tutorials
- Settings reference: https://www.evennia.com/docs/latest/Setup/Settings-Default.html

## Tips
- After changing command/typeclass code, reload server or use `@reload` in-game to apply changes.
- For DB resets during development (SQLite default), stop server and delete `server/evennia.db3`, then `evennia migrate`.
- Use `AttributeProperty` for any attribute you want to be @set-able in-game (e.g., `Character.metabolism`, `Exit.tiredness_cost`).
- To block dead movement, implement `Character.at_pre_move` to return `False` when `is_dead`.
- To separate living vs dead capabilities, use `AliveCmdSet` (living-only) and `DeadCmdSet` (block/override disallowed commands); keep baseline `CharacterCmdSet` inheriting Evennia defaults.

Related memories: `project_context.md`, `system_patterns.md`, `active_context.md`.
