# Active Context — Current Work

Last updated: 2025-08-11

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
1. Add a skill system
   - Define skill model/attributes on `Character` (AttributeProperty-based), e.g., `foraging`, `cooking`, `endurance`.
   - Commands to practice/use skills; simple progression; tests.
2. Add time passage
   - Global time/ticker Script; room/environment day/night; impacts on metabolism and descriptions.
3. Test hexmap
   - Unit tests for `HexMap.load_all/save_all`, neighbor logic, and overwrite modes.
4. Start LLM integration
   - Scaffold `world/llm_service.py`, provider client (Ollama), and prompt templates; add stub tests.

Related memories: `project_context.md`, `system_patterns.md`, `evennia-how-to.md`.
