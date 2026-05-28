import json
from datetime import datetime

LOG_FILE = "audit.log"

def log_event(utterance, intent, guard_result, response, latencies_sec):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "utterance": utterance,
        "intent": intent,
        "guard": {
            "blocked": guard_result.get("blocked"),
            "reason":  guard_result.get("reason"),
            "layer":   guard_result.get("layer"),
            "scores":  guard_result.get("scores")
        },
        "response": response,
        "latency_ms": {
            k: round(v * 1000, 1)
            for k, v in latencies_sec.items()
        }
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")