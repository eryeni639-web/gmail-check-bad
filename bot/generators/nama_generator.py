import random
import re
import csv
from datetime import datetime
from pathlib import Path


# ============================================================
# GENERATOR NAMA -> USERNAME
# VERSI FINAL
# ============================================================
#
# DATABASE:
#
# database_nama.txt
#
# Isinya cukup:
#
# Jaka Kartika
# Rina Putri
# Daniel Smith
# Lily Collins
# Budi Santoso
# Naya Pratama
#
# ============================================================
#
# ATURAN:
#
# 1. 1 nama = 1 username
# 2. Nama depan tidak boleh duplikat dalam satu batch
# 3. Nama yang pernah digunakan akan dihindari
# 4. Jika nama lama perlu digunakan lagi,
#    nama akan dimodifikasi
# 5. Username wajib memiliki angka
# 6. Angka maksimal 3 digit
# 7. Angka berada di belakang username
# 8. Double huruf diperbolehkan
# 9. Username tidak boleh sama dengan history
# 10. Setiap generate dicatat tanggal dan jam
# 11. Jumlah generate dicatat
# 12. hasil_username.txt hanya berisi generate TERAKHIR
# 13. History tidak perlu dihapus setiap hari
#
# ============================================================


# ============================================================
# LOKASI FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "database_nama.txt"

HISTORY_FILE = BASE_DIR / "generator_history.csv"

USED_NAMES_FILE = BASE_DIR / "used_names.csv"

USED_USERNAMES_FILE = BASE_DIR / "used_usernames.txt"

OUTPUT_FILE = BASE_DIR / "hasil_username.txt"


# ============================================================
# MEMBERSIHKAN TEKS
# ============================================================

def clean_text(text):
    """
    Mengubah nama menjadi format yang cocok
    untuk username.

    Contoh:

    Jaka -> jaka
    Kartika -> kartika
    """

    return re.sub(
        r"[^a-zA-Z0-9]",
        "",
        text
    ).lower()


# ============================================================
# NORMALISASI NAMA
# ============================================================

def normalize_name(text):

    return " ".join(
        text.strip().split()
    )


# ============================================================
# MEMBACA DATABASE
# ============================================================

def load_database():

    if not DATABASE_FILE.exists():

        print()
        print("=" * 60)
        print("DATABASE TIDAK DITEMUKAN")
        print("=" * 60)
        print()
        print("File yang dicari:")
        print()
        print(DATABASE_FILE)
        print()
        print("Pastikan:")
        print()
        print("generate_nama.py")
        print("database_nama.txt")
        print()
        print("berada di folder yang sama.")
        print()

        return []


    records = []

    seen = set()


    try:

        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8-sig",
            errors="replace"
        ) as file:

            for line in file:

                line = line.strip()


                # --------------------------------------------
                # Lewati baris kosong
                # --------------------------------------------

                if not line:
                    continue


                # --------------------------------------------
                # Lewati komentar
                # --------------------------------------------

                if line.startswith("#"):
                    continue


                # --------------------------------------------
                # FORMAT UTAMA
                #
                # Jaka Kartika
                #
                # --------------------------------------------

                if "|" not in line and "\t" not in line:

                    full_name = normalize_name(
                        line
                    )


                # --------------------------------------------
                # FORMAT DENGAN |
                #
                # Jaka Kartika | Cowok | Indonesia
                #
                # Tetap didukung
                # --------------------------------------------

                elif "|" in line:

                    parts = [
                        x.strip()
                        for x in line.split("|")
                    ]

                    full_name = normalize_name(
                        parts[0]
                    )


                # --------------------------------------------
                # FORMAT TAB
                #
                # Jaka Kartika    Cowok    Indonesia
                #
                # --------------------------------------------

                else:

                    parts = [
                        x.strip()
                        for x in line.split("\t")
                    ]

                    full_name = normalize_name(
                        parts[0]
                    )


                # --------------------------------------------
                # Lewati header
                # --------------------------------------------

                header = (
                    full_name
                    .lower()
                    .replace(" ", "")
                )


                if header in (
                    "nama",
                    "namalengkap",
                    "fullname",
                    "name"
                ):
                    continue


                # --------------------------------------------
                # Pecah nama
                # --------------------------------------------

                words = full_name.split()


                # Minimal 2 kata
                if len(words) < 2:
                    continue


                # --------------------------------------------
                # Nama depan
                # --------------------------------------------

                first = words[0]


                # --------------------------------------------
                # Nama belakang
                # Menggunakan kata terakhir
                # --------------------------------------------

                last = words[-1]


                first_clean = clean_text(
                    first
                )

                last_clean = clean_text(
                    last
                )


                if not first_clean:
                    continue


                if not last_clean:
                    continue


                # --------------------------------------------
                # Batasi panjang nama
                # --------------------------------------------

                if len(first_clean) > 15:
                    continue


                if len(last_clean) > 18:
                    continue


                # --------------------------------------------
                # Hindari duplikat database
                # --------------------------------------------

                key = (
                    first_clean,
                    last_clean
                )


                if key in seen:
                    continue


                seen.add(key)


                records.append({

                    "first": first,

                    "last": last,

                    "first_clean": first_clean,

                    "last_clean": last_clean

                })


    except Exception as error:

        print()
        print("GAGAL MEMBACA DATABASE")
        print()
        print(error)
        print()

        return []


    return records


