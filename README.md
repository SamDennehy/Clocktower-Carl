# Clocktower Carl

Clocktower Carl is a Discord bot and companion web dashboard for organizing games of *Blood on the Clocktower*. It can generate random scripts, track player statistics, manage timers, and provide optional voice-channel tools.

## Important Notice

Clocktower Carl is an unofficial, community-created project. It is not affiliated with, endorsed by, sponsored by, or approved by The Pandemonium Institute or the creators of *Blood on the Clocktower*.

*Blood on the Clocktower* and related names, characters, and artwork belong to their respective owners. This project is intended for personal and community use.

## Features

- Generate scripts for supported *Blood on the Clocktower* editions and custom scripts
- Use interactive Discord menus for alignment, character type, script, and game-result inputs
- Record and display player statistics and win-rate leaderboards
- Run a browser-based Grimoire with timers, seating, and script information
- Send messages from the dashboard
- Join and leave Discord voice channels
- Generate text-to-speech audio and play MP3 files in voice channels
- Configure automatic reactions for messages from a selected Discord user
- View bot logs through the dashboard

## Limitations

- Carl can only be connected to one Discord voice channel at a time across all servers where it is installed. Joining a voice channel in another server moves Carl out of its current channel.
- Only one automatic-reaction rule can be active at a time: one Discord user and one emoji. Setting a new rule replaces the existing rule.

## Requirements

- Python 3.10 or newer
- A Discord bot application and token
- A PostgreSQL database
- A Discord server where you can install the bot

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. Do not commit this file or share its values.

```dotenv
DISCORD_TOKEN=your-discord-bot-token
DATABASE_URL=postgresql://user:password@host:5432/database
FLASK_SECRET_KEY=replace-with-a-long-random-value
DASHBOARD_PASSWORD=choose-a-dashboard-password
```

The bot initializes its required statistics tables in the configured PostgreSQL database when it starts.

## Running Locally

Start the bot and web dashboard with:

```bash
python main.py
```

The web dashboard is served by Flask. The dashboard includes protected controls for sending messages, managing voice playback, and viewing logs.

## Project Structure

- `bot.py` - Discord bot commands, interactions, statistics, and voice features
- `main.py` - Flask application and bot startup
- `templates/` - Web dashboard and Grimoire pages
- `static/` - Stylesheets, JavaScript, and image/audio assets
- `models.py` - Script data model
- `role_descriptions.py` - Role descriptions used by the bot

## Disclaimer

Use this project at your own risk. You are responsible for complying with Discord's Terms of Service, the rules of any server where you install the bot, and any applicable rights or licenses for content used with it.
