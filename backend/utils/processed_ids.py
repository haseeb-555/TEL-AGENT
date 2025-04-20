import json
import os

FILE_PATH = "processed_ids.json"

def load_processed_ids():
    if not os.path.exists(FILE_PATH):
        return set()
    with open(FILE_PATH, "r") as f:
        return set(json.load(f))

def save_processed_ids(processed_ids):
    with open(FILE_PATH, "w") as f:
        json.dump(list(processed_ids), f)
