import asyncio
import re
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes

from bot.storage import save_emails, get_emails, clear_emails
from bot.compare import compare_emails
from bot.generators.generator_api import generate_usernames, generate_iphone_uas


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('💾 Simpan Gmail', callback_data='save')],
        [InlineKeyboardButton('🔍 Compare Bad Gmail', callback_data='check')],
        [InlineKeyboardButton('📋 List Gmail', callback_data='list'), InlineKeyboardButton('🗑 Clear', callback_data='clear')],
        [InlineKeyboardButton('📧 Name To Gmail', callback_data='name_to_gmail')],
        [InlineKeyboardButton('👤 Generator Username', callback_data='gen_username')],
        [InlineKeyboardButton('📱 Generator iPhone UA', callback_data='gen_ua')],
        [InlineKeyboardButton('📊 Status Gmail', callback_data='status')],
        [InlineKeyboardButton('❓ Bantuan', callback_data='help')],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = None
    await update.message.reply_text(
        '👋 *Selamat Datang di Gmail Check Bot*\n\nPilih fitur yang ingin digunakan:',
        parse_mode='Markdown', reply_markup=main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        '📖 *Panduan*\n\n'
        '💾 *Simpan Gmail* — menyimpan daftar Gmail per pengguna.\n\n'
        '🔍 *Compare Bad Gmail* — membandingkan Gmail tersimpan dengan daftar bad.\n\n'
        '📋 *List Gmail* — melihat Gmail tersimpan.\n\n'
        '🗑 *Clear* — menghapus Gmail tersimpan.\n\n'
        '📧 *Name To Gmail* — menambahkan @gmail.com ke username secara massal.\n\n'
        '👤 *Generator Username* — membuat username dan mengirim hasil sebagai TXT.\n\n'
        '📱 *Generator iPhone UA* — membuat UA iPhone unik dan mengirim hasil sebagai TXT.\n\n'
        '📊 *Status Gmail* — placeholder status checker yang ada di versi repository saat ini.'
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')


async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'save'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text(
        '💾 *Simpan Gmail*\n\nKirim daftar Gmail, satu per baris.', parse_mode='Markdown'
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_emails(update.effective_user.id):
        target = update.callback_query.message if update.callback_query else update.message
        if update.callback_query:
            await update.callback_query.answer()
        await target.reply_text('❌ Belum ada Gmail tersimpan. Gunakan *Simpan Gmail* terlebih dahulu.', parse_mode='Markdown')
        return
    context.user_data['mode'] = 'check'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text('🔍 *Compare Bad Gmail*\n\nKirim daftar email bad, satu per baris.', parse_mode='Markdown')


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emails = get_emails(update.effective_user.id)
    text = f'📋 *Daftar Gmail*\n\n📧 Total Gmail tersimpan: *{len(emails)}*'
    if emails:
        text += '\n\n' + '\n'.join(emails[:10])
        if len(emails) > 10:
            text += f'\n\n... dan {len(emails)-10} Gmail lainnya.'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text(text, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    emails = get_emails(user_id)
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    if not emails:
        await target.reply_text('📂 Belum ada Gmail yang tersimpan.')
        return
    clear_emails(user_id)
    await target.reply_text(f'🗑 Berhasil menghapus *{len(emails)}* Gmail.', parse_mode='Markdown')


async def name_to_gmail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'name_to_gmail'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text(
        '🔤 *Name To Gmail*\n\nKirim username satu per baris. Bot akan menambahkan `@gmail.com`.',
        parse_mode='Markdown'
    )


async def username_generator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gen_username_count'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text('👤 *Generate Username*\n\nMasukkan jumlah username yang ingin dibuat.\nContoh: `50`', parse_mode='Markdown')


async def ua_generator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gen_ua_count'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text('📱 *Generate iPhone UA*\n\nMasukkan jumlah UA yang ingin dibuat.\nContoh: `50`', parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'status'
    target = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
    await target.reply_text('📊 *Status Gmail*\n\nKirim daftar Gmail yang ingin dicek.\n\nCatatan: status checker belum diimplementasikan pada repository saat ini.', parse_mode='Markdown')


async def send_generated_file(update: Update, path, caption):
    with open(path, 'rb') as f:
        await update.message.reply_document(
            document=InputFile(f, filename=path.name),
            caption=caption,
            parse_mode='Markdown'
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action = query.data
    await query.answer()

    actions = {
        'save': save_command,
        'check': check_command,
        'list': list_command,
        'clear': clear_command,
        'help': help_command,
        'name_to_gmail': name_to_gmail_command,
        'gen_username': username_generator_command,
        'gen_ua': ua_generator_command,
        'status': status_command,
    }
    handler = actions.get(action)
    if handler:
        await handler(update, context)


EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def extract_emails(text):
    return [m.group(0).lower() for m in EMAIL_RE.finditer(text)]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    if not mode or not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if mode == 'name_to_gmail':
        results = []
        for username in text.splitlines():
            username = username.strip()
            if not username:
                continue
            results.append(username if username.lower().endswith('@gmail.com') else f'{username}@gmail.com')
        context.user_data['mode'] = None
        if not results:
            await update.message.reply_text('❌ Tidak ada username yang ditemukan.')
            return
        data = BytesIO(('\n'.join(results) + '\n').encode('utf-8'))
        data.name = 'name_to_gmail.txt'
        await update.message.reply_document(document=data, filename=data.name, caption=f'✅ Selesai. Total: {len(results)} username.')
        return

    if mode == 'save':
        emails = extract_emails(text)
        if not emails:
            await update.message.reply_text('❌ Tidak menemukan alamat Gmail. Kirim ulang daftar email.')
            return
        save_emails(update.effective_user.id, emails)
        context.user_data['mode'] = None
        await update.message.reply_text(f'✅ Berhasil menyimpan {len(emails)} Gmail.')
        return

    if mode == 'check':
        emails = extract_emails(text)
        my_emails = get_emails(update.effective_user.id)
        result = compare_emails(my_emails, emails)
        context.user_data['mode'] = None
        if result['matched']:
            body = '\n'.join(f'• `{email}`' for email in result['matched'])
            await update.message.reply_text(
                f"❌ *HASIL PENGECEKAN*\n\n📧 Email Saya: {result['total_my']}\n🚫 Email Bad: {result['total_bad']}\n⚠️ Cocok: {result['matched_count']}\n\n*Daftar:*\n{body}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"✅ *HASIL PENGECEKAN*\n\n📧 Email Saya: {result['total_my']}\n🚫 Email Bad: {result['total_bad']}\n\nTidak ada Gmail Anda yang masuk daftar bad.",
                parse_mode='Markdown'
            )
        return

    if mode == 'status':
        context.user_data['mode'] = None
        await update.message.reply_text(f'🚧 Status checker belum tersedia. Jumlah Gmail diterima: {len(extract_emails(text))}.')
        return

    if mode == 'gen_username_count':
        try:
            count = int(text)
            if count <= 0 or count > 10000:
                raise ValueError
        except ValueError:
            await update.message.reply_text('❌ Masukkan jumlah antara 1 sampai 10000.')
            return

        context.user_data['mode'] = None
        msg = await update.message.reply_text(f'⏳ Sedang membuat {count} username...')
        try:
            path = await asyncio.to_thread(generate_usernames, count)
            await msg.edit_text(f'✅ Selesai membuat {count} username.\n\n📄 File TXT sedang dikirim...')
            await send_generated_file(update, path, f'👤 *Generate Username selesai*\n📊 Berhasil: {count}\n📄 Hasil: `{path.name}`')
        except Exception as exc:
            await msg.edit_text(f'❌ Gagal generate username:\n{exc}')
        return

    if mode == 'gen_ua_count':
        try:
            count = int(text)
            if count <= 0 or count > 10000:
                raise ValueError
        except ValueError:
            await update.message.reply_text('❌ Masukkan jumlah antara 1 sampai 10000.')
            return

        context.user_data['ua_count'] = count
        context.user_data['mode'] = 'gen_ua_model'
        await update.message.reply_text(
            f'📱 Jumlah: *{count}*\n\nPilih format UA:',
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('🍎 Standard', callback_data='ua_standard')],
                [InlineKeyboardButton('📱 + Model iPhone', callback_data='ua_model')],
                [InlineKeyboardButton('❌ Batal', callback_data='ua_cancel')],
            ])
        )
        return

    if mode == 'gen_ua_model':
        await update.message.reply_text('Gunakan tombol pilihan format UA di atas.')


async def ua_format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    if action == 'ua_cancel':
        context.user_data['mode'] = None
        context.user_data.pop('ua_count', None)
        await query.message.reply_text('❌ Generate UA dibatalkan.')
        return

    count = context.user_data.get('ua_count')
    if not count:
        context.user_data['mode'] = 'gen_ua_count'
        await query.message.reply_text('Masukkan jumlah UA terlebih dahulu.')
        return

    with_model = action == 'ua_model'
    context.user_data['mode'] = None
    context.user_data.pop('ua_count', None)
    msg = await query.message.reply_text(f'⏳ Sedang membuat {count} UA iPhone...')
    try:
        path = await asyncio.to_thread(generate_iphone_uas, count, with_model)
        await msg.edit_text(f'✅ Selesai membuat {count} UA.\n\n📄 File TXT sedang dikirim...')
        caption = f"📱 *Generate iPhone UA selesai*\n📊 Berhasil: {count}\n🔧 Model: {'Ya' if with_model else 'Tidak'}\n📄 Hasil: `{path.name}`"
        with open(path, 'rb') as f:
            await query.message.reply_document(document=InputFile(f, filename=path.name), caption=caption, parse_mode='Markdown')
    except Exception as exc:
        await msg.edit_text(f'❌ Gagal generate UA:\n{exc}')
