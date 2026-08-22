import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

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

    keyboard = [

        [
            InlineKeyboardButton(
                "💾 Simpan Gmail",
                callback_data="save",
            )
        ],

        [
            InlineKeyboardButton(
                "🔍 Compare Bad Gmail",
                callback_data="check",
            )
        ],

        [
            InlineKeyboardButton(
                "📋 List Gmail",
                callback_data="list",
            ),
            InlineKeyboardButton(
                "🗑 Clear",
                callback_data="clear",
            ),
        ],
        [
            InlineKeyboardButton(
                "📧 Name To Gmail",
                callback_data="name_to_gmail",
            )
        [
            InlineKeyboardButton(
                "❓ Bantuan",
                callback_data="help",
            )
        ],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "👋 *Selamat Datang di Gmail Check Bot*\n\n"
        "Silakan pilih menu di bawah ini."
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ==========================
# HELP
# ==========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "📖 *Panduan Gmail Check Bot*\n\n"
        "💾 *Simpan Gmail*\n"
        "Menyimpan daftar Gmail Anda.\n\n"
        "🔍 *Compare Bad Gmail*\n"
        "Membandingkan Gmail Anda dengan daftar bad.\n\n"
        "📋 *List Gmail*\n"
        "Melihat jumlah Gmail yang tersimpan.\n\n"
        "🗑 *Clear*\n"
        "Menghapus semua Gmail yang tersimpan.\n\n"
        "📧 *Cek Status Gmail*\n"
        "Fitur akan ditambahkan berikutnya."
    )

    if update.message:

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )

# ==========================
# SAVE
# ==========================

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["mode"] = "save"

    text = (
        "💾 *Simpan Gmail*\n\n"
        "Silakan kirim daftar Gmail Anda.\n\n"
        "Contoh:\n\n"
        "gmail1@gmail.com\n"
        "gmail2@gmail.com\n"
        "gmail3@gmail.com"
    )

    if update.message:

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )


# ==========================
# CHECK
# ==========================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    my_emails = get_emails(update.effective_user.id)

    if not my_emails:

        text = (
            "❌ Belum ada Gmail yang tersimpan.\n\n"
            "Gunakan menu *💾 Simpan Gmail* terlebih dahulu."
        )

        if update.message:

            await update.message.reply_text(
                text,
                parse_mode="Markdown",
            )

        elif update.callback_query:

            await update.callback_query.answer()

            await update.callback_query.message.reply_text(
                text,
                parse_mode="Markdown",
            )

        return

    context.user_data["mode"] = "check"

    text = (
        "🔍 *Compare Bad Gmail*\n\n"
        "Silakan kirim daftar email bad.\n\n"
        "Bot akan membandingkan dengan Gmail yang telah disimpan."
    )

    if update.message:

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )

# ==========================
# LIST
# ==========================

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    emails = get_emails(update.effective_user.id)

    total = len(emails)

    text = (
        "📋 *Daftar Gmail*\n\n"
        f"📧 Total Gmail tersimpan: *{total}*"
    )

    if total > 0:

        preview = "\n".join(emails[:10])

        text += (
            "\n\n"
            "10 Gmail pertama:\n\n"
            f"{preview}"
        )

        if total > 10:
            text += f"\n\n... dan {total - 10} Gmail lainnya."

    else:

        text += "\n\nBelum ada Gmail yang tersimpan."

    if update.message:

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )


# ==========================
# CLEAR
# ==========================

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    emails = get_emails(user_id)

    if not emails:

        text = (
            "📂 *Data Gmail*\n\n"
            "Belum ada Gmail yang tersimpan."
        )

        if update.message:

            await update.message.reply_text(
                text,
                parse_mode="Markdown",
            )

        elif update.callback_query:

            await update.callback_query.answer()

            await update.callback_query.message.reply_text(
                text,
                parse_mode="Markdown",
            )

        return

    total = len(emails)

    clear_emails(user_id)

    text = (
        "🗑 *Hapus Gmail*\n\n"
        f"✅ Berhasil menghapus *{total}* Gmail."
    )

    if update.message:

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )

