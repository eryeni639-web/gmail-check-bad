from pathlib import Path
import shutil

from . import nama_generator
from . import iphone_ua_generator

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
USERNAME_OUT = ROOT_DIR / 'outputs' / 'username' / 'hasil_username.txt'
UA_OUT = ROOT_DIR / 'outputs' / 'iphone_ua' / 'hasil_iphone_ua.txt'


def generate_usernames(count: int) -> Path:
    count = int(count)
    if count <= 0:
        raise ValueError('Jumlah harus lebih dari 0.')

    results = nama_generator.generate(count)
    if not results:
        raise RuntimeError('Tidak ada username yang berhasil dibuat.')

    source = nama_generator.OUTPUT_FILE
    if not source.exists():
        raise RuntimeError('File hasil_username.txt tidak ditemukan.')

    USERNAME_OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, USERNAME_OUT)
    return USERNAME_OUT


def generate_iphone_uas(count: int, with_model: bool = False) -> Path:
    count = int(count)
    if count <= 0:
        raise ValueError('Jumlah harus lebih dari 0.')

    history = iphone_ua_generator.load_history()
    result = []
    seen_this_run = set()
    attempts = 0
    max_attempts = count * 50 + 1000

    while len(result) < count and attempts < max_attempts:
        attempts += 1
        ua = iphone_ua_generator.build_ua(with_model)
        if ua in history or ua in seen_this_run:
            continue
        seen_this_run.add(ua)
        result.append(ua)

    if not result:
        raise RuntimeError('Tidak ada UA unik yang berhasil dibuat.')

    UA_OUT.parent.mkdir(parents=True, exist_ok=True)
    with UA_OUT.open('w', encoding='utf-8') as f:
        f.write('\n'.join(result) + '\n')

    iphone_ua_generator.save_history(result)
    return UA_OUT
