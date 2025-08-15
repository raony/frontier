# Active Context — Current Work

Last updated: 2025-08-14

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
1. Tag System Experiment ✅ **COMPLETED**
   - Successfully implemented tag-based living/dead state system using additive tags (living_being + dead)
   - Created `LivingStateMixin` with pure tag-based approach (no AttributeProperty fallbacks)
- All tests passing (28/28) - covers state transitions, additive tags, death integration, inheritance, kill/revive commands
- Demonstrated performance benefits: fast searches, database efficiency, intuitive logic
- Created builder commands: `@kill` and `@revive` for testing living/dead state transitions
- Enhanced kill commands trigger full death process: command sets, metabolism, notifications
- Moved `time` command to AliveCmdSet (living characters only)
- Enhanced kill/revive commands support: self, me, #dbref, character names
- Updated `resetchar` command to reuse revive functionality and reset vital stats
- Refactored revive logic into reusable helper method
- **Extracted all living/death logic to `typeclasses/living.py`** - better organization and reusability
   - Next: Apply similar patterns to equipment slots, resource types, item capabilities

2. Skill system
   - Implemented dynamic skills as objects (`typeclasses.skills.Skill`) with player-visible `skills` command and admin `createskill`/`setskill`.
   - Character stores mapping `skills: {skill_key: level_label}` and helpers on `LivingMixin`.
   - Next: Add practice/progression and tests.

3. Add time passage
   - Adopted Evennia gametime: `TIME_FACTOR = 6.0` in `server/conf/settings.py`.
   - `Character.get_metabolism_interval()` uses `TIME_FACTOR` to map 1 in-game hour to real seconds and scale by metabolism.
   - Prefer `evennia.utils.gametime` and `gametime.schedule` for time queries/events.
   - Next: Add `time` command and day/night effects using `gametime` APIs.

4. Hex ↔ Room linkage
   - Rooms can link to macro hex tiles via Evennia Attribute `hex_id` (category `environment`).
   - Helper APIs on `typeclasses.rooms.Room`:
     - `set_hex_by_coords(q, r, s)`, `set_hex(tile)`, `get_hex_tile()`, `get_hex_coords()`.
     - `get_hex_weather()` maps `HexTile.terrain` to a placeholder weather string.
   - Future: Dedicated weather model per hex; expose richer macro attributes.

5. Start LLM integration
   - Scaffold `world/llm_service.py`, provider client (Ollama), and prompt templates; add stub tests.

Related memories: `project_context.md`, `system_patterns.md`, `evennia-how-to.md`.
