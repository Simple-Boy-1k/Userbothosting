import os
import time
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from host_engine import (
    ACTIVE_HOSTS,
    PENDING_LOGINS,
    cancel_pending_login,
    get_meta_state,
    load_all_sessions,
    logout_user_account,
    restore_all_saved_sessions,
    restart_user_account,
    save_meta_state,
    send_login_code,
    submit_2fa_password,
    submit_otp_code,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DEFAULT_BANNER_URL = os.getenv("START_BANNER_URL", "")
SUPPORT_GROUP_URL = os.getenv("SUPPORT_GROUP_URL", "https://t.me/+bajyE84Lj-szODdh")
CRAFTED_BY = os.getenv("CRAFTED_BY", "@Simple_Boy_1k")
START_TIME = time.time()


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def is_sudo(uid: int) -> bool:
    meta = get_meta_state()
    return uid == OWNER_ID or uid in meta["sudos"]


def is_blocked(uid: int) -> bool:
    if uid == OWNER_ID:
        return False
    meta = get_meta_state()
    return uid in meta["blocked"]


def help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Help", callback_data="open_help")]
    ])


def start_caption_html() -> str:
    return (
        "<b>🏆 WELCOME TO THE PREMIUM USERBOT HOSTER BOT! 🏆</b>\n\n"
        "<b>🚀 UNLEASH THE POWER OF AUTOMATION WITH STYLE! 🚀</b>\n\n"
        f"<b>👑 CRAFTED BY: {CRAFTED_BY} 👑</b>\n\n"
        "<b>🔒 100% SECURE &amp; LIGHTNING FAST! 🔒</b>\n\n"
        "<b>✨ EXPLORE COMMANDS WITH /help OR TAP BELOW! ✨</b>"
    )


def help_text_html() -> str:
    return (
        "<b>🌟 PREMIUM HOSTER BOT COMMANDS 🌟</b>\n\n"
        "🔹 <code>/start</code> - LAUNCH THE BOT WITH A GRAND WELCOME\n"
        "🔹 <code>/help</code> - DISCOVER ALL COMMANDS\n"
        "🔹 <code>/commands</code> - EXPLORE USERBOT FEATURES\n"
        "🔹 <code>/host</code> - DEPLOY YOUR OWN USERBOT\n"
        "🔹 <code>/support</code> - REQUEST SUPPORT FROM ADMIN (FAST RESPONSE)\n"
        "🔹 <code>/restart</code> - REVIVE YOUR HOSTED USERBOT\n"
        "🔹 <code>/supportraid</code> - PRO SUPPORT RAID COMMAND (OWNERS / PREMIUM USERS ONLY)\n"
        "🔹 <code>/restartall</code> - RESTART ALL USERBOTS (OWNERS ONLY)\n"
        "🔹 <code>/refresh</code> - REFRESH BOT STATE (OWNERS ONLY)\n"
        "🔹 <code>/status</code> - CHECK YOUR USERBOT'S PULSE\n"
        "🔹 <code>/logout</code> - SAFELY LOG OUT YOUR USERBOT\n"
        "🔹 <code>/sudolist</code> - VIEW SUDO USERS (OWNERS ONLY)\n"
        "🔹 <code>/setdp</code> - SET DISPLAY PHOTO (OWNERS ONLY)\n"
        "🔹 <code>/block</code> - BLOCK A USER (OWNERS ONLY)\n"
        "🔹 <code>/unblock</code> - UNBLOCK A USER (OWNERS ONLY)\n"
        "🔹 <code>/blockeduser</code> - VIEW BLOCKED USERS (OWNERS ONLY)\n"
        "🔹 <code>/stats</code> - VIEW BOT STATISTICS (OWNERS ONLY)\n"
        "🔹 <code>/secretfunction</code> - VIEW SECRET COMMANDS (OWNERS ONLY)"
    )


async def guard(update: Update) -> bool:
    user = update.effective_user
    if not user:
        return False
    if is_blocked(user.id):
        if update.message:
            await update.message.reply_text("Aap is bot ke liye blocked hain.")
        return False
    return True


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    meta = get_meta_state()
    photo = meta["dp_url"] or DEFAULT_BANNER_URL
    caption = start_caption_html()

    if photo:
        try:
            await update.message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=help_keyboard(),
            )
            return
        except Exception:
            pass

    await update.message.reply_text(caption, parse_mode="HTML", reply_markup=help_keyboard())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    await update.message.reply_text(help_text_html(), parse_mode="HTML")


