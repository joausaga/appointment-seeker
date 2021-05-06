import json
import unicodedata

def get_config(config_file):
    with open(str(config_file), 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
    return config


def normalize_text(text):
    if isinstance(text,str):
        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode()
    else:
        return text