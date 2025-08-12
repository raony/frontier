# Active Context — Current Work

Last updated: 2025-08-12

## Goals
- Understand Frontier codebase structure and Evennia integration.
- Establish memory bank for faster future onboarding.

## Notes
- `.cursor/memory/` initialized with:
  - `project_context.md`
  - `system_patterns.md`
  - `evennia-how-to.md`
  - `active_context.md` (this file)
- Key entry points: `server/conf/settings.py`, `commands/default_cmdsets.py`, `typeclasses/characters.py`.
- Tests available under `tests/` using `EvenniaTest`.

## Next steps
1. Skill system
   - Implemented dynamic skills as objects (`typeclasses.skills.Skill`) with player-visible `skills` command and admin `createskill`/`setskill`.
   - Character stores mapping `skills: {skill_key: level_label}` and helpers on `LivingMixin`.
   - Next: Add practice/progression and tests.
2. Add time passage
   - Adopted Evennia gametime: `TIME_FACTOR = 6.0` in `server/conf/settings.py`.
   - `Character.get_metabolism_interval()` uses `TIME_FACTOR` to map 1 in-game hour to real seconds and scale by metabolism.
   - Prefer `evennia.utils.gametime` and `gametime.schedule` for time queries/events.
   - Next: Add `time` command and day/night effects using `gametime` APIs.
3. Test hexmap
   - Unit tests for `HexMap.load_all/save_all`, neighbor logic, and overwrite modes.
4. Start LLM integration
   - Scaffold `world/llm_service.py`, provider client (Ollama), and prompt templates; add stub tests.

Related memories: `project_context.md`, `system_patterns.md`, `evennia-how-to.md`.
