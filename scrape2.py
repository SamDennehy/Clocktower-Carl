import json

with open("roles-combined.json", "r", encoding="utf-8") as f:
    data = json.load(f)

PLAYABLE_TEAMS = {
    "townsfolk",
    "outsider",
    "minion",
    "demon",
    "traveler",
}

ROLE_DESCRIPTIONS = {
    role["name"].lower(): role["ability"]
    for role in data["character_by_id"].values()
    if role.get("team") in PLAYABLE_TEAMS
    and role.get("ability")
}

print(f"Found {len(ROLE_DESCRIPTIONS)} playable roles.")

with open("role_descriptions.py", "w", encoding="utf-8") as f:
    f.write("ROLE_DESCRIPTIONS = {\n")

    for name, description in sorted(ROLE_DESCRIPTIONS.items()):
        f.write(f"    {name!r}: {description!r},\n")

    f.write("}\n")