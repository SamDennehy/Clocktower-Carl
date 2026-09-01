import asyncio
import edge_tts

async def generate_tts(text):
    communicate = edge_tts.Communicate(
        text,
        "en-IE-ConnorNeural"
    )
    await communicate.save("speech.mp3")

asyncio.run(generate_tts("Hello everyone, welcome to the game."))