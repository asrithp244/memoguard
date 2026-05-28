import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import subprocess
import json
import time

# Path to the C++ binary and model inside WSL
WHISPER_BIN   = "/home/asrith244/whisper.cpp/build/bin/whisper-json"
WHISPER_MODEL = "/home/asrith244/whisper.cpp/models/ggml-base.en.bin"

SAMPLE_RATE      = 16000
CHUNK_DURATION   = 0.1
SILENCE_THRESHOLD = 0.015
SILENCE_CHUNKS   = 15
MIN_SPEECH_CHUNKS = 4


def record_utterance():
    chunks = []
    silence_count = 0
    speech_started = False
    speech_chunks = 0
    chunk_samples = int(SAMPLE_RATE * CHUNK_DURATION)

    print("[Waiting for you to speak...]", end="", flush=True)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        while True:
            data, _ = stream.read(chunk_samples)
            rms = float(np.sqrt(np.mean(data ** 2)))

            if rms > SILENCE_THRESHOLD:
                if not speech_started:
                    print(" Recording...", end="", flush=True)
                speech_started = True
                speech_chunks += 1
                silence_count = 0
                chunks.append(data.copy())
            elif speech_started:
                chunks.append(data.copy())
                silence_count += 1
                if silence_count >= SILENCE_CHUNKS:
                    break

    print()

    if speech_chunks < MIN_SPEECH_CHUNKS:
        return None, 0

    audio = np.concatenate(chunks, axis=0).flatten()
    duration = len(audio) / SAMPLE_RATE

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav.write(tmp.name, SAMPLE_RATE, (audio * 32767).astype(np.int16))
    return tmp.name, duration


def transcribe(audio_path):
    """
    Calls the C++ whisper-json binary via WSL.
    Falls back to faster-whisper if WSL call fails.
    """
    if audio_path is None:
        return ""

    t0 = time.time()

    try:
        # Convert Windows path to WSL path
        wsl_path = audio_path.replace("\\", "/").replace("C:", "/mnt/c")

        result = subprocess.run(
            ["wsl", WHISPER_BIN, WHISPER_MODEL, wsl_path],
            capture_output=True, text=True, timeout=15
        )

        # Parse JSON from output (ignore model loading lines)
        for line in result.stdout.splitlines():
            if line.startswith('{"text"'):
                data = json.loads(line)
                text = data.get("text", "").strip()
                print(f"[C++ STT: {(time.time()-t0)*1000:.0f}ms]")
                os.unlink(audio_path)
                return text

    except Exception as e:
        print(f"[C++ STT failed: {e}, falling back to Python]")

    # Fallback to faster-whisper
    from faster_whisper import WhisperModel
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, beam_size=1)
    text = " ".join(s.text for s in segments).strip()
    os.unlink(audio_path)
    return text