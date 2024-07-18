import asyncio
import base64
import json
import os
import shutil
import subprocess

import websockets
from dotenv import load_dotenv

load_dotenv()


# Define API keys and voice ID
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker():
    with open("sample.txt", "r") as f:
        content = f.read()
    for word in content.split():
        await asyncio.sleep(0.02)  # fake llm
        yield word + " "


async def stream(audio_stream):
    """Stream audio data using mpv player."""
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("Started streaming audio")
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()


async def text_to_speech_input_streaming():
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id=eleven_turbo_v2"

    async with websockets.connect(uri) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                    "xi_api_key": ELEVENLABS_API_KEY,
                }
            )
        )

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    print("🌊 [ws receive]")
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get("isFinal"):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))

        async for text in text_chunker():
            print(f"[ws send] {text}")
            await websocket.send(
                json.dumps({"text": text, "try_trigger_generation": True})
            )

        await websocket.send(json.dumps({"text": ""}))

        await listen_task


# Main execution
if __name__ == "__main__":
    asyncio.run(text_to_speech_input_streaming())
