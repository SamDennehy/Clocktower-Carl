import os
import threading
import discord
import json
from discord.ext import commands
from random import sample, choice
import os
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    # Render provides the port dynamically via an environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

load_dotenv()


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

# Step 1: Configure permissions (intents)
intents = discord.Intents.default()
intents.message_content = True  # Required to read message text

# Step 2: Initialize the bot with a command prefix (e.g., !)
bot = commands.Bot(command_prefix='!', intents=intents)

# Step 3: Event that triggers when the bot successfully logs in
@bot.event
async def on_ready():
    print(f'Logged in successfully as {bot.user.name}')

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

@bot.command()
async def generate_script(ctx, *args):
    values = [int(x) for x in args]
    if len(args) != 5:
        if len(args) == 0:
            values = [13,4,4,1,0]
        else:
            await ctx.send("Please provide either 0 or 5 values.")
            return


    script = build_download_script_and_preview(values)
    with open('generated_script.json', 'w') as f:
        json.dump(script[0], f, indent=2)
    with open('generated_script.json', 'rb') as f:
            discord_file = discord.File(f, filename="generated_script.json")

    preview = script[1]
    preview_string = f"SCRIPT PREVIEW:\n"
    for category, list in preview.items():
         preview_string += f"{'-'*10}\n{category.upper()}:\n{'-'*10}\n"
         for character in list:
              preview_string += f"{character}\n"
    await ctx.send(preview_string, file=discord_file)

@bot.command()
async def choose_storyteller(ctx, *args):
    names = [str(x) for x in args]

    await ctx.send(f"Storyteller: {choice(names)}")

@bot.command()
async def choose_storytellers(ctx, *args):
    names = [str(x) for x in args]
    chosen = sample(names, k=2)
    await ctx.send(f"Storyteller: {chosen[0]} {chosen[1]}")

# Step 5: Start the bot

def run_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")

    if not TOKEN:
        print("ERROR: DISCORD_TOKEN environment variable is not set!")
        return

    print("Starting Discord bot...")
    bot.run(TOKEN)


bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()