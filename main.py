import threading
import asyncio

from flask import Flask, render_template, request

import bot
from logs import get_logs
    

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/logs')
def logs_page():
    return {"logs": get_logs()}


@app.route('/echo', methods=['POST'])
def echo():
    message = request.form['message']
    channel_id = int(request.form['channel_id'])

    if bot.bot_loop is None:
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.send_message_to_channel(channel_id, message),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to send message to channel ID: {channel_id}.", 400

    return f"Echoed message to channel ID: {channel_id}."

@app.route('/join_voice', methods=['POST'])
def join_voice():
    voice_channel_id = int(request.form['voice_channel_id'])

    if bot.bot_loop is None:
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.join_voice_channel(voice_channel_id),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to join voice channel ID: {voice_channel_id}.", 400

    return f"Joined voice channel ID: {voice_channel_id}."

@app.route('/leave_voice', methods=['POST'])
def leave_voice():
    voice_channel_id = int(request.form['voice_channel_id'])

    if bot.bot_loop is None:
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.leave_voice_channel(voice_channel_id),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to leave voice channel ID: {voice_channel_id}.", 400

    return f"Left voice channel ID: {voice_channel_id}."

def start_bot():
    bot.run_bot()


bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()