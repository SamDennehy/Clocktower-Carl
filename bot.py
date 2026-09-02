import asyncio
import json
import os
from random import sample
import time
import tempfile

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg import Connection
import edge_tts

logs = []

def add_log(message):
    logs.append(f"{message} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(message)

def get_logs():
    return logs

load_dotenv()

def reconnect_failed(pool):
    add_log(f"DATABASE RECONNECT FAILED: {pool.get_stats()}")


def create_database_pool():
    return ConnectionPool(
        conninfo=os.getenv("DATABASE_URL"),
        min_size=1,
        max_size=5,
        max_idle=300,
        max_lifetime=300,
        reconnect_timeout=300,
        reconnect_failed=reconnect_failed,
        check=ConnectionPool.check_connection,
    )


def initialize_database_schema():
    active_pool = getattr(pool, "_pool", pool)
    with active_pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS player_stats (
                    discord_id BIGINT PRIMARY KEY,

                    townsfolk_games INTEGER DEFAULT 0,
                    townsfolk_wins INTEGER DEFAULT 0,

                    outsider_games INTEGER DEFAULT 0,
                    outsider_wins INTEGER DEFAULT 0,

                    traveller_good_games INTEGER DEFAULT 0,
                    traveller_good_wins INTEGER DEFAULT 0,

                    traveller_evil_games INTEGER DEFAULT 0,
                    traveller_evil_wins INTEGER DEFAULT 0,

                    minion_games INTEGER DEFAULT 0,
                    minion_wins INTEGER DEFAULT 0,

                    demon_games INTEGER DEFAULT 0,
                    demon_wins INTEGER DEFAULT 0,

                    trouble_brewing_games INTEGER DEFAULT 0,
                    trouble_brewing_wins INTEGER DEFAULT 0,

                    bad_moon_rising_games INTEGER DEFAULT 0,
                    bad_moon_rising_wins INTEGER DEFAULT 0,

                    sects_and_violets_games INTEGER DEFAULT 0,
                    sects_and_violets_wins INTEGER DEFAULT 0,

                    teenysville_games INTEGER DEFAULT 0,
                    teenysville_wins INTEGER DEFAULT 0,

                    custom_games INTEGER DEFAULT 0,
                    custom_wins INTEGER DEFAULT 0,

                    total_games INTEGER DEFAULT minion_games + demon_games + traveller_evil_games + townsfolk_games + outsider_games + traveller_good_games,
                    total_wins INTEGER DEFAULT minion_wins + demon_wins + traveller_evil_wins + townsfolk_wins + outsider_wins + traveller_good_wins,

                    whale_buffet_games INTEGER DEFAULT 0,
                    whale_buffet_wins INTEGER DEFAULT 0
                )
                """
            )

            connection.commit()


class DatabasePoolWrapper:
    def __init__(self):
        self._pool = create_database_pool()

    def reset(self):
        try:
            if hasattr(self._pool, "close"):
                self._pool.close()
        except Exception as exc:
            add_log(f"Database pool close failed during reset: {exc}")

        self._pool = create_database_pool()
        initialize_database_schema()

    def connection(self, *args, **kwargs):
        try:
            return self._pool.connection(*args, **kwargs)
        except Exception as exc:
            add_log(f"Database connection failed; resetting pool: {exc}")
            self.reset()
            return self._pool.connection(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pool, name)


def reset_database_pool():
    global pool
    if hasattr(pool, "reset"):
        pool.reset()
    else:
        pool = DatabasePoolWrapper()


pool = DatabasePoolWrapper()
initialize_database_schema()


def player_exists(discord_id):
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM player_stats
                WHERE discord_id = %s
                """,
                (discord_id,),
            )

            return cursor.fetchone() is not None


def create_player(discord_id):
    add_log(f"Creating player record for Discord ID {discord_id}")
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO player_stats (discord_id)
                VALUES (%s)
                ON CONFLICT (discord_id) DO NOTHING
                """,
                (discord_id,),
            )

            connection.commit()


def record_game_result(discord_id, alignment, character_type, script, result):
    create_player(discord_id)

    character_type_prefix = f"{character_type.lower()}_"
    script_prefix = f"{script.lower().replace(' ', '_')}_"

    with pool.connection() as connection:
        with connection.cursor() as cursor:
            if result == "Win":
                cursor.execute(
                    f"""
                    UPDATE player_stats
                    SET {character_type_prefix}games =
                            {character_type_prefix}games + 1,
                        {character_type_prefix}wins =
                            {character_type_prefix}wins + 1,
                        {script_prefix}games =
                            {script_prefix}games + 1,
                        {script_prefix}wins =
                            {script_prefix}wins + 1
                    WHERE discord_id = %s
                    """,
                    (discord_id,),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE player_stats
                    SET {character_type_prefix}games =
                            {character_type_prefix}games + 1,
                        {script_prefix}games =
                            {script_prefix}games + 1
                    WHERE discord_id = %s
                    """,
                    (discord_id,),
                )

            connection.commit()

    add_log((
        f"Recorded game result for Discord ID {discord_id}: "
        f"{alignment} {character_type} - {result} - {script_dict.get(script, script)}"
    ))
