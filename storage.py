import json
import os

STORAGE_PATH = "/tmp/agent_configs.json"

def load_agent_configs():
    if os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    return {
        "Manager": {"instructions": "", "backstory": ""},
        "Cercetător": {"instructions": "", "backstory": ""},
        "Scriitor": {"instructions": "", "backstory": ""},
        "Analist": {"instructions": "", "backstory": ""},
        "Expert Financiar": {"instructions": "", "backstory": ""}
    }

def save_agent_configs(configs):
    with open(STORAGE_PATH, "w") as f:
        json.dump(configs, f)