async def commands_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    txt = (
        "<b>⚡ USERBOT FEATURES ⚡</b>\n\n"
        "• <code>.ping</code> — Check userbot response\n"
        "• <code>.tagall</code> — Group members ko tag karein\n"
        "• <code>.stoptagall</code> — Tagall stop karein\n"
        "• <code>.replyraid &lt;user_id&gt;</code> — DM random reply ON\n"
        "• <code>.dreplyraid &lt;user_id&gt;</code> — DM random reply OFF"
    )
    await update.message.reply_text(txt, parse_mode="HTML")


async def host_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    uid = update.effective_user.id

    if uid in ACTIVE_HOSTS:
        await update.message.reply_text(
            "<b>Error Userbot Already Hosted!</b>\n"
            "Try <code>/restart</code> or <code>/logout</code>.\n"
            "Check <code>/commands</code>.",
            parse_mode="HTML",
        )
        return

    await cancel_pending_login(uid)
    await update.message.reply_text(
        f"Warning Join Our Support Group!\nJoin: <a href=\"{SUPPORT_GROUP_URL}\">Support Group</a>\nYou can still host.",
        parse_mode="HTML",
    )
    PENDING_LOGINS[uid] = {"step": "phone"}
    await update.message.reply_text("📱 Enter Phone Number (+91xxxxxxxxxx):")


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    uid = update.effective_user.id
    if uid in PENDING_LOGINS:
        await cancel_pending_login(uid)
        await update.message.reply_text("Host login process cancel kar diya gaya hai.")
    else:
        await update.message.reply_text("Koi active login process nahi hai.")


async def text_step_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not await guard(update):
        return

    uid = update.effective_user.id
    pending = PENDING_LOGINS.get(uid)
    if not pending:
        return

    text = update.message.text.strip()
    step = pending.get("step")

    if step == "phone":
        ok, res = await send_login_code(uid, text, API_ID, API_HASH)
        await update.message.reply_text(res)
        if not ok:
            PENDING_LOGINS.pop(uid, None)

    elif step == "otp":
        status, res = await submit_otp_code(uid, text, API_ID, API_HASH)
        if status == "done":
            wait_msg = await update.message.reply_text("🛸 Hosting userbot, please wait...")
            await wait_msg.edit_text(res)
        else:
            await update.message.reply_text(res)

    elif step == "2fa":
        wait_msg = await update.message.reply_text("🛸 Hosting userbot, please wait...")
        status, res = await submit_2fa_password(uid, text, API_ID, API_HASH)
        await wait_msg.edit_text(res)
        try:
            await update.message.delete()
        except Exception:
            pass


async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    await update.message.reply_text(
        f"Support ke liye Owner ID <code>{OWNER_ID}</code> par contact karein.",
        parse_mode="HTML",
    )


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    uid = update.effective_user.id
    saved = load_all_sessions()
    if uid not in ACTIVE_HOSTS and uid not in saved:
        await update.message.reply_text("Aapka koi hosted account nahi mila. Pehle /host likhein.")
        return

    msg = await update.message.reply_text("Processing Restarting Userbot...")
    _, res = await restart_user_account(uid, API_ID, API_HASH)
    await msg.edit_text(res)


async def supportraid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("Yeh command sirf Owner ya Sudo users ke liye hai.")
        return
    await update.message.reply_text("Support raid module ready (authorized access).")


async def restartall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    saved_ids = list(load_all_sessions().keys())
    all_ids = list(set(ACTIVE_HOSTS.keys()) | set(saved_ids))
    done = 0
    for uid in all_ids:
        ok, _ = await restart_user_account(uid, API_ID, API_HASH)
        if ok:
            done += 1
    await update.message.reply_text(f"Restarted {done}/{len(all_ids)} hosted accounts.")


