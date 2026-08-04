# ==========================
# HANDLE MESSAGE
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mode = context.user_data.get("mode")

    user_id = update.effective_user.id

    text = update.message.text

    emails = []

    for line in text.splitlines():

        line = line.strip()

        if "@" in line:

            match = re.search(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                line,
            )

            if match:

                emails.append(match.group(0).lower())

    if mode == "save":

        save_emails(user_id, emails)

        context.user_data["mode"] = None

        await update.message.reply_text(
            f"✅ Berhasil menyimpan {len(emails)} email."
        )

        return

    if mode == "check":

        my_emails = get_emails(user_id)

        result = compare_emails(my_emails, emails)

        context.user_data["mode"] = None

        message = (
            "📊 HASIL PENGECEKAN\n\n"
            f"Email saya : {result['total_my']}\n"
            f"Email bad : {result['total_bad']}\n"
            f"Cocok : {result['matched_count']}\n\n"
        )

        if result["matched"]:

            message += "❌ Email Bad:\n\n"

            for email in result["matched"]:

                message += f"{email}\n"

        else:

            message += "✅ Tidak ada email Anda yang masuk daftar bad."

        await update.message.reply_text(message)
