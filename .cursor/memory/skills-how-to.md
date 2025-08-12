# Skills System — How To

## Overview
- Skills are dynamic in-game objects (`typeclasses.skills.Skill`). Builders can create new skills at runtime; no reload required.
- Characters store their skill levels as an Attribute mapping on the `LivingMixin` via `AttributeProperty`:
  - `Character.skills`: `{skill_key: level_label}` where `level_label ∈ {novice, journeyman, master}`.
- Player command: `skills` shows text-only levels (no numbers).
- Builder commands: `createskill`, `setskill`.

## Typeclasses
- `typeclasses.skills.Skill`:
  - Tag: `skill` in category `system` (used for discovery/search).
  - `db.display_name` optional (fallback to object `key`).

## Commands
- `skills` (player): Lists skills in a table: Skill | Level.
- `createskill <key>[=Display Name]` (builders): Creates a new `Skill` object.
- `setskill <target> = <skill>[,<skill2>,...] : <novice|journeyman|master>` (builders): Sets levels.

Registered in `commands/default_cmdsets.py`:
- `AliveCmdSet`: `skills`.
- `CharacterCmdSet`: `createskill`, `setskill` (perm-gated).

## Character API
- `get_skill_level_label(skill_key) -> str`: returns normalized text level.
- `set_skill_level_label(skill_key, level_label)`: sets level (validates label).

## Patterns
- Use Tags (`skill`/`system`) for object discovery.
- Store player-state as Attributes via `AttributeProperty` for @set-ability and persistence.
- Levels are text-first; avoid exposing numbers to players.

## Examples
- Create skill: `@createskill cooking=Cooking`
- Grant: `@setskill me = cooking : journeyman`
- View: `skills`

## Future extensions
- Practice/use-based progression scripts.
- Skill checks with difficulty tiers mapping to text outcomes.
- Contextual effects (e.g., `foraging` affects food gathering yields).
