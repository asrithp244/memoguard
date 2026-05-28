import time
from audio.capture import record_utterance, transcribe
from nlu.intent_parser import parse_intent
from guardrails.guardrails import check_guardrails
from behaviors.dispatcher import dispatch
from tts.speak import speak
from utils.audit import log_event

BANNER = """
╔══════════════════════════════════════╗
║  MemoGuard — Voice Robot Interface  ║
║  Ctrl+C to stop                     ║
╚══════════════════════════════════════╝
"""

def run():
    print(BANNER)
    while True:
        try:
            t_start = time.time()
            audio_path, duration = record_utterance()

            text = transcribe(audio_path)
            t_stt = time.time()

            if not text.strip():
                print("[No speech detected, listening again...]")
                continue

            print(f"\n👤 You said: \"{text}\"")

            guard = check_guardrails(text)
            t_guard = time.time()

            if guard["blocked"]:
                response = "I'm sorry, I can't help with that."
                print(f"🛡️  BLOCKED — Reason: {guard.get('reason')}")
                speak(response)
                log_event(text, None, guard, response, {
                    "stt": t_stt - t_start,
                    "guardrail": t_guard - t_stt,
                    "total": time.time() - t_start
                })
                continue

            intent = parse_intent(text)
            t_nlu = time.time()
            print(f"🧠 Intent: {intent}")

            response = dispatch(intent)
            t_dispatch = time.time()

            speak(response)
            t_total = time.time()

            log_event(text, intent, guard, response, {
                "stt": t_stt - t_start,
                "guardrail": t_guard - t_stt,
                "nlu": t_nlu - t_guard,
                "dispatch": t_dispatch - t_nlu,
                "total": t_total - t_start
            })

            print(f"⏱️  Total latency: {(t_total - t_start)*1000:.0f}ms")

        except KeyboardInterrupt:
            print("\n\nStopping MemoGuard. Goodbye!")
            break
        except Exception as e:
            print(f"[Error: {e}]")
            continue

if __name__ == "__main__":
    run()