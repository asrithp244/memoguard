MAX_RESPONSE_SENTENCES = 2

def _truncate(text):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    return '. '.join(sentences[:MAX_RESPONSE_SENTENCES]) + '.'

def dispatch(intent):
    name = intent.get("intent", "unknown")
    target = intent.get("target", "")
    duration = intent.get("duration_minutes", 1)

    if name == "move_to_room":
        response = f"Moving to the {target} now." if target else "Where would you like me to go?"
    elif name == "pick_up_object":
        response = f"Picking up the {target}. I'll bring it to you." if target else "What object should I pick up?"
    elif name == "set_timer":
        response = f"Timer set for {duration} {'minute' if duration == 1 else 'minutes'}. I'll alert you when it's done."
    elif name == "report_status":
        response = "All systems operational. Battery at 80 percent, no obstacles detected."
    elif name == "turn_on_light":
        room = f" in the {target}" if target else ""
        response = f"Turning on the light{room}."
    elif name == "turn_off_light":
        room = f" in the {target}" if target else ""
        response = f"Turning off the light{room}."
    else:
        response = "I didn't catch that. Could you rephrase your command?"

    return _truncate(response)