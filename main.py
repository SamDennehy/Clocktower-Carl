import threading
import asyncio

from flask import Flask, render_template, request

import bot
from logs import get_logs, add_log

app = Flask(__name__)
bot_thread = None
bot_thread_lock = threading.Lock()


def is_bot_ready():
    return bot is not None and bot.bot_loop is not None and bot.is_ready()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/logs')
def logs_page():
    return {"logs": get_logs()}


@app.route('/echo', methods=['POST'])
def echo():
    print("bot_loop seen by Flask:", bot.bot_loop)

    message = request.form['message']
    channel_id = int(request.form['channel_id'])

    if not is_bot_ready():
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.send_message_to_channel(channel_id, message),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to send message to channel ID: {channel_id}.", 400

    return f"Echoed message to channel ID: {channel_id}.", 204

@app.route('/join_voice', methods=['POST'])
def join_voice():
    voice_channel_id = int(request.form['voice_channel_id'])
    add_log(f"Attempting to join voice channel ID: {voice_channel_id}.")

    if not is_bot_ready():
        add_log("Bot is not ready yet.")
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.join_voice_channel(voice_channel_id),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to join voice channel ID: {voice_channel_id}.", 400

    return f"Joined voice channel ID: {voice_channel_id}.", 204

@app.route('/leave_voice', methods=['POST'])
def leave_voice():
    if not is_bot_ready():
        return "Bot is not ready yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.leave_voice_channel(),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to leave voice channel.", 400

    return f"Left voice channel successfully.", 204

def start_bot():
    bot.run_bot()


def ensure_bot_started():
    global bot_thread

    if bot_thread and bot_thread.is_alive():
        return

    with bot_thread_lock:
        if bot_thread and bot_thread.is_alive():
            return

        bot_thread = threading.Thread(target=start_bot, daemon=True, name="discord-bot")
        bot_thread.start()


ensure_bot_started()


if __name__ == '__main__':
    app.run(debug=True)