def get_player_stats(discord_id):
    add_log(f"Fetching stats for Discord ID {discord_id}")
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM player_stats
                WHERE discord_id = %s
                """,
                (discord_id,),
            )

            return cursor.fetchone()


scripts = [
    "trouble_brewing",
    "bad_moon_rising",
    "sects_and_violets",
    "teenysville",
    "whale_buffet",
]

script_dict = {
    "trouble_brewing": "Trouble Brewing",
    "bad_moon_rising": "Bad Moon Rising",
    "sects_and_violets": "Sects & Violets",
    "teenysville": "Teenysville",
    "custom": "Custom Script",
    "whale_buffet": "Whale Buffet",
}

townsfolk = [
    "steward",
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
    "atheist",
]
outsiders = [
    "hermit",
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
    "puzzlemaster",
]
minions = [
    "mezepheles",
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
    "baron",
]
demons = [
    "yaggababble",
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
    "leviathan",
]
npcs = [
    "zenomancer",
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
    "revolutionary",
]
characters = townsfolk + outsiders + minions + demons + npcs

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    activity=discord.Game(name="Blood on the Clocktower"),
)

bot_loop = None

character_emojis = {}
synced = False


@tasks.loop(minutes=3)
async def check_database():
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

        add_log("Database connection OK")
    except Exception as e:
        add_log(f"Database connection check failed: {e}")
        reset_database_pool()
@bot.event
async def on_ready():
    global bot_loop
    bot_loop = asyncio.get_running_loop()
    add_log("bot_loop set to: " + str(bot_loop))

    global character_emojis

    add_log("Bot is ready and connected to Discord.")

    add_log("READY EVENT FIRED")

    add_log("API REQUEST: fetch_application_emojis()")
    emojis = await bot.fetch_application_emojis()
    add_log(f"API RESPONSE: received {len(emojis)} application emojis")

    character_emojis = {emoji.name: str(emoji) for emoji in emojis}

    add_log("API REQUEST: bot.tree.sync()")
    synced_commands = await bot.tree.sync()
    add_log(f"API RESPONSE: synced {len(synced_commands)} commands")

    add_log(f"Logged in successfully as {bot.user.name}")

    if not check_database.is_running():
        check_database.start()


def build_download_script_and_preview(values):
    add_log(f"Building download script and preview with values: {values}")
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


@bot.tree.command(
    name="generate_script",
    description="Generate a random script with specified counts of each character type",
)
@discord.app_commands.describe(
    townsfolk_count="Number of Townsfolk",
    outsider_count="Number of Outsiders",
    minion_count="Number of Minions",
    demon_count="Number of Demons",
    npc_count="Number of NPCs",
)
async def generate_script(
    interaction: discord.Interaction,
    townsfolk_count: int | None = None,
    outsider_count: int | None = None,
    minion_count: int | None = None,
    demon_count: int | None = None,
    npc_count: int | None = None,
):
    add_log(f"Generating script with counts - Townsfolk: {townsfolk_count}, Outsiders: {outsider_count}, Minions: {minion_count}, Demons: {demon_count}, NPCs: {npc_count}")
    values = [
        townsfolk_count if townsfolk_count is not None else 13,
        outsider_count if outsider_count is not None else 4,
        minion_count if minion_count is not None else 4,
        demon_count if demon_count is not None else 1,
        npc_count if npc_count is not None else 0,
    ]

    script = build_download_script_and_preview(values)

    with open("generated_script.json", "w") as f:
        json.dump(script[0], f, indent=2)

    with open("generated_script.json", "rb") as f:
        discord_file = discord.File(f, filename="generated_script.json")

        preview = script[1]

        embed = discord.Embed(
            title="🎲 Carl's Random Script",
            description="Your randomly generated script has been created!",
            color=discord.Color.purple(),
        )

        for category, characters in preview.items():
            if characters:
                formatted_characters = []

                for character in characters:
                    emoji = character_emojis.get(character, "")

                    if emoji:
                        formatted_characters.append(f"{emoji} {character}")

                embed.add_field(
                    name=category.capitalize(),
                    value="\n".join(formatted_characters),
                    inline=False,
                )

        embed.set_footer(text="Carl's Script Generator")

        add_log(f"Generated script with values: {values}")
        await interaction.response.send_message(embed=embed, file=discord_file)


@bot.tree.command(
    name="choose_storyteller",
    description="Randomly choose a storyteller from a list of names (separate names by commas)",
)
@discord.app_commands.describe(
    num="Number of storytellers to choose",
    names="Names separated by commas",
)
async def choose_storyteller(
    interaction: discord.Interaction,
    names: str,
    num: int = 1,
):
    add_log(f"Choosing {num} storytellers from names: {names}")
    names = [name.strip() for name in names.split(",") if name.strip()]

    if num < 1:
        await interaction.response.send_message(
            "The number of storytellers must be at least 1.",
            ephemeral=True,
        )
        return

    if num > len(names):
        await interaction.response.send_message(
            "You cannot choose more storytellers than there are names.",
            ephemeral=True,
        )
        return

    chosen = sample(names, k=num)

    add_log(f"Choosing storytellers from: {names}")
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
            discord.SelectOption(label="Good"),
            discord.SelectOption(label="Evil"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        choice = select.values[0]

        if choice == "Good":
            await interaction.response.send_message(
                "Choose a Good character type:",
                view=InputGoodType(self.user, choice),
                ephemeral=True,
            )

        elif choice == "Evil":
            await interaction.response.send_message(
                "Choose an Evil character type:",
                view=InputEvilType(self.user, choice),
                ephemeral=True,
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
            discord.SelectOption(label="Townsfolk"),
            discord.SelectOption(label="Outsider"),
            discord.SelectOption(label="Traveller", value="Traveller_Good"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        choice = select.values[0]

        await interaction.response.send_message(
            "What script did you play with?",
            view=InputScript(self.user, self.alignment, choice, False, None),
            ephemeral=True,
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
            discord.SelectOption(label="Minion"),
            discord.SelectOption(label="Demon"),
            discord.SelectOption(label="Traveller", value="Traveller_Evil"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        choice = select.values[0]

        await interaction.response.send_message(
            "What script did you play with?",
            view=InputScript(self.user, self.alignment, choice, False, None),
            ephemeral=True,
        )

class InputScript(discord.ui.View):
    def __init__(self, user, alignment, character_type, massBool, discord_id_role_dict):
        super().__init__()
        self.user = user
        self.alignment = alignment
        self.character_type = character_type
        self.massBool = massBool
        self.discord_id_role_dict = discord_id_role_dict

    @discord.ui.select(
        placeholder="Choose a character type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Trouble Brewing", value="trouble_brewing"),
            discord.SelectOption(label="Bad Moon Rising", value="bad_moon_rising"),
            discord.SelectOption(label="Sects & Violets", value="sects_and_violets"),
            discord.SelectOption(label="Teenysville", value="teenysville"),
            discord.SelectOption(label="Whale Buffet", value="whale_buffet"),
            discord.SelectOption(label="Custom Script", value="custom"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        choice = select.values[0]

        if self.massBool:
            await interaction.response.send_message(
                "Input your game results:",
                view=InputMassResults(self.user, self.discord_id_role_dict, choice),
                ephemeral=True,
            )

        await interaction.response.send_message(
            "Input your game results:",
            view=InputResults(self.user, self.alignment, self.character_type, choice),
            ephemeral=True,
        )

class InputResults(discord.ui.View):
    def __init__(self, user, alignment, character_type, script):
        super().__init__()
        self.user = user
        self.alignment = alignment
        self.character_type = character_type
        self.script = script

    @discord.ui.select(
        placeholder="Input your game results",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Win"),
            discord.SelectOption(label="Lose"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        result = select.values[0]

        await interaction.response.send_message(
            f"You chose: {self.alignment.title()} {self.character_type.title()} played on: {script_dict.get(self.script, self.script)}, with result: {result.title()}. Is this correct?",
            view=ConfirmInput(self.user, self.alignment, self.character_type, self.script, result),
            ephemeral=True,
        )

class ConfirmInput(discord.ui.View):
    def __init__(self, user, alignment, character_type, script, result):
        super().__init__()
        self.user = user
        self.alignment = alignment
        self.character_type = character_type
        self.script = script
        self.result = result

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This button isn't for you.",
                ephemeral=True,
            )
            return

        record_game_result(
            interaction.user.id,
            self.alignment,
            self.character_type,
            self.script,
            self.result,
        )

        await interaction.response.send_message(
            f"{interaction.user.mention}, your game results have been recorded.",
            ephemeral=False,
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This button isn't for you.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"{interaction.user.mention}, your game results have been recorded.",
            ephemeral=True,
        )


@bot.tree.command(name="log_stats", description="Log your personal game stats")
async def log_stats(interaction: discord.Interaction):
    add_log(f"Logging stats for Discord ID {interaction.user.id}")
    await interaction.response.send_message(
        "Choose an Alignment",
        view=InputAlignment(interaction.user),
        ephemeral=True,
    )


@bot.tree.command(name="display_stats", description="Display your personal game stats")
async def display_stats(interaction: discord.Interaction):
    discord_id = interaction.user.id
    add_log(f"Displaying stats for Discord ID {discord_id}")
    if not player_exists(discord_id):
        await interaction.response.send_message(
            "You have no recorded stats.",
            ephemeral=True,
        )
        return

    stats = get_player_stats(discord_id)

    townsfolk_games = stats[1]
    townsfolk_wins = stats[2]

    outsider_games = stats[3]
    outsider_wins = stats[4]

    traveller_good_games = stats[5]
    traveller_good_wins = stats[6]

    traveller_evil_games = stats[7]
    traveller_evil_wins = stats[8]

    minion_games = stats[9]
    minion_wins = stats[10]

    demon_games = stats[11]
    demon_wins = stats[12]

    trouble_brewing_games = stats[13]
    trouble_brewing_wins = stats[14]

    bad_moon_rising_games = stats[15]
    bad_moon_rising_wins = stats[16]

    sects_and_violets_games = stats[17]
    sects_and_violets_wins = stats[18]

    teenysville_games = stats[19]
    teenysville_wins = stats[20]

    custom_games = stats[21]
    custom_wins = stats[22]

    overall_games = stats[23]
    overall_wins = stats[24]

    whale_buffet_games = stats[25]
    whale_buffet_wins = stats[26]

    good_games = townsfolk_games + outsider_games + traveller_good_games
    good_wins = townsfolk_wins + outsider_wins + traveller_good_wins

    evil_games = minion_games + demon_games + traveller_evil_games
    evil_wins = minion_wins + demon_wins + traveller_evil_wins

    good_win_rate = (good_wins / good_games) * 100 if good_games > 0 else 0
    evil_win_rate = (evil_wins / evil_games) * 100 if evil_games > 0 else 0
    overall_win_rate = (overall_wins / overall_games) * 100 if overall_games > 0 else 0
    townsfolk_win_rate = (townsfolk_wins / townsfolk_games) * 100 if townsfolk_games > 0 else 0
    outsider_win_rate = (outsider_wins / outsider_games) * 100 if outsider_games > 0 else 0
    traveller_good_win_rate = (traveller_good_wins / traveller_good_games) * 100 if traveller_good_games > 0 else 0
    traveller_evil_win_rate = (traveller_evil_wins / traveller_evil_games) * 100 if traveller_evil_games > 0 else 0
    minion_win_rate = (minion_wins / minion_games) * 100 if minion_games > 0 else 0
    demon_win_rate = (demon_wins / demon_games) * 100 if demon_games > 0 else 0
    trouble_brewing_win_rate = (trouble_brewing_wins / trouble_brewing_games) * 100 if trouble_brewing_games > 0 else 0
    bad_moon_rising_win_rate = (bad_moon_rising_wins / bad_moon_rising_games) * 100 if bad_moon_rising_games > 0 else 0
    sects_and_violets_win_rate = (sects_and_violets_wins / sects_and_violets_games) * 100 if sects_and_violets_games > 0 else 0
    teenysville_win_rate = (teenysville_wins / teenysville_games) * 100 if teenysville_games > 0 else 0
    custom_win_rate = (custom_wins / custom_games) * 100 if custom_games > 0 else 0
    whale_buffet_win_rate = (whale_buffet_wins / whale_buffet_games) * 100 if whale_buffet_games > 0 else 0
    add_log(f"Calculating win rates for Discord ID {interaction.user.id}")
    embed = discord.Embed(
        title=f"{interaction.user.name}'s Game Stats",
        color=discord.Color.purple(),
    )

    embed.add_field(
        name=character_emojis.get("custom", "") + "All Games",
        value=f"Games: {overall_games}, Wins: {overall_wins},\n Win Rate: {overall_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("good", "") + "Good Games",
        value=f"Games: {good_games}, Wins: {good_wins},\n Win Rate: {good_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("evil", "") + "Evil Games",
        value=f"Games: {evil_games}, Wins: {evil_wins},\n Win Rate: {evil_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("townsfolk", "") + "Townsfolk",
        value=f"Games: {townsfolk_games}, Wins: {townsfolk_wins},\n Win Rate: {townsfolk_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("outsider", "") + "Outsider",
        value=f"Games: {outsider_games}, Wins: {outsider_wins},\n Win Rate: {outsider_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("traveller_g", "") + "Traveller (Good)",
        value=f"Games: {traveller_good_games}, Wins: {traveller_good_wins},\n Win Rate: {traveller_good_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("traveller_e", "") + "Traveller (Evil)",
        value=f"Games: {traveller_evil_games}, Wins: {traveller_evil_wins},\n Win Rate: {traveller_evil_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("minion", "") + "Minion",
        value=f"Games: {minion_games}, Wins: {minion_wins},\n Win Rate: {minion_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("demon", "") + "Demon",
        value=f"Games: {demon_games}, Wins: {demon_wins},\n Win Rate: {demon_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("trouble_brewing", "") + "Trouble Brewing",
        value=f"Games: {trouble_brewing_games}, Wins: {trouble_brewing_wins},\n Win Rate: {trouble_brewing_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("bad_moon_rising", "") + "Bad Moon Rising",
        value=f"Games: {bad_moon_rising_games}, Wins: {bad_moon_rising_wins},\n Win Rate: {bad_moon_rising_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("sects_and_violets", "") + "Sects and Violets",
        value=f"Games: {sects_and_violets_games}, Wins: {sects_and_violets_wins},\n Win Rate: {sects_and_violets_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("custom_script", "") + "Custom",
        value=f"Games: {custom_games}, Wins: {custom_wins},\n Win Rate: {custom_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name=character_emojis.get("custom_script", "") + "Teenysville",
        value=f"Games: {teenysville_games}, Wins: {teenysville_wins},\n Win Rate: {teenysville_win_rate:.2f}%",
        inline=True,
    )

    embed.add_field(
        name="🐋" + "Whale Buffet",
        value=f"Games: {whale_buffet_games}, Wins: {whale_buffet_wins},\n Win Rate: {whale_buffet_win_rate:.2f}%",
        inline=True,
    )

    add_log(f"Sending stats embed for Discord ID {interaction.user.id}")
    await interaction.response.send_message(embed=embed, ephemeral=False)


async def create_leaderboard_embed(top_players, title, members=None):
    add_log(f"Creating leaderboard embed for {title} with {len(top_players)} players")
    embed = discord.Embed(
        title=f"🏆 Leaderboard - {title}",
        color=discord.Color.gold(),
    )
    leaderboard = ""

    for position, player in enumerate(top_players, start=1):
        if members is not None:
            user = members.get(player[0])
            name = user.display_name if user is not None else "Unknown User"
        else:
            name = "Unknown User"

        if player[2] > 0:
            win_rate = player[1] / player[2] * 100
        else:
            win_rate = 0

        if position == 1:
            rank = "🥇"
        elif position == 2:
            rank = "🥈"
        elif position == 3:
            rank = "🥉"
        else:
            rank = f"**{position}.**"

        leaderboard += (
            f"{rank} **{name}** - "
            f"{win_rate:.2f}% "
            f"({player[1]}/{player[2]})\n"
        )

    embed.add_field(name="Top Players", value=leaderboard, inline=False)

    return embed


async def get_win_leaderboard(members):
    add_log("Fetching overall leaderboard")
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    discord_id,
                    townsfolk_wins + outsider_wins + traveller_good_wins +
                    minion_wins + demon_wins + traveller_evil_wins AS total_wins,
                    townsfolk_games + outsider_games + traveller_good_games +
                    traveller_evil_games + minion_games + demon_games AS total_games
                FROM player_stats
                WHERE townsfolk_games + outsider_games + traveller_good_games +
                      traveller_evil_games + minion_games + demon_games >= 5
                ORDER BY
                    (townsfolk_wins + outsider_wins + traveller_good_wins +
                    minion_wins + demon_wins + traveller_evil_wins)::float
                    /
                    NULLIF(
                        townsfolk_games + outsider_games + traveller_good_games +
                        traveller_evil_games + minion_games + demon_games,
                        0
                    ) DESC NULLS LAST,
                    townsfolk_games + outsider_games + traveller_good_games +
                    traveller_evil_games + minion_games + demon_games DESC NULLS LAST
                LIMIT 50
                """
            )

            candidates = cursor.fetchall()

    top_players = []

    for discord_id, wins, games in candidates:
        member = members.get(discord_id)
        add_log(f"API REQUEST: get_member() for Discord ID {discord_id}")
        if member is not None:
            top_players.append((discord_id, wins, games))

        if len(top_players) == 10:
            break

    return top_players

