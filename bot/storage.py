import json
import os

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "users.json")
os.makedirs(DATA_DIR, exist_ok=True)


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_emails(user_id, emails):
    data = load_users()
    data[str(user_id)] = emails
    save_users(data)


def get_emails(user_id):
    data = load_users()
    return data.get(str(user_id), [])


def clear_emails(user_id):
    data = load_users()
    if str(user_id) in data:
        del data[str(user_id)]
        save_users(data)