# ============================================================
# LOAD NAMA YANG SUDAH PERNAH DIGUNAKAN
# ============================================================

def load_used_names():

    used = set()


    if not USED_NAMES_FILE.exists():

        return used


    try:

        with open(
            USED_NAMES_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.reader(
                file
            )


            for row in reader:

                if len(row) < 2:
                    continue


                first = clean_text(
                    row[0]
                )

                last = clean_text(
                    row[1]
                )


                if first and last:

                    used.add(
                        (
                            first,
                            last
                        )
                    )


    except Exception:

        pass


    return used


# ============================================================
# SIMPAN NAMA YANG SUDAH DIGUNAKAN
# ============================================================

def save_used_names(used):

    with open(
        USED_NAMES_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )


        for first, last in sorted(
            used
        ):

            writer.writerow([
                first,
                last
            ])


# ============================================================
# LOAD USERNAME YANG SUDAH DIGUNAKAN
# ============================================================

def load_used_usernames():

    if not USED_USERNAMES_FILE.exists():

        return set()


    try:

        with open(
            USED_USERNAMES_FILE,
            "r",
            encoding="utf-8-sig",
            errors="replace"
        ) as file:

            return {
                line.strip().lower()
                for line in file
                if line.strip()
            }


    except Exception:

        return set()


# ============================================================
# SIMPAN USERNAME
# ============================================================

def save_used_usernames(
    usernames
):

    with open(
        USED_USERNAMES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for username in sorted(
            usernames
        ):

            file.write(
                username + "\n"
            )


# ============================================================
# DOUBLE HURUF
# ============================================================

def double_letter(word):

    if not word:

        return word


    # Jangan terlalu sering
    # mengubah nama yang sangat pendek

    if len(word) <= 2:

        return word + word[-1]


    position = random.randint(
        0,
        len(word) - 1
    )


    return (
        word[:position + 1]
        + word[position]
        + word[position + 1:]
    )


# ============================================================
# MEMBUAT VARIASI NAMA
# ============================================================

def create_name_variation(
    first,
    last,
    used_names
):

    variations = []


    # --------------------------------------------
    # Double huruf depan
    # --------------------------------------------

    variations.append(
        (
            double_letter(first),
            last
        )
    )


    # --------------------------------------------
    # Double huruf belakang
    # --------------------------------------------

    variations.append(
        (
            first,
            double_letter(last)
        )
    )


    # --------------------------------------------
    # Tambahkan huruf terakhir
    # --------------------------------------------

    variations.append(
        (
            first + first[-1],
            last
        )
    )


    variations.append(
        (
            first,
            last + last[-1]
        )
    )


    # --------------------------------------------
    # Double keduanya
    # --------------------------------------------

    variations.append(
        (
            double_letter(first),
            double_letter(last)
        )
    )


    random.shuffle(
        variations
    )


    for new_first, new_last in variations:

        new_first_clean = clean_text(
            new_first
        )

        new_last_clean = clean_text(
            new_last
        )


        key = (
            new_first_clean,
            new_last_clean
        )


        if key not in used_names:

            return {

                "first":
                    new_first,

                "last":
                    new_last,

                "first_clean":
                    new_first_clean,

                "last_clean":
                    new_last_clean

            }


    return None


# ============================================================
# MEMBUAT USERNAME
# ============================================================

def make_username(
    first,
    last,
    used_usernames
):

    first_clean = clean_text(
        first
    )

    last_clean = clean_text(
        last
    )


    # --------------------------------------------
    # Base username
    # --------------------------------------------

    bases = [

        first_clean
        + last_clean,

        first_clean
        + first_clean[-1]
        + last_clean,

        first_clean
        + last_clean
        + last_clean[-1],

        first_clean
        + first_clean[-1]
        + last_clean
        + last_clean[-1]

    ]


    # Hapus base yang sama

    bases = list(
        dict.fromkeys(
            bases
        )
    )


    # --------------------------------------------
    # Angka WAJIB
    #
    # 1 sampai 3 angka
    # --------------------------------------------

    for base in bases:

        for _ in range(500):

            number = random.randint(
                1,
                999
            )


            username = (
                base
                + str(number)
            )


            if username not in used_usernames:

                return username


    return None


# ============================================================
# MEMILIH NAMA
# ============================================================

def choose_names(
    records,
    amount,
    used_names
):

    selected = []

    used_first_today = set()


    # ========================================================
    # TAHAP 1
    # Ambil nama yang belum pernah digunakan
    # ========================================================

    fresh_candidates = [

        record

        for record in records

        if (
            record["first_clean"],
            record["last_clean"]
        )
        not in used_names

    ]


    random.shuffle(
        fresh_candidates
    )


    for record in fresh_candidates:

        first = record[
            "first_clean"
        ]


        # Nama depan tidak boleh sama
        # dalam batch yang sama

        if first in used_first_today:

            continue


        selected.append(
            record
        )


        used_first_today.add(
            first
        )


        if len(selected) >= amount:

            return selected


    # ========================================================
    # TAHAP 2
    #
    # Kalau nama fresh sudah tidak cukup,
    # gunakan nama lama dengan modifikasi.
    # ========================================================

    old_candidates = list(
        records
    )


    random.shuffle(
        old_candidates
    )


    for record in old_candidates:

        original_first = record[
            "first_clean"
        ]


        # Jangan gunakan nama depan
        # yang sudah ada dalam batch

        if (
            original_first
            in used_first_today
        ):

            continue


        variation = create_name_variation(

            record["first"],

            record["last"],

            used_names

        )


        if variation is None:

            continue


        new_first_clean = variation[
            "first_clean"
        ]


        if (
            new_first_clean
            in used_first_today
        ):

            continue


        selected.append({

            "first":
                variation["first"],

            "last":
                variation["last"],

            "first_clean":
                variation["first_clean"],

            "last_clean":
                variation["last_clean"]

        })


        used_first_today.add(
            new_first_clean
        )


        if len(selected) >= amount:

            return selected


    return selected


# ============================================================
# SIMPAN HISTORY GENERATE
# ============================================================

def append_history(
    results,
    requested_amount
):

    file_exists = (
        HISTORY_FILE.exists()
    )


    now = datetime.now()


    try:

        with open(
            HISTORY_FILE,
            "a",
            encoding="utf-8",
            newline=""
        ) as file:

            fields = [

                "tanggal",

                "jam",

                "jumlah_diminta",

                "jumlah_berhasil",

                "nama",

                "username"

            ]


            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )


            if not file_exists:

                writer.writeheader()


            for item in results:

                writer.writerow({

                    "tanggal":
                        now.strftime(
                            "%Y-%m-%d"
                        ),

                    "jam":
                        now.strftime(
                            "%H:%M:%S"
                        ),

                    "jumlah_diminta":
                        requested_amount,

                    "jumlah_berhasil":
                        len(results),

                    "nama":
                        item["name"],

                    "username":
                        item["username"]

                })


    except Exception as error:

        print()
        print(
            "Peringatan: history gagal disimpan."
        )

        print(error)


# ============================================================
# GENERATE
# ============================================================

def generate(amount):

    records = load_database()


    print()
    print(
        "Database ditemukan :",
        DATABASE_FILE.name
    )

    print(
        "Nama terbaca       :",
        len(records)
    )

    print()


    if not records:

        print(
            "Tidak ada nama yang berhasil dibaca."
        )

        print()

        print(
            "Contoh isi database:"
        )

        print()

        print(
            "Jaka Kartika"
        )

        print(
            "Rina Putri"
        )

        print(
            "Daniel Smith"
        )

        print()

        return []


    used_names = load_used_names()

    used_usernames = (
        load_used_usernames()
    )


    selected = choose_names(

        records,

        amount,

        used_names

    )


    if not selected:

        print(
            "Tidak ada nama yang memenuhi aturan."
        )

        return []


    results = []


    for record in selected:

        username = make_username(

            record["first"],

            record["last"],

            used_usernames

        )


        if username is None:

            continue


        name = (

            record["first"]
            + " "
            + record["last"]

        )


        used_usernames.add(
            username
        )


        used_names.add(

            (
                record["first_clean"],
                record["last_clean"]
            )

        )


        results.append({

            "name":
                name,

            "username":
                username

        })


    # --------------------------------------------
    # Simpan database penggunaan
    # --------------------------------------------

    save_used_names(
        used_names
    )


    save_used_usernames(
        used_usernames
    )


    # --------------------------------------------
    # Simpan history
    # --------------------------------------------

    append_history(

        results,

        amount

    )


    # ========================================================
    # HASIL USERNAME
    #
    # MENGGUNAKAN "w"
    #
    # Jadi hasil generate sebelumnya akan diganti.
    # Tidak menumpuk.
    # ========================================================

    try:

        with open(

            OUTPUT_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            for item in results:

                file.write(

                    item["username"]

                    + "\n"

                )


    except Exception as error:

        print()

        print(
            "Gagal menyimpan hasil username."
        )

        print(error)


    return results


# ============================================================
# STATISTIK
# ============================================================

def show_stats():

    records = load_database()

    used_names = load_used_names()


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    today_count = 0

    total_count = 0


    if HISTORY_FILE.exists():

        try:

            with open(

                HISTORY_FILE,

                "r",

                encoding="utf-8-sig",

                newline=""

            ) as file:


                reader = csv.DictReader(
                    file
                )


                for row in reader:

                    total_count += 1


                    if (
                        row.get("tanggal")
                        == today
                    ):

                        today_count += 1


        except Exception:

            pass


    unique_first = len({

        record["first_clean"]

        for record in records

    })


    unique_combinations = len({

        (
            record["first_clean"],

            record["last_clean"]

        )

        for record in records

    })


    remaining = max(

        0,

        unique_combinations
        - len(used_names)

    )


    print()

    print("=" * 60)

    print(
        "STATISTIK GENERATOR"
    )

    print("=" * 60)

    print()

    print(
        "Database              :",
        DATABASE_FILE.name
    )

    print(
        "Nama terbaca          :",
        len(records)
    )

    print(
        "Nama depan unik       :",
        unique_first
    )

    print(
        "Kombinasi nama        :",
        unique_combinations
    )

    print()

    print(
        "Generate hari ini     :",
        today_count
    )

    print(
        "Total generate        :",
        total_count
    )

    print(
        "Kombinasi belum pakai :",
        remaining
    )

    print()

    print("=" * 60)


# ============================================================
# RESET HISTORY
# ============================================================

def reset_history():

    print()

    print(
        "PERINGATAN!"
    )

    print(
        "Ini akan menghapus:"
    )

    print(
        "- generator_history.csv"
    )

    print(
        "- used_names.csv"
    )

    print(
        "- used_usernames.txt"
    )

    print()

    print(
        "database_nama.txt TIDAK akan dihapus."
    )

    print(
        "hasil_username.txt TIDAK akan dihapus."
    )

    print()


    confirmation = input(
        "Ketik RESET untuk melanjutkan: "
    ).strip()


    if confirmation != "RESET":

        print()

        print(
            "Reset dibatalkan."
        )

        return


    files = [

        HISTORY_FILE,

        USED_NAMES_FILE,

        USED_USERNAMES_FILE

    ]


    for file in files:

        try:

            if file.exists():

                file.unlink()

        except Exception as error:

            print()

            print(
                "Gagal menghapus:",
                file.name
            )

            print(error)


    print()

    print(
        "History berhasil direset."
    )


# ============================================================
# MENU UTAMA
# ============================================================

def main():

    while True:

        print()

        print("=" * 60)

        print(
            "              GENERATOR NAMA"
        )

        print("=" * 60)

        print()

        print(
            "1. GAS Generate Nama"
        )

        print(
            "2. Statistik"
        )

        print(
            "3. Reset history"
        )

        print(
            "4. Metu"
        )

        print()


        choice = input(
            "Pilih menu: "
        ).strip()


        # ====================================================
        # GENERATE
        # ====================================================

        if choice == "1":

            try:

                amount = int(

                    input(
                        "Piro Username Seng Kate digenerate= "
                    )

                )


            except ValueError:

                print()

                print(
                    "Masukkan angka yang benar."
                )

                continue


            if amount <= 0:

                print()

                print(
                    "Jumlah harus lebih dari 0."
                )

                continue


            print()

            print(
                "Sedang generate..."
            )


            results = generate(
                amount
            )


            if results:

                print()

                print("=" * 60)

                print(
                    "USERNAME HASIL GENERATE"
                )

                print("=" * 60)

                print()


                # --------------------------------------------
                # HANYA USERNAME
                # --------------------------------------------

                for item in results:

                    print(
                        item["username"]
                    )


                print()

                print("=" * 60)

                print()

                print(
                    "Berhasil generate:",
                    len(results),
                    "username"
                )

                print()

                print(
                    "Hasil tersimpan di:"
                )

                print(
                    OUTPUT_FILE.name
                )


        # ====================================================
        # STATISTIK
        # ====================================================

        elif choice == "2":

            show_stats()


        # ====================================================
        # RESET
        # ====================================================

        elif choice == "3":

            reset_history()


        # ====================================================
        # KELUAR
        # ====================================================

        elif choice == "4":

            print()

            print(
                "Program selesai."
            )

            break


        else:

            print()

            print(
                "Pilihan tidak tersedia."
            )


# ============================================================
# JALANKAN PROGRAM
# ============================================================

if __name__ == "__main__":

    try:

        main()


    except KeyboardInterrupt:

        print()

        print(
            "Program dihentikan."
        )


    except Exception as error:

        print()

        print("=" * 60)

        print(
            "TERJADI ERROR"
        )

        print("=" * 60)

        print()

        print(
            error
        )

        print()

        input(
            "Tekan ENTER untuk keluar..."
        )
