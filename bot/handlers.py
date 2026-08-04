from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from bot.storage import (
    save_emails,
    get_emails,
    clear_emails,
)

from bot.compare import compare_emails


# ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Selamat datang di Gmail Check Bot\n\n"

        "Perintah:\n"
        "/save - Simpan email Gmail\n"
        "/check - Bandingkan email bad\n"
        "/list - Lihat jumlah email\n"
        "/clear - Hapus email\n"
        "/help - Bantuan"
    )

    await update.message.reply_text(text)


# ==========================
# HELP
# ==========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "Cara penggunaan:\n\n"

        "1. /save\n"
        "Lalu kirim daftar Gmail.\n\n"

        "2. /check\n"
        "Lalu kirim daftar email bad.\n\n"

        "Bot akan mencari email yang cocok."
    )


# ==========================
# LIST
# ==========================

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    emails = get_emails(user_id)

    await update.message.reply_text(

        f"📊 Total email tersimpan : {len(emails)}"
    )


# ==========================
# CLEAR
# ==========================

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    clear_emails(user_id)

    await update.message.reply_text(

        "✅ Semua email berhasil dihapus."
    )

# ==========================
# SAVE
# ==========================

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["mode"] = "save"

    await update.message.reply_text(
        "📥 Kirim daftar Gmail Anda.\n\n"
        "Format:\n"
        "email1@gmail.com\n"
        "email2@gmail.com\n"
        "email3@gmail.com"
    )


# ==========================
# HANDLE MESSAGE
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mode = context.user_data.get("mode")

    if mode != "save":
        return

    user_id = update.effective_user.id

    text = update.message.text

    emails = []

    for line in text.splitlines():

        line = line.strip()

        if "@" in line:

            emails.append(line)

    save_emails(user_id, emails)

    context.user_data["mode"] = None

    await update.message.reply_text(

        f"✅ Berhasil menyimpan {len(emails)} email."
    )
