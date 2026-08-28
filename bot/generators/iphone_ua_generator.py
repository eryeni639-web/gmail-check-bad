#!/usr/bin/env python3
"""
Generator User Agent iPhone (Chrome for iOS / CriOS) — versi scalable.

Cara pakai:
    python3 ua_generator.py --count 1000
    python3 ua_generator.py --count 5000 --out hasil.txt
    python3 ua_generator.py --count 1000 --with-model     # sisipkan identifier hardware di UA
    python3 ua_generator.py --reset                       # kosongkan histori dedup

Setiap kali dijalankan, script ini:
  1. Membaca histori UA yang sudah pernah dibuat dari file '.ua_history.txt'
  2. Generate UA baru secara acak dalam ruang kombinasi yang jauh lebih besar
     (bukan tabel hardcode kecil), lalu buang yang sudah pernah muncul.
  3. Menyimpan hasil baru ke --out DAN menambahkannya ke histori,
     sehingga run berikutnya otomatis tidak akan menghasilkan yang sama lagi.
"""

import argparse
import os
import random

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ua_history.txt")

# --- Ruang versi iOS yang realistis (major_minor) ---
IOS_VERSIONS = [f"{major}_{minor}" for major in range(14, 19) for minor in range(0, 8)]

# --- Build number iOS mengikuti pola asli Apple: <darwin_major_letter><digit><suffix> ---
IOS_BUILD_LETTERS = "ABCDEFGH"

def random_ios_build(major):
    darwin_major = 18 + (major - 14)  # perkiraan kasar korelasi versi darwin
    letter = random.choice(IOS_BUILD_LETTERS)
    num = random.randint(50, 999)
    return f"{darwin_major}{letter}{num}"

# --- Rentang versi Chrome (CriOS) realistis, major 91–137 (rilis ~2021–2026) ---
def random_crios():
    major = random.randint(91, 137)
    build = random.randint(4400, 7200)
    patch = random.randint(1, 250)
    return f"{major}.0.{build}.{patch}"

# --- Identifier hardware resmi Apple (opsional, kalau --with-model dipakai) ---
MODEL_IDS = [
    "iPhone10,1", "iPhone10,2", "iPhone10,3", "iPhone10,4", "iPhone10,5", "iPhone10,6",
    "iPhone11,2", "iPhone11,4", "iPhone11,6", "iPhone11,8",
    "iPhone12,1", "iPhone12,3", "iPhone12,5", "iPhone12,8",
    "iPhone13,1", "iPhone13,2", "iPhone13,3", "iPhone13,4",
    "iPhone14,2", "iPhone14,3", "iPhone14,4", "iPhone14,5", "iPhone14,6", "iPhone14,7", "iPhone14,8",
    "iPhone15,2", "iPhone15,3", "iPhone15,4", "iPhone15,5",
    "iPhone16,1", "iPhone16,2",
    "iPhone17,1", "iPhone17,2", "iPhone17,3", "iPhone17,4",
]

def build_ua(with_model: bool) -> str:
    ios = random.choice(IOS_VERSIONS)
    major = int(ios.split("_")[0])
    build = random_ios_build(major)
    crios = random_crios()
    prefix = random.choice(MODEL_IDS) if with_model else "iPhone"
    return (
        f"Mozilla/5.0 ({prefix}; CPU iPhone OS {ios} like Mac OS X) "
        f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
        f"CriOS/{crios} Mobile/{build} Safari/604.1"
    )

def load_history() -> set:
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(new_uas):
    with open(HISTORY_FILE, "a") as f:
        for ua in new_uas:
            f.write(ua + "\n")

def main():
    parser = argparse.ArgumentParser(description="Generate UA iPhone unik, auto-dedup lintas run.")
    parser.add_argument("--count", type=int, default=100, help="Jumlah UA yang mau dihasilkan (default 100)")
    parser.add_argument("--out", type=str, default="ua_output.txt", help="Nama file output")
    parser.add_argument("--with-model", action="store_true", help="Sisipkan identifier hardware iPhone di dalam UA")
    parser.add_argument("--reset", action="store_true", help="Kosongkan histori dedup lalu keluar")
    args = parser.parse_args()

    if args.reset:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print("Histori dedup sudah direset.")
        return

    history = load_history()
    result = []
    seen_this_run = set()

    attempts = 0
    max_attempts = args.count * 50 + 1000
    while len(result) < args.count and attempts < max_attempts:
        attempts += 1
        ua = build_ua(args.with_model)
        if ua in history or ua in seen_this_run:
            continue
        seen_this_run.add(ua)
        result.append(ua)

    with open(args.out, "w") as f:
        for ua in result:
            f.write(ua + "\n")

    save_history(result)

    print(f"Berhasil generate {len(result)} UA unik -> {args.out}")
    print(f"Total histori kumulatif sekarang: {len(history) + len(result)} UA")
    if len(result) < args.count:
        print(f"Catatan: hanya berhasil {len(result)}/{args.count} karena ruang kombinasi mulai menipis "
              f"di parameter saat ini. Perbesar rentang IOS_VERSIONS / random_crios() kalau butuh lebih banyak lagi.")

if __name__ == "__main__":
    main()
