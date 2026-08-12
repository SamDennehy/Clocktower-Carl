import os
import threading
import discord
import json
from discord.ext import commands
from random import sample
from dotenv import load_dotenv
from flask import Flask
import sqlite3

connection = sqlite3.connect("fred_stats.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_stats (
        discord_id INTEGER PRIMARY KEY,

        townsfolk_games INTEGER DEFAULT 0,
        townsfolk_wins INTEGER DEFAULT 0,

        outsider_games INTEGER DEFAULT 0,
        outsider_wins INTEGER DEFAULT 0,

        traveller_games INTEGER DEFAULT 0,
        traveller_wins INTEGER DEFAULT 0,

        minion_games INTEGER DEFAULT 0,
        minion_wins INTEGER DEFAULT 0,

        demon_games INTEGER DEFAULT 0,
        demon_wins INTEGER DEFAULT 0
    )
""")

connection.commit()

def create_player(discord_id):
    cursor.execute("""
        UPDATE player_stats
        SET townsfolk_games = townsfolk_games + 1,
            townsfolk_wins = townsfolk_wins + 1
        WHERE discord_id = ?
    """, (discord_id,))

def record_game_result(discord_id, alignment, character_type, result):
    column_prefix = f"{character_type.lower()}_"
    alignment_prefix = f"{alignment.lower()}_"

    if result == "Win":
        cursor.execute(f"""
            UPDATE player_stats
            SET {column_prefix}games = {column_prefix}games + 1,
                {column_prefix}wins = {column_prefix}wins + 1,
                {alignment_prefix}games = {alignment_prefix}games + 1,
                {alignment_prefix}wins = {alignment_prefix}wins + 1
            WHERE discord_id = ?
        """, (discord_id,))
    else:
        cursor.execute(f"""
            UPDATE player_stats
            SET {column_prefix}games = {column_prefix}games + 1,
                {alignment_prefix}games = {alignment_prefix}games + 1
            WHERE discord_id = ?
        """, (discord_id,))

    connection.commit()

def get_player_stats(discord_id):
    cursor.execute("""
        SELECT *
        FROM player_stats
        WHERE discord_id = ?
    """, (discord_id,))
    return cursor.fetchone()

townsfolk = ["steward",
  "knight",
  "chef",
  "noble",
  "investigator",
  "washerwoman",
  "clockmaker",
  "grandmother",
  "librarian",
  "shugenja",
  "pixie",
  "bountyhunter",
  "empath",
  "highpriestess",
  "sailor",
  "balloonist",
  "general",
  "preacher",
  "chambermaid",
  "villageidiot",
  "snakecharmer",
  "mathematician",
  "king",
  "dreamer",
  "fortuneteller",
  "cultleader",
  "flowergirl",
  "towncrier",
  "oracle",
  "undertaker",
  "innkeeper",
  "monk",
  "gambler",
  "acrobat",
  "exorcist",
  "lycanthrope",
  "gossip",
  "savant",
  "alsaahir",
  "engineer",
  "nightwatchman",
  "courtier",
  "seamstress",
  "philosopher",
  "huntsman",
  "professor",
  "artist",
  "slayer",
  "fisherman",
  "princess",
  "juggler",
  "soldier",
  "alchemist",
  "cannibal",
  "amnesiac",
  "farmer",
  "minstrel",
  "ravenkeeper",
  "sage",
  "choirboy",
  "banshee",
  "tealady",
  "mayor",
  "fool",
  "virgin",
  "magician",
  "poppygrower",
  "pacifist",
  "atheist"]
outsiders = ["hermit",
  "butler",
  "goon",
  "ogre",
  "lunatic",
  "drunk",
  "tinker",
  "recluse",
  "golem",
  "sweetheart",
  "plaguedoctor",
  "klutz",
  "moonchild",
  "saint",
  "barber",
  "hatter",
  "mutant",
  "politician",
  "zealot",
  "damsel",
  "snitch",
  "heretic",
  "puzzlemaster"]
minions = ["mezepheles",
  "godfather",
  "poisoner",
  "devilsadvocate",
  "spy",
  "harpy",
  "witch",
  "cerenovus",
  "fearmonger",
  "pithag",
  "psychopath",
  "assassin",
  "wizard",
  "widow",
  "xaan",
  "marionette",
  "wraith",
  "summoner",
  "eviltwin",
  "goblin",
  "boomdandy",
  "mastermind",
  "scarletwoman",
  "vizier",
  "organgrinder",
  "boffin",
  "baron"]
demons = ["yaggababble",
  "pukka",
  "lilmonsta",
  "nodashii",
  "imp",
  "shabaloth",
  "ojo",
  "kazali",
  "po",
  "zombuul",
  "vigormortis",
  "vortox",
  "legion",
  "fanggu",
  "lordoftyphon",
  "lleech",
  "alhadikhia",
  "riot",
  "leviathan"]
npcs = ["zenomancer",
  "godofug",
  "ventriloquist",
  "gardener",
  "pope",
  "hindu",
  "knaves",
  "tor",
  "stormcatcher",
  "bigwig",
  "duchess",
  "fibbin",
  "fiddler",
  "ferryman",
  "doomsayer",
  "spiritofivory",
  "sentinel",
  "toymaker",
  "buddhist",
  "hellslibrarian",
  "angel",
  "deusexfiasco",
  "revolutionary"]
characters = townsfolk + outsiders + minions + demons + npcs

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

character_emojis = {}
synced = False


@bot.event
async def on_ready():
    global character_emojis, synced

    emojis = await bot.fetch_application_emojis()

    character_emojis = {
        emoji.name: str(emoji)
        for emoji in emojis
    }

    if not synced:
        await bot.tree.sync()
        synced = True
        print("Slash commands synced.")

    print(f"Logged in successfully as {bot.user.name}")
    print(f"Loaded {len(character_emojis)} application emojis")
def build_download_script_and_preview(values):
    townsfolk_count = values[0]
    outsiders_count = values[1]
    minions_count = values[2]
    demons_count = values[3]
    npcs_count = values[4]


    preview_dict = {}
    generated_script = [
        {
        "id": "_meta",
        "author": "Fate",
        "name": "Fate's Random Script",
        }
    ]

    chosen_townsfolk = sample(townsfolk, k=min(townsfolk_count, len(townsfolk)))
    chosen_outsiders = sample(outsiders, k=min(outsiders_count, len(outsiders)))
    chosen_minions = sample(minions, k=min(minions_count, len(minions)))
    chosen_demons = sample(demons, k=min(demons_count, len(demons)))
    chosen_npcs = sample(npcs, k=min(npcs_count, len(npcs)))

    generated_script.extend(chosen_townsfolk)
    generated_script.extend(chosen_outsiders)
    generated_script.extend(chosen_minions)
    generated_script.extend(chosen_demons)
    generated_script.extend(chosen_npcs)

    preview_dict["townsfolk"] = chosen_townsfolk
    preview_dict["outsiders"] = chosen_outsiders
    preview_dict["minions"] = chosen_minions
    preview_dict["demons"] = chosen_demons
    preview_dict["npcs"] = chosen_npcs

    return [generated_script, preview_dict]

@bot.tree.command(name="generate_script")
@discord.app_commands.describe(
    townsfolk_count="Number of Townsfolk",
    outsider_count="Number of Outsiders",
    minion_count="Number of Minions",
    demon_count="Number of Demons",
    npc_count="Number of NPCs"
)
async def generate_script(
    interaction: discord.Interaction,
    townsfolk_count: int | None = None,
    outsider_count: int | None = None,
    minion_count: int | None = None,
    demon_count: int | None = None,
    npc_count: int | None = None
):
    if all(value is None for value in [
        townsfolk_count,
        outsider_count,
        minion_count,
        demon_count,
        npc_count
    ]):
        values = [13, 4, 4, 1, 0]

    elif any(value is None for value in [
        townsfolk_count,
        outsider_count,
        minion_count,
        demon_count,
        npc_count
    ]):
        await interaction.response.send_message(
            "Please provide either 0 or all 5 values.",
            ephemeral=True
        )
        return

    else:
        values = [
            townsfolk_count,
            outsider_count,
            minion_count,
            demon_count,
            npc_count
        ]

    script = build_download_script_and_preview(values)

    with open("generated_script.json", "w") as f:
        json.dump(script[0], f, indent=2)

    with open("generated_script.json", "rb") as f:
        discord_file = discord.File(
            f,
            filename="generated_script.json"
        )

        preview = script[1]

        embed = discord.Embed(
            title="🎲 Carl's Random Script",
            description="Your randomly generated script has been created!",
            color=discord.Color.purple()
        )

        for category, characters in preview.items():
            if characters:
                formatted_characters = []

                for character in characters:
                    emoji = character_emojis.get(character, "")

                    if emoji:
                        formatted_characters.append(
                            f"{emoji} {character}"
                        )

                embed.add_field(
                    name=category.capitalize(),
                    value="\n".join(formatted_characters),
                    inline=False
                )

        embed.set_footer(text="Fred's Script Generator")

        print(f"Generated script with values: {values}")

        await interaction.response.send_message(
            embed=embed,
            file=discord_file
        )

@bot.tree.command(name="choose_storyteller")
@discord.app_commands.describe(
    num="Number of storytellers to choose",
    names="Names separated by commas"
)
async def choose_storyteller(
    interaction: discord.Interaction,
    names: str,
    num: int = 1
):
    names = [
        name.strip()
        for name in names.split(",")
        if name.strip()
    ]

    if num < 1:
        await interaction.response.send_message(
            "The number of storytellers must be at least 1.",
            ephemeral=True
        )
        return

    if num > len(names):
        await interaction.response.send_message(
            "You cannot choose more storytellers than there are names.",
            ephemeral=True
        )
        return

    chosen = sample(names, k=num)

    print(f"Choosing storytellers from: {names}")

    await interaction.response.send_message(
        "Storyteller: " + ", ".join(chosen)
    )

class InputAlignment(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
    @discord.ui.select(
        placeholder="Choose an allignment",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Good"
            ),
            discord.SelectOption(
                label="Evil"
            ),
        ]
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        # Check who clicked the menu FIRST
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you fuckhead.",
                ephemeral=True
            )
            return

        discord_id = interaction.user.id

        choice = select.values[0]

        if choice == "Good":
            await interaction.response.send_message(
                "Choose a Good character type:",
                view=InputGoodType(self.user),
                ephemeral=True
            )

        elif choice == "Evil":
            await interaction.response.send_message(
                "Choose an Evil character type:",
                view=InputEvilType(self.user),
                ephemeral=True
            )
class InputGoodType(discord.ui.View):
    def __init__(self, user, alignment):
        super().__init__()
        self.user = user
        self.alignment = alignment
    @discord.ui.select(
        placeholder="Choose a character type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Townsfolk"
            ),
            discord.SelectOption(
                label="Outsider"
            ),
            discord.SelectOption(
                label="Traveller"
            ),
        ]
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        # Check who clicked the menu FIRST
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you fuckhead.",
                ephemeral=True
            )
            return
        
        choices = ", ".join(select.values)

        await interaction.response.send_message(
            "Input your game results:",
            view=InputResults(self.user),
            ephemeral=True
        )  
class InputEvilType(discord.ui.View):
    def __init__(self, user, alignment):
        super().__init__()
        self.user = user
        self.alignment = alignment
    @discord.ui.select(
        placeholder="Choose a character type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Minion"
            ),
            discord.SelectOption(
                label="Demon"
            ),
            discord.SelectOption(
                label="Traveller"
            ),
        ]
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        # Check who clicked the menu FIRST
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you fuckhead.",
                ephemeral=True
            )
            return
        
        choices = ", ".join(select.values)

        await interaction.response.send_message(
            "Input your game results:",
            view=InputResults(self.user),
            ephemeral=True
        )      
class InputResults(discord.ui.View):
    def __init__(self, user, alignment, character_type):
        super().__init__()
        self.user = user
        self.alignment = alignment
        self.character_type = character_type

    @discord.ui.select(
        placeholder="Input your game results",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Win"),
            discord.SelectOption(label="Lose"),
        ]
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True
            )
            return

        choice = select.values[0]

        await interaction.response.send_message(
            f"You chose: {choice}",
            ephemeral=True
        )

@bot.tree.command(name="log_stats")
async def log_stats(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose an Alignment",
        view=InputAlignment(interaction.user),
        ephemeral=True
    )

# Step 5: Start the bot
#def run_bot():
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable is not set!")

print("Starting Discord bot...")
bot.run(TOKEN)

#bot_thread = threading.Thread(target=run_bot)
#bot_thread.daemon = True
#bot_thread.start()