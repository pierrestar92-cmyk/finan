import json
import os

DATA_FILE = "finanzdaten.json"
HISTORY_FILE = "finanzverlauf.json"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            # corrupted file -> return default
            return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
