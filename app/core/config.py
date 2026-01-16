import os
import json
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CONFIG_PATH = os.path.join("data", "app_config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(new_config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(new_config, f, indent=2)

config = load_config()
