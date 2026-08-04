import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Selamat datang di Gmail Check Bot!\n\n"
        "Perintah yang tersedia:\n"
        "/save - Simpan daftar Gmail\n"
        "/check - Bandingkan dengan daftar email bad\n"
        "/list - Lihat jumlah email tersimpan\n"
        "/clear - Hapus semua email\n"
        "/help - Bantuan"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kirim /save untuk menyimpan email.\n"
        "Kirim /check untuk mengecek email bad."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN belum diatur.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot sedang berjalan...")

    app.run_polling()


if __name__ == "__main__":
    main()
