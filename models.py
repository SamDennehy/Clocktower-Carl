class Script:
    from role_descriptions import ROLE_DESCRIPTIONS 

    def __init__(self):
        self.name = None
        self.id = None
        self.author = None
        self.characters = {}

    def append_character(self, character, category="Other"):
        character_key = character.lower().replace(" ", "")
        description = self.ROLE_DESCRIPTIONS.get(character.lower())
        if description is None:
            description = next(
                (
                    value
                    for key, value in self.ROLE_DESCRIPTIONS.items()
                    if key.replace(" ", "") == character_key
                ),
                None,
            )
        self.characters[character] = {
            "description": description,
            "category": category,
        }
    def get_characters(self):
        return self.characters

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name

    def set_id(self, id):
        self.id = id
    def get_id(self):
        return self.id

    def set_author(self, author):
        self.author = author
    def get_author(self):
        return self.author

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "author": self.author,
            "characters": [
                {
                    "name": name,
                    "description": character["description"],
                    "category": character["category"],
                }
                for name, character in self.characters.items()
            ]
        }