async def get_good_leaderboard(members):
    add_log("Fetching good leaderboard")
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    discord_id,
                    townsfolk_wins + outsider_wins + traveller_good_wins AS total_wins,
                    townsfolk_games + outsider_games + traveller_good_games AS total_games
                FROM player_stats
                WHERE townsfolk_games + outsider_games + traveller_good_games >= 5
                ORDER BY
                    (townsfolk_wins + outsider_wins + traveller_good_wins)::float
                    /
                    NULLIF(
                        townsfolk_games + outsider_games + traveller_good_games,
                        0
                    ) DESC NULLS LAST,
                    townsfolk_games + outsider_games + traveller_good_games DESC NULLS LAST
                LIMIT 50
                """
            )

            candidates = cursor.fetchall()

    top_players = []

    for discord_id, wins, games in candidates:
        add_log(f"API REQUEST: get_member() for Discord ID {discord_id}")
        member = members.get(discord_id)

        if member is not None:
            top_players.append((discord_id, wins, games))

        if len(top_players) == 10:
            break

    return top_players

async def get_evil_leaderboard(members):
    add_log("Fetching evil leaderboard")
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    discord_id,
                    minion_wins + demon_wins + traveller_evil_wins AS total_wins,
                    traveller_evil_games + minion_games + demon_games AS total_games
                FROM player_stats
                WHERE traveller_evil_games + minion_games + demon_games >= 5
                ORDER BY
                    (minion_wins + demon_wins + traveller_evil_wins)::float
                    /
                    NULLIF(traveller_evil_games + minion_games + demon_games,
                        0
                    ) DESC NULLS LAST,
                    traveller_evil_games + minion_games + demon_games DESC NULLS LAST
                LIMIT 50
                """
            )

            candidates = cursor.fetchall()

    top_players = []

    for discord_id, wins, games in candidates:
        add_log(f"API REQUEST: get_member() for Discord ID {discord_id}")
        member = members.get(discord_id)

        if member is not None:
            top_players.append((discord_id, wins, games))

        if len(top_players) == 10:
            break

    return top_players