# ==========================
# NAME TO GMAIL
# ==========================

async def name_to_gmail_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["mode"] = "name_to_gmail"

    text = (
        "🔤 *Name To Gmail*\n\n"
        "Kirim daftar username secara massal.\n"
        "Bot hanya akan menambahkan `@gmail.com` "
        "tanpa mengubah username.\n\n"
        "Contoh:\n\n"
        "johnsmith\n"
        "michaelandrew27\n"
        "alexanderbrown"
    )

    if update.message:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    elif update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
        )

# ==========================
# BUTTON HANDLER
# ==========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    action = query.data

    # ======================
    # SAVE
    # ======================

    if action == "save":

        await save_command(update, context)
        return

    # ======================
    # CHECK
    # ======================

    if action == "check":

        await check_command(update, context)
        return

    # ======================
    # LIST
    # ======================

    if action == "list":

        await list_command(update, context)
        return

    # ======================
    # CLEAR
    # ======================

    if action == "clear":

        await clear_command(update, context)
        return

    # ======================
    # HELP
    # ======================

    if action == "help":

        await help_command(update, context)
        return

# ======================
# NAME TO GMAIL
# ======================

if action == "name_to_gmail":

    await name_to_gmail_command(
        update,
        context
    )

    return

    # ======================
    # STATUS
    # ======================

    if action == "status":

        context.user_data["mode"] = "status"

        await query.message.reply_text(
            "📧 *Cek Status Gmail*\n\n"
            "Kirim daftar Gmail yang ingin dicek.\n\n"
            "Contoh:\n"
            "gmail1@gmail.com\n"
            "gmail2@gmail.com",
            parse_mode="Markdown",
        )

        return

# ==========================
# HANDLE MESSAGE
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mode = context.user_data.get("mode")

    if mode is None:
        return

    text = update.message.text or ""

    emails = []

    for line in text.splitlines():

        line = line.strip()

        match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            line,
        )

        if match:
            emails.append(match.group(0).lower())

    # ==========================
    # SAVE
    # ==========================

    if mode == "save":

        save_emails(
            update.effective_user.id,
            emails,
        )

        context.user_data["mode"] = None

        await update.message.reply_text(
            f"✅ Berhasil menyimpan {len(emails)} Gmail."
        )

        return

    # ==========================
    # CHECK
    # ==========================

    if mode == "check":

        my_emails = get_emails(
            update.effective_user.id
        )

        result = compare_emails(
            my_emails,
            emails,
        )

        context.user_data["mode"] = None

        if result["matched"]:

            message = (
                "❌ *HASIL PENGECEKAN*\n\n"
                f"📧 Email Saya : {result['total_my']}\n"
                f"🚫 Email Bad : {result['total_bad']}\n"
                f"⚠️ Cocok : {result['matched_count']}\n\n"
                "*Daftar Email Bad:*\n"
            )

            for email in result["matched"]:
                message += f"\n• `{email}`"

        else:

            message = (
                "✅ *HASIL PENGECEKAN*\n\n"
                f"📧 Email Saya : {result['total_my']}\n"
                f"🚫 Email Bad : {result['total_bad']}\n\n"
                "Tidak ada Gmail Anda yang masuk daftar bad."
            )

        await update.message.reply_text(
            message,
            parse_mode="Markdown",
        )

        return

    # ==========================
    # STATUS (sementara)
    # ==========================

    if mode == "status":

        context.user_data["mode"] = None

        message = (
            "🚧 *Fitur Cek Status Gmail*\n\n"
            "Fitur ini masih dalam tahap pengembangan.\n\n"
            f"Jumlah Gmail diterima: {len(emails)}"
        )

        await update.message.reply_text(
            message,
            parse_mode="Markdown",
        )

        return
