"""Lesson 3: a voice pipeline: speech to text, reason over text, then text to speech.

Offline, the input audio is a test tone, the transcript is simulated, and the output is a tone.

Run: python lessons/03_voice_pipeline.py
"""

import sys
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from genai_kit import get_llm  # noqa: E402
from project.media import synthesize_speech, transcribe, write_test_tone  # noqa: E402


def timed(label, function, *args):
    start = time.perf_counter()
    result = function(*args)
    print(f"  {label:<18}{(time.perf_counter() - start) * 1000:>8.1f} ms")
    return result


def main() -> None:
    output = UNIT / "output"
    recording = write_test_tone(output / "caller.wav", seconds=1.5)
    llm = get_llm(mock_handler=lambda messages, system, tools: "[mock] Let me check order A-1002 for you.")

    print("Each stage adds to the delay the caller hears:")
    transcript = timed("1. speech to text", transcribe, recording)
    reply = timed(
        "2. model reply",
        lambda: llm.complete(
            [{"role": "user", "content": transcript}],
            system="You are a phone support agent. Reply in one short spoken sentence.",
            max_tokens=80,
        ).text,
    )
    audio = timed("3. text to speech", synthesize_speech, reply, output / "reply.wav")

    print(f"\nCaller said : {transcript}")
    print(f"Agent says  : {reply}")
    print(f"Reply audio : {audio}")
    print("\nReal voice products stream at every stage. Providers also offer realtime speech-to-speech")
    print("APIs. Always tell callers that they are speaking with AI, and get consent to record.")


if __name__ == "__main__":
    main()