class LeaderboardView(discord.ui.View):
    def __init__(self, user, members):
        super().__init__(timeout=300)
        self.user = user
        self.members = members

    @discord.ui.select(
        placeholder="Choose a leaderboard",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Overall", value="overall", description="All Games"),
            discord.SelectOption(label="Good", value="good", description="Good Games"),
            discord.SelectOption(label="Evil", value="evil", description="Evil Games"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This leaderboard isn't for you.",
                ephemeral=True,
            )
            return

        choice = select.values[0]
        add_log(f"Selected leaderboard: {choice}")
        if choice == "overall":
            top_players = await get_win_leaderboard(self.members)
            title = "Top 10 Players by Overall Win Rate (minimum 5 games)"

        elif choice == "good":
            top_players = await get_good_leaderboard(self.members)
            title = "Top 10 Players by Good Win Rate (minimum 5 games)"
        elif choice == "evil":
            top_players = await get_evil_leaderboard(self.members)
            title = "Top 10 Players by Evil Win Rate (minimum 5 games)"

        add_log(f"Creating leaderboard embed for {title} with {len(top_players)} players")
        add_log(f"CHOICE: {choice}")
        add_log(f"TOP PLAYERS: {top_players}")
        if not top_players:
            await interaction.response.edit_message(
                content="No players have recorded enough games for this leaderboard.",
                embed=None,
                view=self,
            )
            return

        embed = await create_leaderboard_embed(top_players, title, self.members)

        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(
    name="leaderboard",
    description="Display the top 10 players in the server by win rate",
)
async def leaderboard(interaction: discord.Interaction):
    add_log(f"Displaying leaderboard for Discord ID {interaction.user.id}")
    members = {member.id: member for member in interaction.guild.members}

    top_players = await get_win_leaderboard(members)

    if not top_players:
        await interaction.response.send_message(
            "No players have recorded enough games for the leaderboard.",
            ephemeral=True,
        )
        return

    embed = await create_leaderboard_embed(
        top_players,
        "Top 10 Players by Overall Win Rate (minimum 5 games)",
        members,
    )

    await interaction.response.send_message(
        embed=embed,
        view=LeaderboardView(interaction.user, members),
        ephemeral=False,
    )


@bot.tree.command(
    name="timer",
    description="Set a timer in seconds for the bot to send a message when it ends",
)
async def timer(interaction: discord.Interaction, seconds: int):
    add_log(f"Setting timer for {seconds} seconds for Discord ID {interaction.user.id}")
    await interaction.response.send_message(
        f"Timer set for {seconds} seconds.",
        ephemeral=False,
    )
    await asyncio.sleep(seconds)
    await interaction.channel.send(f"{interaction.user.mention}, your timer has ended!")


class JSONModal(discord.ui.Modal, title="Import BOTC JSON"):
    def __init__(self, user):
        super().__init__()
        self.user = user

    json_input = discord.ui.TextInput(
        label="Paste your Game State JSON:",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        add_log(f"Submitting JSON for Discord ID {interaction.user.id}")
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        try:
            data = json.loads(self.json_input.value)
        except json.JSONDecodeError:
            await interaction.response.send_message(
                "That isn't valid JSON.",
                ephemeral=True,
            )
            return

        discord_id_role_dict = {}
        players = data["players"]
        for player in players:
            discord_id = player.get("pronouns").strip() if player.get("pronouns") else None
            role = player.get("role").strip() if player.get("role") else None
            try:
                discord_id = int(discord_id)
            except (ValueError, TypeError):
                discord_id = None

            if discord_id and role:
                discord_id_role_dict[discord_id] = role

        await interaction.response.send_message(
            "Select the script you played with:",
            view=InputScript(self.user, None, None, True, discord_id_role_dict),
            ephemeral=True,
        )

class Player:
    def __init__(self, discord_id, alignment, character_type, script, result):
        self.discord_id = discord_id
        self.alignment = alignment
        self.character_type = character_type
        self.script = script
        self.result = result

class InputMassResults(discord.ui.View):
    def __init__(self, user, discord_id_role_dict, script):
        super().__init__()
        self.user = user
        self.discord_id_role_dict = discord_id_role_dict
        self.script = script

    @discord.ui.select(
        placeholder="Which alignment won?",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Good"),
            discord.SelectOption(label="Evil"),
        ],
    )
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This menu isn't for you.",
                ephemeral=True,
            )
            return

        players = []
        winner = select.values[0]
        for discord_id, role in self.discord_id_role_dict.items():
            if discord_id and role:
                category = ""
                alignment = ""
                if role in townsfolk:
                    category = "townsfolk"
                    alignment = "good"
                elif role in outsiders:
                    category = "outsider"
                    alignment = "good"
                elif role in minions:
                    category = "minion"
                    alignment = "evil"
                elif role in demons:
                    category = "demon"
                    alignment = "evil"

                try:
                    member = interaction.guild.get_member(discord_id)

                    if member is None:
                        member = await interaction.guild.fetch_member(discord_id)

                    player = Player(
                        discord_id=discord_id,
                        alignment=alignment,
                        character_type=category,
                        script=self.script,
                        result="Win" if alignment.lower() == winner.lower() else "Lose",
                    )

                    players.append(player)

                except discord.NotFound:
                    pass

        confirm_string = ""
        for player in players:
            confirm_string += f"<@{player.discord_id}> played as {player.character_type} ({player.alignment}) in {script_dict.get(player.script, player.script)} and {'won' if player.result.lower() == 'win' else 'lost'}.\n"
        confirm_string += f"{winner} team won the game. Is this correct?"
        await interaction.response.send_message(
            confirm_string,
            view=ConfirmMassInput(self.user, players),
            ephemeral=True,
        )


