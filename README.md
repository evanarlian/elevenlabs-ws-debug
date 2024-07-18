# elevenlabs-ws-debug

# installation
Make virtual env and install requirements.
```bash
sudo apt install mpv  # from official elevenlabs websocket tutorial
sudo apt install portaudio19-dev  # because of pyaudio
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and fill all the required values.

# report
Here is the setup. I have a stream of token inputs from LLM, but for this case, I'll simulate LLM by reading from file and outputting words instead. I modified [this example](https://elevenlabs.io/docs/api-reference/websockets#example-voice-streaming-using-elevenlabs-and-openai) from the docs.
```bash
python mpv.py
```
Wait for a while, and this is the error message.
```
websockets.exceptions.ConnectionClosedError: received 1008 (policy violation) Have not received a new text input within the timeout of 20.0 seconds. Streaming input terminated.
```
My observation:
* The word iterator has not finished. For some reason websocket sending is blocked, which triggered the 20 sec timeout.
* Volume is getting smaller the longer the audio.
