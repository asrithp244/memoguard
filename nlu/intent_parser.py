import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a home robot intent parser.
Given a voice command from a user, extract the intent as JSON.
Return ONLY valid JSON — no explanation, no markdown, no backticks.

Available intents:
- move_to_room     (e.g. "go to the kitchen")
- pick_up_object   (e.g. "pick up the cup")
- set_timer        (e.g. "set a 5 minute timer")
- report_status    (e.g. "what's your status")
- turn_on_light    (e.g. "turn on the light")
- turn_off_light   (e.g. "turn off the light")
- unknown          (anything else)

Examples:
Input: "go to the kitchen"
Output: {"intent": "move_to_room", "target": "kitchen", "confidence": 0.95}

Input: "pick up the book on the table"
Output: {"intent": "pick_up_object", "target": "book", "confidence": 0.90}

Input: "set a 5 minute timer"
Output: {"intent": "set_timer", "duration_minutes": 5, "confidence": 0.95}

Input: "what is your battery level"
Output: {"intent": "report_status", "confidence": 0.92}

Always include at least "intent" and "confidence" in your JSON."""


def parse_intent(text):
    prompt = f'{SYSTEM_PROMPT}\n\nInput: "{text}"\nOutput:'

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 80
                }
            },
            timeout=15
        )
        response.raise_for_status()
        raw = response.json()["response"].strip()

        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        return {"intent": "unknown", "confidence": 0.0, "raw": raw}

    except requests.exceptions.ConnectionError:
        print("[ERROR] Ollama not running. Start it with: ollama serve")
        return {"intent": "unknown", "confidence": 0.0, "error": "ollama_offline"}
    except Exception as e:
        return {"intent": "unknown", "confidence": 0.0, "error": str(e)}