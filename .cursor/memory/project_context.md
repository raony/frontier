# Frontier — Project Context

This repository is an Evennia-based MUD (multi-user dungeon) game using Python and Django. It follows the standard Evennia game directory layout and overrides selected systems via typeclasses, command sets, and Django URL/template extensions.

## High-level layout
- `commands/`: Custom commands and command sets (e.g., `drink.py`, `eat.py`, `rest.py`, plus default/override cmdsets).
- `typeclasses/`: Game entity classes extending Evennia defaults (e.g., `characters.py`, `rooms.py`, `exits.py`, `objects.py`, `scripts.py`).
- `server/conf/`: Server configuration (settings, session hooks, parser hooks, portal/server services, web plugins).
- `web/`: Django-side overrides for site, API, admin, and webclient; extends Evennia’s URLs, templates, and static assets.
- `world/`: Game content and systems not covered elsewhere (help entries, prototypes, models/migrations, utilities like `hexmap.py`).
- `tests/`: Unit tests using Evennia’s testing helpers (`EvenniaTest`).

## Entry points
- Run migrations: `evennia migrate`
- Start the game: `evennia start` (MUD at `localhost:4000`, web at `http://localhost:4001/`)
- Run tests: `evennia test --settings settings.py .`

## Key customizations present
- Typeclasses for `Character`, `Room`, `Exit`, `Object`, `Script` under `typeclasses/`.
- Example gameplay commands: `drink`, `eat`, `rest`, `liquid` with cmdsets in `commands/`.
- Prototypes and help entries in `world/prototypes.py` and `world/help_entries.py`.
- Web URLs extend Evennia’s defaults (`web/urls.py`, `web/website/urls.py`, `web/webclient/urls.py`); templates and static override Evennia defaults under `web/templates/` and `web/static/`.
- Settings import Evennia defaults (`server/conf/settings.py`) and override selectively.

## Documentation
- Evennia docs (latest): [https://www.evennia.com/docs/latest/](https://www.evennia.com/docs/latest/)
- Directory overview: [https://github.com/evennia/evennia/wiki/Directory-Overview](https://github.com/evennia/evennia/wiki/Directory-Overview)

Related memories: See `system_patterns.md`, `evennia-how-to.md`, `active_context.md`.