class ConfirmMassInput(discord.ui.View):
    def __init__(self, user, players):
        super().__init__()
        self.user = user
        self.players = players

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This button isn't for you.",
                ephemeral=True,
            )
            return

        for player in self.players:
            record_game_result(
                player.discord_id,
                player.alignment,
                player.character_type,
                player.script,
                player.result,
            )

        await interaction.response.send_message(
            f"{interaction.user.mention}, your mass game results have been recorded.",
            ephemeral=False,
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This button isn't for you.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"{interaction.user.mention}, your game results have not been recorded.",
            ephemeral=True,
        )


async def mass_log_stats(interaction: discord.Interaction):
    add_log(f"Logging mass stats for Discord ID {interaction.user.id}")
    await interaction.response.send_modal(JSONModal(interaction.user))


@bot.tree.command(
    name="help",
    description="Get help with using the bot",
)
async def help_command(interaction: discord.Interaction):
    help_text = (
        "Here are the commands you can use:\n"
        "- `/generate_script <townsfolk>, <outsiders>, <minions>, <demons>, <npcs>`: Generate a random script for your game\n"
        "- `/choose_storyteller <amount>`: Choose a storyteller for your game\n"
        "- `/timer <seconds>`: Set a timer in seconds for the bot to send a message when it ends\n"
        "- `/log_stats`: Log your personal game stats\n"
        "- `/leaderboard`: Display the top 10 players in the server by win rate\n"
        "- `/display_stats`: Display your personal game stats\n"
    )
    await interaction.response.send_message(help_text, ephemeral=True)


