import threading
import asyncio
import time

from flask import Flask, render_template, request

import bot

def add_log(message):
    bot.add_log(message)

def get_logs():
    return bot.get_logs()

app = Flask(__name__)
bot_thread = None
bot_thread_lock = threading.Lock()


@app.before_request
def start_bot_for_request():
    ensure_bot_started()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/logs')
def logs_page():
    return {"logs": get_logs()}


@app.route('/echo', methods=['POST'])
def echo():
    print("bot_loop seen by Flask:", getattr(bot, "bot_loop", None))

    message = request.form['message']
    channel_id = int(request.form['channel_id'])

    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

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

    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

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

    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.leave_voice_channel(),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to leave voice channel.", 400

    return f"Left voice channel successfully.", 204

@app.route('/tts', methods=['POST'])
def tts():
    text = request.form['text']

    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.tts_speak(text),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to generate TTS for text: {text}.", 400

    return f"TTS generated successfully for text: {text}.", 204

def start_bot():
    print("STARTING DISCORD BOT THREAD", flush=True)

    try:
        bot.run_bot()
    except Exception as e:
        print(f"DISCORD BOT THREAD CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()


def ensure_bot_started():
    global bot_thread

    if bot_thread and bot_thread.is_alive():
        return

    with bot_thread_lock:
        if bot_thread and bot_thread.is_alive():
            return

        bot_thread = threading.Thread(target=start_bot, daemon=True, name="discord-bot")
        bot_thread.start()


if __name__ == '__main__':
    ensure_bot_started()
    app.run(debug=True, use_reloader=False)