async def refresh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    _ = get_meta_state()
    await update.message.reply_text("Bot state refreshed.")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    uid = update.effective_user.id
    uptime = int(time.time() - START_TIME)
    await update.message.reply_text(
        f"<b>Status</b>\n"
        f"• Uptime: <code>{uptime}s</code>\n"
        f"• Your Slot: <code>{'Running' if uid in ACTIVE_HOSTS else 'Not Hosted'}</code>\n"
        f"• Active Hosts: <code>{len(ACTIVE_HOSTS)}</code>",
        parse_mode="HTML",
    )


async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    ok, res = await logout_user_account(update.effective_user.id)
    await update.message.reply_text(res)


async def sudolist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    sudos = get_meta_state()["sudos"]
    if not sudos:
        await update.message.reply_text("Sudo list khali hai.")
        return
    lines = "\n".join(f"• <code>{u}</code>" for u in sudos)
    await update.message.reply_text(f"<b>Sudo Users:</b>\n{lines}", parse_mode="HTML")


async def setdp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    meta = get_meta_state()
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        file_id = update.message.reply_to_message.photo[-1].file_id
        meta["dp_url"] = file_id
        save_meta_state(meta)
        await update.message.reply_text("Display photo update ho gaya.")
        return
    if context.args:
        meta["dp_url"] = context.args[0].strip()
        save_meta_state(meta)
        await update.message.reply_text("Display photo URL save ho gaya.")
        return
    await update.message.reply_text("Photo reply karke /setdp likhein ya image URL dein.")


async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /block 123456789")
        return
    target = int(context.args[0])
    if target == OWNER_ID:
        await update.message.reply_text("Owner ko block nahi kiya ja sakta.")
        return
    meta = get_meta_state()
    if target not in meta["blocked"]:
        meta["blocked"].append(target)
        save_meta_state(meta)
    await update.message.reply_text(f"User {target} blocked.")


async def unblock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /unblock 123456789")
        return
    target = int(context.args[0])
    meta = get_meta_state()
    if target in meta["blocked"]:
        meta["blocked"].remove(target)
        save_meta_state(meta)
    await update.message.reply_text(f"User {target} unblocked.")


async def blockeduser_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    blocked = get_meta_state()["blocked"]
    if not blocked:
        await update.message.reply_text("Koi blocked user nahi hai.")
        return
    lines = "\n".join(f"• <code>{u}</code>" for u in blocked)
    await update.message.reply_text(f"<b>Blocked Users:</b>\n{lines}", parse_mode="HTML")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    meta = get_meta_state()
    await update.message.reply_text(
        f"<b>Bot Stats</b>\n"
        f"• Active Hosts: <code>{len(ACTIVE_HOSTS)}</code>\n"
        f"• Sudo Users: <code>{len(meta['sudos'])}</code>\n"
        f"• Blocked Users: <code>{len(meta['blocked'])}</code>",
        parse_mode="HTML",
    )


async def secretfunction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("Access denied.")
        return
    meta = get_meta_state()
    meta["secret_mode"] = not meta["secret_mode"]
    save_meta_state(meta)
    state_label = "ENABLED" if meta["secret_mode"] else "DISABLED"
    await update.message.reply_text(f"Secret mode: {state_label}")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "open_help":
        await query.message.reply_text(help_text_html(), parse_mode="HTML")


async def post_init(application: Application):
    if API_ID and API_HASH:
        await restore_all_saved_sessions(API_ID, API_HASH)


def main():
    if not BOT_TOKEN or not API_ID or not API_HASH:
        raise ValueError("BOT_TOKEN, API_ID, aur API_HASH environment variables set karein.")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    handlers = [
        ("start", start_cmd),
        ("help", help_cmd),
        ("commands", commands_cmd),
        ("host", host_cmd),
        ("cancel", cancel_cmd),
        ("support", support_cmd),
        ("restart", restart_cmd),
        ("supportraid", supportraid_cmd),
        ("restartall", restartall_cmd),
        ("refresh", refresh_cmd),
        ("status", status_cmd),
        ("logout", logout_cmd),
        ("sudolist", sudolist_cmd),
        ("setdp", setdp_cmd),
        ("block", block_cmd),
        ("unblock", unblock_cmd),
        ("blockeduser", blockeduser_cmd),
        ("stats", stats_cmd),
        ("secretfunction", secretfunction_cmd),
    ]

    for cmd, fn in handlers:
        app.add_handler(CommandHandler(cmd, fn))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_step_handler))

    print("Hoster Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
