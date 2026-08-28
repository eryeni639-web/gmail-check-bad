import asyncio
import re
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.storage import save_emails, get_emails, clear_emails
from bot.compare import compare_emails
from bot.generators.generator_api import generate_usernames, generate_iphone_uas

MAX_GENERATE = 5000


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💾 Simpan Gmail", callback_data="save")],
        [InlineKeyboardButton("🔍 Compare Bad Gmail", callback_data="check")],
        [
            InlineKeyboardButton("📋 List Gmail", callback_data="list"),
            InlineKeyboardButton("🗑 Clear", callback_data="clear"),
        ],
        [InlineKeyboardButton("📧 Name To Gmail", callback_data="name_to_gmail")],
        [InlineKeyboardButton("👤 Generate Username", callback_data="gen_username")],
        [InlineKeyboardButton("📱 Generate iPhone UA", callback_data="gen_ua")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    await update.message.reply_text(
        "👋 *Selamat Datang di Gmail Check Bot*\n\nSilakan pilih menu di bawah ini.",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Panduan Gmail Check Bot*\n\n"
        "💾 *Simpan Gmail* — menyimpan daftar Gmail Anda.\n\n"
        "🔍 *Compare Bad Gmail* — membandingkan Gmail tersimpan dengan daftar bad.\n\n"
        "📋 *List Gmail* — melihat Gmail yang tersimpan.\n\n"
        "🗑 *Clear* — menghapus Gmail tersimpan.\n\n"
        "📧 *Name To Gmail* — menambahkan @gmail.com ke username.\n\n"
        "👤 *Generate Username* — membuat username dari database nama dan mengirim hasil TXT.\n\n"
        "📱 *Generate iPhone UA* — membuat User-Agent iPhone dan mengirim hasil TXT."
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "save"
    text = (
        "💾 *Simpan Gmail*\n\n"
        "Silakan kirim daftar Gmail Anda, satu per baris."
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    my_emails = get_emails(update.effective_user.id)
    if not my_emails:
        text = "❌ Belum ada Gmail yang tersimpan.\n\nGunakan *💾 Simpan Gmail* terlebih dahulu."
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")
        return
    context.user_data["mode"] = "check"
    text = "🔍 *Compare Bad Gmail*\n\nSilakan kirim daftar email bad, satu per baris."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emails = get_emails(update.effective_user.id)
    total = len(emails)
    text = f"📋 *Daftar Gmail*\n\n📧 Total Gmail tersimpan: *{total}*"
    if total:
        text += "\n\n10 Gmail pertama:\n\n" + "\n".join(emails[:10])
        if total > 10:
            text += f"\n\n... dan {total - 10} Gmail lainnya."
    else:
        text += "\n\nBelum ada Gmail yang tersimpan."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    emails = get_emails(user_id)
    if not emails:
        text = "📂 *Data Gmail*\n\nBelum ada Gmail yang tersimpan."
    else:
        total = len(emails)
        clear_emails(user_id)
        text = f"🗑 *Hapus Gmail*\n\n✅ Berhasil menghapus *{total}* Gmail."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def name_to_gmail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "name_to_gmail"
    text = "🔤 *Name To Gmail*\n\nKirim daftar username secara massal, satu per baris."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def generator_username_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "generate_username"
    text = (
        "👤 *Generate Username*\n\n"
        f"Kirim jumlah username yang ingin dibuat. Maksimal {MAX_GENERATE}.\n\n"
        "Contoh: `50`"
    )
    await update.callback_query.message.reply_text(text, parse_mode="Markdown")


async def generator_ua_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "generate_ua"
    keyboard = [[
        InlineKeyboardButton("🍎 Standard", callback_data="ua_standard"),
        InlineKeyboardButton("📱 + Model", callback_data="ua_model"),
    ]]
    await update.callback_query.message.reply_text(
        "📱 *Generate iPhone UA*\n\nPilih format User-Agent:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "save":
        await save_command(update, context)
    elif action == "check":
        await check_command(update, context)
    elif action == "list":
        await list_command(update, context)
    elif action == "clear":
        await clear_command(update, context)
    elif action == "help":
        await help_command(update, context)
    elif action == "name_to_gmail":
        await name_to_gmail_command(update, context)
    elif action == "gen_username":
        await generator_username_command(update, context)
    elif action == "gen_ua":
        await generator_ua_command(update, context)
    elif action in ("ua_standard", "ua_model"):
        if context.user_data.get("mode") != "generate_ua":
            return
        context.user_data["ua_with_model"] = action == "ua_model"
        context.user_data["mode"] = "generate_ua_count"
        await query.message.reply_text(
            f"📱 Mode: {'+ Model iPhone' if action == 'ua_model' else 'Standard'}\n\n"
            f"Kirim jumlah UA yang ingin dibuat. Maksimal {MAX_GENERATE}.\n\nContoh: `50`",
            parse_mode="Markdown",
        )
    elif action == "status":
        context.user_data["mode"] = "status"
        await query.message.reply_text("📧 *Cek Status Gmail*\n\nKirim daftar Gmail.", parse_mode="Markdown")


async def _send_txt(update: Update, filename: str, content: str, caption: str):
    data = BytesIO(content.encode("utf-8"))
    data.name = filename
    await update.message.reply_document(document=data, filename=filename, caption=caption, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if not mode or not update.message or not update.message.text:
        return
    text = update.message.text.strip()

    if mode in ("generate_username", "generate_ua_count"):
        if not text.isdigit():
            await update.message.reply_text("❌ Masukkan jumlah dalam angka. Contoh: 50")
            return
        count = int(text)
        if count < 1 or count > MAX_GENERATE:
            await update.message.reply_text(f"❌ Jumlah harus antara 1 dan {MAX_GENERATE}.")
            return

        current_mode = mode
        with_model = bool(context.user_data.get("ua_with_model", False))
        context.user_data["mode"] = None

        status = await update.message.reply_text("⏳ Sedang generate, tunggu sebentar...")
        try:
            if current_mode == "generate_username":
                usernames, output = await asyncio.to_thread(generate_usernames, count)
                if not usernames:
                    await status.edit_text("❌ Tidak ada username yang berhasil dibuat. Periksa database_nama.txt dan history.")
                    return
                content = output.read_text(encoding="utf-8")
                await status.delete()
                await _send_txt(
                    update,
                    "hasil_username.txt",
                    content,
                    f"✅ *Generate Username selesai*\n\n📊 Berhasil: *{len(usernames)}* username",
                )
            else:
                uas, output = await asyncio.to_thread(generate_iphone_uas, count, with_model)
                if not uas:
                    await status.edit_text("❌ Tidak ada UA yang berhasil dibuat.")
                    return
                content = output.read_text(encoding="utf-8")
                await status.delete()
                await _send_txt(
                    update,
                    "hasil_iphone_ua.txt",
                    content,
                    f"✅ *Generate iPhone UA selesai*\n\n📊 Berhasil: *{len(uas)}* UA\n📱 Mode: *{'+ Model' if with_model else 'Standard'}*",
                )
        except Exception as exc:
            await status.edit_text(f"❌ Generator gagal:\n`{str(exc)[:3500]}`", parse_mode="Markdown")
        return

    if mode == "name_to_gmail":
        usernames = [line.strip() for line in text.splitlines() if line.strip()]
        results = [u if u.lower().endswith("@gmail.com") else f"{u}@gmail.com" for u in usernames]
        context.user_data["mode"] = None
        if not results:
            await update.message.reply_text("❌ Tidak ada username yang ditemukan.")
            return
        await _send_txt(update, "name_to_gmail.txt", "\n".join(results) + "\n", f"✅ *Name To Gmail selesai!*\n\n📊 Total: *{len(results)}* username")
        return

    emails = []
    for line in text.splitlines():
        match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", line.strip())
        if match:
            emails.append(match.group(0).lower())

    if mode == "save":
        save_emails(update.effective_user.id, emails)
        context.user_data["mode"] = None
        await update.message.reply_text(f"✅ Berhasil menyimpan {len(emails)} Gmail.")
        return

    if mode == "check":
        result = compare_emails(get_emails(update.effective_user.id), emails)
        context.user_data["mode"] = None
        if result["matched"]:
            message = (
                "❌ *HASIL PENGECEKAN*\n\n"
                f"📧 Email Saya : {result['total_my']}\n"
                f"🚫 Email Bad : {result['total_bad']}\n"
                f"⚠️ Cocok : {result['matched_count']}\n\n"
                "*Daftar Email Bad:*\n" + "\n".join(f"• `{e}`" for e in result["matched"])
            )
        else:
            message = (
                "✅ *HASIL PENGECEKAN*\n\n"
                f"📧 Email Saya : {result['total_my']}\n"
                f"🚫 Email Bad : {result['total_bad']}\n\n"
                "Tidak ada Gmail Anda yang masuk daftar bad."
            )
        await update.message.reply_text(message, parse_mode="Markdown")
        return

    if mode == "status":
        context.user_data["mode"] = None
        await update.message.reply_text(
            "🚧 *Fitur Cek Status Gmail*\n\nFitur ini masih dalam tahap pengembangan.\n\n"
            f"Jumlah Gmail diterima: {len(emails)}",
            parse_mode="Markdown",
        )