async def send_message_to_channel(channel_id: int, message: str):
    channel = bot.get_channel(channel_id)

    if channel is None:
        add_log(f"Channel with ID {channel_id} not found.")
        return False

    try:
        await channel.send(message)
        add_log(f"Sent message to channel ID {channel_id}: {message}")
        return True
    except discord.DiscordException as e:
        add_log(f"Failed to send message to channel ID {channel_id}: {e}")
        return False

@bot.command()
async def echo(ctx, channel_id: int, *, message: str):
    success = await send_message_to_channel(channel_id, message)

    if not success:
        await ctx.send("I couldn't find that channel.")
    else:
        await ctx.send(f"Echoed message to channel ID: {channel_id}.")

async def join_voice_channel(channel_id: int):
    channel = bot.get_channel(channel_id)

    if channel is None:
        add_log(f"Channel with ID {channel_id} not found.")
        return False

    if not isinstance(channel, discord.VoiceChannel):
        add_log(f"Channel with ID {channel_id} is not a voice channel.")
        return False

    # Leave any voice channel the bot is currently in
    for voice_client in bot.voice_clients:
        if voice_client.is_connected():
            add_log(f"Leaving current voice channel: {voice_client.channel.name}")
            await voice_client.disconnect()

    try:
        await channel.connect()
        add_log(f"Joined voice channel ID {channel_id}.")
        return True

    except discord.DiscordException as e:
        add_log(f"Failed to join voice channel: {e}")
        return False

