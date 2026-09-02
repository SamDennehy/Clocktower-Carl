import threading
import asyncio
import os
import tempfile
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

@app.route('/play_mp3', methods=['POST'])
def play_mp3():
    if 'mp3_file' not in request.files:
        return "No MP3 file uploaded.", 400

    uploaded_file = request.files['mp3_file']

    if uploaded_file.filename == '':
        return "No file selected.", 400

    if not uploaded_file.filename.lower().endswith('.mp3'):
        return "Only .mp3 files are supported.", 400

    temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
    os.close(temp_fd)
    uploaded_file.save(temp_path)

    if getattr(bot, "bot_loop", None) is None:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return "Discord bot loop is not available yet.", 503

    try:
        future = asyncio.run_coroutine_threadsafe(
            bot.play_mp3_file(temp_path),
            bot.bot_loop,
        )
        success = future.result()
    except Exception as exc:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        add_log(f"Failed to play uploaded MP3: {exc}")
        return f"Failed to play uploaded MP3: {exc}", 500

    if not success:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return "Failed to play uploaded MP3.", 400

    return "MP3 uploaded and playing in the voice channel.", 204

@app.route('/set_auto_react', methods=['POST'])
def set_auto_react():
    id = request.form['id']
    emoji = request.form['emoji']

    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.set_auto_react(int(id), emoji),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to set auto-react.", 400

    return f"Auto-react set successfully.", 204

@app.route('/disable_auto_react', methods=['POST'])
def disable_auto_react():
    if getattr(bot, "bot_loop", None) is None:
        return "Discord bot loop is not available yet.", 503

    future = asyncio.run_coroutine_threadsafe(
        bot.disable_auto_react(),
        bot.bot_loop
    )

    success = future.result()

    if not success:
        return f"Failed to disable auto-react.", 400

    return f"Auto-react disabled successfully.", 204

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