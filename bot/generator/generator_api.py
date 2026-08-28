from pathlib import Path

from . import nama_generator
from . import iphone_ua_generator

BASE_DIR = Path(__file__).resolve().parent
USERNAME_OUTPUT = BASE_DIR.parent.parent / "outputs" / "username" / "hasil_username.txt"
UA_OUTPUT = BASE_DIR.parent.parent / "outputs" / "iphone_ua" / "hasil_iphone_ua.txt"


def generate_usernames(count: int):
    if count < 1:
        raise ValueError("Jumlah harus lebih dari 0.")
    results = nama_generator.generate(count)
    usernames = [item["username"] for item in results]
    USERNAME_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    USERNAME_OUTPUT.write_text("\n".join(usernames) + ("\n" if usernames else ""), encoding="utf-8")
    return usernames, USERNAME_OUTPUT


def generate_iphone_uas(count: int, with_model: bool = False):
    if count < 1:
        raise ValueError("Jumlah harus lebih dari 0.")
    history = iphone_ua_generator.load_history()
    result = []
    seen = set()
    attempts = 0
    max_attempts = count * 50 + 1000
    while len(result) < count and attempts < max_attempts:
        attempts += 1
        ua = iphone_ua_generator.build_ua(with_model)
        if ua in history or ua in seen:
            continue
        seen.add(ua)
        result.append(ua)
    UA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    UA_OUTPUT.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
    iphone_ua_generator.save_history(result)
    return result, UA_OUTPUT
