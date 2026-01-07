import json
import os

def make_serializable(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(v) for v in obj]
    else:
        return obj

def restore_sets(obj):
    if isinstance(obj, list):
        return set(restore_sets(v) for v in obj)
    elif isinstance(obj, dict):
        return {k: restore_sets(v) for k, v in obj.items()}
    else:
        return obj

def save_data(filename, list_data):
    serializable_data = make_serializable(list_data)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(serializable_data, file, ensure_ascii=False, indent=4)

def load_data(filename):
    if not os.path.exists(filename):
        return {}

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    data = restore_sets(data)
    return data