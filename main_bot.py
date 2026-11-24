import os
import time
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from host_engine import (
    ACTIVE_HOSTS,
    host_user_account,
    load_all_saved_sessions,
    logout_user_account,
    restore_all_saved_sessions,
    restart_user_account,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
START_TIME = time.time()


def build_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Help Menu", callback_data="menu_help")],
        [
            InlineKeyboardButton("Commands", callback_data="menu_cmds"),
            InlineKeyboardButton("Status", callback_data="menu_status"),
        ],
    ])


def help_html() -> str:
    return (
        "<b>Userbot Hoster Menu</b>\n\n"
        "<b>Bot Commands:</b>\n"
        "• <code>/host &lt;string_session&gt;</code> — Account host karein\n"
        "• <code>/restart</code> — Apna hosted bot restart karein\n"
        "• <code>/logout</code> — Account disconnect karein\n"
        "• <code>/status</code> — Status check karein\n\n"
        "<b>Userbot Commands (Account Se):</b>\n"
        "• <code>.tagall</code> — Group members tag karein\n"
        "• <code>.stoptagall</code> — Tagall stop karein\n"
        "• <code>.replyraid &lt;user_id&gt;</code> — DM random reply ON\n"
        "• <code>.dreplyraid &lt;user_id&gt;</code> — DM random reply OFF"
    )


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"<b>Welcome To Userbot Hoster</b>\n\n"
        f"Hi <b>{user.first_name}</b>! Host karne ke liye:\n"
        f"<code>/host YOUR_STRING_SESSION</code>\n\n"
        f"Menu ke liye <code>/help</code> bhejein."
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=build_keyboard())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_html(), parse_mode="HTML", reply_markup=build_keyboard())


async def host_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage: <code>/host YOUR_STRING_SESSION</code>",
            parse_mode="HTML",
        )
        return

    session_str = " ".join(context.args).strip()
    msg_box = await update.message.reply_text("Account host ho raha hai...")
    ok, res_msg = await host_user_account(update.effective_user.id, session_str, API_ID, API_HASH, persist=True)
    await msg_box.edit_text(res_msg)


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_box = await update.message.reply_text("Restart ho raha hai...")
    ok, res_msg = await restart_user_account(update.effective_user.id, API_ID, API_HASH)
    await msg_box.edit_text(res_msg)


async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, res_msg = await logout_user_account(update.effective_user.id)
    await update.message.reply_text(res_msg)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uptime = int(time.time() - START_TIME)
    await update.message.reply_text(
        f"<b>Bot Status</b>\n"
        f"• Uptime: <code>{uptime}s</code>\n"
        f"• Your Slot: <code>{'Active' if uid in ACTIVE_HOSTS else 'Inactive'}</code>\n"
        f"• Active Hosts: <code>{len(ACTIVE_HOSTS)}</code>",
        parse_mode="HTML",
    )


async def restartall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return

    saved_ids = list(load_all_saved_sessions().keys())
    all_ids = list(set(ACTIVE_HOSTS.keys()) | set(saved_ids))
    count = 0
    for uid in all_ids:
        ok, _ = await restart_user_account(uid, API_ID, API_HASH)
        if ok:
            count += 1
    await update.message.reply_text(f"Restarted {count}/{len(all_ids)} accounts.")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    await update.message.reply_text(f"Total Active Hosts: <code>{len(ACTIVE_HOSTS)}</code>", parse_mode="HTML")


async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_help":
        await query.edit_message_text(help_html(), parse_mode="HTML", reply_markup=build_keyboard())
    elif query.data == "menu_cmds":
        await query.edit_message_text(
            "<b>Commands</b>\n"
            "• <code>/host &lt;session&gt;</code>\n"
            "• <code>/restart</code>\n"
            "• <code>/logout</code>\n"
            "• <code>.tagall</code> / <code>.stoptagall</code>\n"
            "• <code>.replyraid &lt;id&gt;</code> / <code>.dreplyraid &lt;id&gt;</code>",
            parse_mode="HTML",
            reply_markup=build_keyboard(),
        )
    elif query.data == "menu_status":
        uid = query.from_user.id
        await query.edit_message_text(
            f"<b>Your Slot:</b> <code>{'Active' if uid in ACTIVE_HOSTS else 'Inactive'}</code>\n"
            f"<b>Active Hosts:</b> <code>{len(ACTIVE_HOSTS)}</code>",
            parse_mode="HTML",
            reply_markup=build_keyboard(),
        )


async def post_init(application: Application):
    if API_ID and API_HASH:
        await restore_all_saved_sessions(API_ID, API_HASH)


def main():
    if not BOT_TOKEN or not API_ID or not API_HASH:
        raise ValueError("BOT_TOKEN, API_ID, aur API_HASH set karein.")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("host", host_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
    app.add_handler(CommandHandler("logout", logout_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("restartall", restartall_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(button_cb))

    print("Heroku Hoster Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
