import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

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

    keyboard = [

        [
            InlineKeyboardButton(
                "📧 Cek Status Gmail",
                callback_data="cek_status"
            )
        ],

        [
            InlineKeyboardButton(
                "💾 Simpan Gmail",
                callback_data="save"
            ),

            InlineKeyboardButton(
                "📋 List Gmail",
                callback_data="list"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑 Hapus Semua",
                callback_data="clear"
            )
        ],

        [
            InlineKeyboardButton(
                "❓ Bantuan",
                callback_data="help"
            )
        ]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Selamat Datang di Gmail Check Bot\n\n"
        "Silakan pilih menu di bawah ini.",
        reply_markup=reply_markup
    )


# ==========================
# HELP
# ==========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Cara menggunakan bot:\n\n"
        "1. Ketik /save\n"
        "2. Kirim daftar Gmail Anda\n\n"
        "3. Ketik /check\n"
        "4. Kirim daftar email bad\n\n"
        "Bot akan mencari email yang cocok."
    )


# ==========================
# SAVE
# ==========================

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["mode"] = "save"

    await update.message.reply_text(
        "📥 Kirim daftar Gmail Anda.\n\n"
        "Contoh:\n"
        "gmail1@gmail.com\n"
        "gmail2@gmail.com"
    )


# ==========================
# CHECK
# ==========================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    my_emails = get_emails(update.effective_user.id)

    if not my_emails:

        await update.message.reply_text(
            "❌ Belum ada email yang disimpan.\nGunakan /save terlebih dahulu."
        )
        return

    context.user_data["mode"] = "check"

    await update.message.reply_text(
        "📥 Kirim daftar email bad."
    )


# ==========================
# LIST
# ==========================

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    emails = get_emails(update.effective_user.id)

    await update.message.reply_text(
        f"📊 Total email tersimpan: {len(emails)}"
    )


# ==========================
# CLEAR
# ==========================

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    clear_emails(update.effective_user.id)

    await update.message.reply_text(
        "✅ Semua email berhasil dihapus."
    )


# ==========================
# HANDLE MESSAGE
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mode = context.user_data.get("mode")

    if mode is None:
        return

    text = update.message.text

    emails = []

    for line in text.splitlines():

        line = line.strip()

        match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            line,
        )

        if match:
            emails.append(match.group(0).lower())

    if mode == "save":

        save_emails(update.effective_user.id, emails)

        context.user_data["mode"] = None

        await update.message.reply_text(
            f"✅ Berhasil menyimpan {len(emails)} email."
        )

        return

    if mode == "check":

        my_emails = get_emails(update.effective_user.id)

        result = compare_emails(my_emails, emails)

        context.user_data["mode"] = None

        if result["matched"]:

            pesan = (
                "❌ Ditemukan email yang BAD\n\n"
                f"Jumlah cocok: {result['matched_count']}\n\n"
            )

            for email in result["matched"]:
                pesan += f"• {email}\n"

        else:

            pesan = "✅ Tidak ada email Anda yang masuk daftar bad."

        await update.message.reply_text(pesan)
