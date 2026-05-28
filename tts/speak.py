import pyttsx3

_engine = pyttsx3.init()
_engine.setProperty('rate', 165)
_engine.setProperty('volume', 0.9)

def speak(text):
    print(f"\n🤖 Robot: {text}")
    _engine.say(text)
    _engine.runAndWait()