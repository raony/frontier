"""Commands to manage and view skills.

Player-facing:
- skills: Show your skills with text levels.

Builder-facing (perm-limited):
- createskill <key>[=Display Name]: Create a new Skill object.
- setskill <target> = <skill>[,skill2,...] : <novice|journeyman|master>
"""

from typing import Dict, List, Tuple

from evennia import create_object, search_object
from evennia.utils.evtable import EvTable

from .command import Command


SKILL_LEVELS: Tuple[str, ...] = ("novice", "journeyman", "master")
_LEVEL_ALIASES = {
    "journey": "journeyman",
    "jr": "journeyman",
    "jm": "journeyman",
}


def find_skill_by_name(name: str):
    """Return a Skill object by key or display name, case-insensitive."""
    name_low = (name or "").strip().lower()
    if not name_low:
        return None
    # First try key match
    matches = search_object(name_low)
    for obj in matches:
        if obj.tags.get("skill", category="system"):
            return obj
    # Fallback: scan all skill-tagged objects and compare display name
    from evennia.objects.models import ObjectDB

    for obj in ObjectDB.objects.filter(db_tags__db_key="skill", db_tags__db_category="system"):
        disp = (obj.db.display_name or obj.key or "").lower()
        if disp == name_low:
            return obj
    return None


class CmdSkills(Command):
    """Show your current skills.

    Usage:
      skills

    Displays skills as text-only levels (no numbers).
    """

    key = "skills"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        # Character's skills stored as mapping: {skill_key: level_label}
        skills: Dict[str, str] = getattr(caller.db, "skills", {}) or {}

        # Collect all skill objects for nice display names
        rows: List[Tuple[str, str]] = []
        if skills:
            for skill_key, level in sorted(skills.items()):
                skill_obj = find_skill_by_name(skill_key)
                display = skill_obj.display_name if skill_obj else skill_key.title()
                # Normalize level to known label
                level_label = str(level).lower()
                # Normalize aliases
                level_label = _LEVEL_ALIASES.get(level_label, level_label)
                if level_label not in SKILL_LEVELS:
                    level_label = "novice"
                rows.append((display, level_label))

        if not rows:
            caller.msg("You have not learned any skills yet.")
            return

        table = EvTable("Skill", "Level", border="header")
        for name, level in rows:
            table.add_row(name, level)
        caller.msg(str(table))


class CmdCreateSkill(Command):
    """Create a new global Skill definition.

    Usage:
      createskill <key>[=Display Name]

    Example:
      createskill cooking=Cooking
    """

    key = "createskill"
    aliases = ["@createskill"]
    locks = "cmd:perm(Builders) or perm(Developer) or perm(Admin)"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: createskill <key>[=Display Name]")
            return
        if "=" in self.args:
            key, disp = [part.strip() for part in self.args.split("=", 1)]
        else:
            key, disp = self.args.strip(), None

        key = key.lower().strip()
        if not key:
            caller.msg("Please supply a skill key.")
            return

        # Look for existing skill with same key
        existing = find_skill_by_name(key)
        if existing and existing.key.lower() == key:
            caller.msg(f"A skill with key '{key}' already exists.")
            return

        try:
            skill = create_object("typeclasses.skills.Skill", key=key)
        except Exception as err:  # pragma: no cover - safety net
            caller.msg(f"Could not create skill: {err}")
            return

        if disp:
            skill.db.display_name = disp

        caller.msg(f"Created skill '{skill.key}' ({skill.display_name}).")


class CmdSetSkill(Command):
    """Set skill level on a target character.

    Usage:
      setskill <target> = <skill>[,<skill2>,...] : <novice|journeyman|master>

    Examples:
      setskill me = cooking : journeyman
      setskill Bob = blacksmithing,cooking : master
    """

    key = "setskill"
    aliases = ["@setskill"]
    locks = "cmd:perm(Builders) or perm(Developer) or perm(Admin)"

    def func(self):
        caller = self.caller
        if not self.args or "=" not in self.args or ":" not in self.args:
            caller.msg("Usage: setskill <target> = <skill>[,<skill2>,...] : <novice|journeyman|master>")
            return

        left, right = [part.strip() for part in self.args.split("=", 1)]
        target_name = left
        skills_part, level_part = [p.strip() for p in right.split(":", 1)]
        skill_names = [s.strip() for s in skills_part.split(",") if s.strip()]
        level = _LEVEL_ALIASES.get(level_part.lower(), level_part.lower())
        if level not in SKILL_LEVELS:
            caller.msg(f"Invalid level '{level}'. Choose one of: {', '.join(SKILL_LEVELS)}")
            return

        # Find target (allow 'me')
        if target_name.lower() in ("me", "self"):
            target = caller
        else:
            # Try local search in location, then global
            target = None
            if caller.location:
                target = caller.location.search(target_name)
            if not target:
                matches = search_object(target_name)
                target = matches[0] if matches else None
        if not target:
            caller.msg(f"Could not find target '{target_name}'.")
            return

        # Ensure skills mapping exists
        target.db.skills = target.db.skills or {}

        updated: List[str] = []
        for skill_name in skill_names:
            skill_obj = find_skill_by_name(skill_name)
            if not skill_obj:
                caller.msg(f"No such skill '{skill_name}'. Create it with 'createskill {skill_name}'.")
                continue
            target.db.skills[skill_obj.key] = level
            updated.append(skill_obj.display_name)

        if not updated:
            caller.msg("No skills updated.")
            return

        if target == caller:
            caller.msg(f"You set your skills: {', '.join(f'{name}={level}' for name in updated)}")
        else:
            caller.msg(f"Set {target.get_display_name(caller)}'s skills: {', '.join(f'{name}={level}' for name in updated)}")