@bot.command()
async def joinvc(ctx, channel_id: int):
    success = await join_voice_channel(channel_id)

    if not success:
        await ctx.send("I couldn't join that voice channel.")
    else:
        await ctx.send(f"Joined channel ID: {channel_id}.")

async def leave_voice_channel():
    print("Guilds:", bot.guilds)
    print("Voice clients:", bot.voice_clients)

    for vc in bot.voice_clients:
        print("Voice client guild:", vc.guild)
        print("Voice channel:", vc.channel)

    if not bot.voice_clients:
        add_log("No voice clients found.")
        return False

    voice_client = bot.voice_clients[0]

    try:
        await voice_client.disconnect()
        add_log("Bot left the voice channel.")
        return True

    except discord.DiscordException as e:
        add_log(f"Failed to leave voice channel: {e}")
        return False

@bot.command()
async def leavevc(ctx):
    success = await leave_voice_channel()

    if not success:
        await ctx.send("I couldn't leave that voice channel.")
    else:
        await ctx.send("Left the voice channel.")

async def generate_tts(text):
    """Generate TTS audio file in a unique temp file"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        temp_path = tmp.name

    communicate = edge_tts.Communicate(text, "en-IE-ConnorNeural")
    await communicate.save(temp_path)
    return temp_path

async def play_audio_file(audio_file: str):
    if not bot.voice_clients:
        add_log("Bot is not connected to a voice channel.")
        return False

    voice_client = bot.voice_clients[0]

    if not voice_client.is_connected():
        add_log("Voice client is not connected.")
        return False

    if not os.path.exists(audio_file):
        add_log(f"Audio file not found: {audio_file}")
        return False

    try:
        audio_source = discord.FFmpegPCMAudio(audio_file)
        add_log(f"Starting audio playback for file: {audio_file}")

        def cleanup_audio(error):
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    add_log(f"Cleaned up temp audio file: {audio_file}")
            except Exception as cleanup_err:
                add_log(f"Cleanup error: {cleanup_err}")
            if error:
                add_log(f"Audio playback finished with error: {error}")

        voice_client.play(audio_source, after=cleanup_audio)

        while voice_client.is_playing():
            await asyncio.sleep(0.5)

        return True

    except Exception as e:
        add_log(f"PLAY_AUDIO ERROR: {type(e).__name__}: {e}")

        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        except Exception:
            pass

        return False

async def tts_speak(text: str):
    if not bot.voice_clients:
        add_log("Bot is not connected to a voice channel.")
        return False

    voice_client = bot.voice_clients[0]

    if not voice_client.is_connected():
        add_log("Voice client is not connected.")
        return False

    temp_audio_file = None
    try:
        add_log(f"Generating TTS for text: {text}")

        temp_audio_file = await generate_tts(text)
        add_log(f"Audio file generated: {temp_audio_file}")

        # discord.py will find FFmpeg in PATH (works on all platforms)
        audio_source = discord.FFmpegPCMAudio(temp_audio_file)

        add_log("Starting audio playback.")

        def cleanup_audio(error):
            try:
                if temp_audio_file and os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
                    add_log(f"Cleaned up temp audio file: {temp_audio_file}")
            except Exception as cleanup_err:
                add_log(f"Cleanup error: {cleanup_err}")
            if error:
                add_log(f"Audio playback finished with error: {error}")

        voice_client.play(audio_source, after=cleanup_audio)

        while voice_client.is_playing():
            await asyncio.sleep(0.5)

        add_log(f"Spoke text: {text}")
        return True

    except Exception as e:
        add_log(f"TTS ERROR: {type(e).__name__}: {e}")

        import traceback
        traceback.print_exc()

        # Clean up temp file on error
        if temp_audio_file:
            try:
                if os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
            except:
                pass

        return False

async def play_mp3_file(mp3_path: str):
    return await play_audio_file(mp3_path)

@bot.command()
async def tts(ctx, *, text: str):
    success = await tts_speak(text)

    if not success:
        await ctx.send("I couldn't speak that text.")
    else:
        await ctx.send(f"Spoke text: {text}")

REACTION_DISCORD_ID = None
REACTION_EMOJI = "✅"
AUTO_REACT = False

async def set_auto_react(id: int, emoji: str):
    global AUTO_REACT
    global REACTION_DISCORD_ID
    global REACTION_EMOJI
    REACTION_DISCORD_ID = id
    REACTION_EMOJI = emoji
    AUTO_REACT = True
    add_log("Auto-react enabled.")

async def disable_auto_react():
    global AUTO_REACT
    AUTO_REACT = False
    add_log("Auto-react disabled.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if AUTO_REACT and message.author.id == REACTION_DISCORD_ID:
        try:
            await message.add_reaction(REACTION_EMOJI)
            add_log(f"Auto-reacted to message from {message.author} with {REACTION_EMOJI}")
        except Exception as e:
            add_log(f"Failed to auto-react: {e}")


def run_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")

    if not TOKEN:
        add_log("ERROR: DISCORD_TOKEN environment variable is not set!")
        return
    
    add_log("Starting Discord bot...")
    bot.run(TOKEN)