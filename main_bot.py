import asyncio
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:
    from config import (
        API_HASH,
        API_ID,
        BOT_TOKEN,
        CRAFTED_BY,
        DEFAULT_BANNER_URL,
        DEFAULT_FORCE_JOIN_CHAT_ID,
        DEFAULT_FORCE_JOIN_LINK,
        DEFAULT_SUPPORT_GROUP_URL,
        OWNER_ID,
    )
except ModuleNotFoundError:
    import os

    API_ID = int(os.getenv("API_ID", "0").strip() or "0")
    API_HASH = os.getenv("API_HASH", "").strip()
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    CRAFTED_BY = os.getenv("CRAFTED_BY", "ADMIN").strip()
    DEFAULT_BANNER_URL = os.getenv("DEFAULT_BANNER_URL", "").strip()
    DEFAULT_FORCE_JOIN_CHAT_ID = int(os.getenv("DEFAULT_FORCE_JOIN_CHAT_ID", "0").strip() or "0")
    DEFAULT_FORCE_JOIN_LINK = os.getenv("DEFAULT_FORCE_JOIN_LINK", "").strip()
    DEFAULT_SUPPORT_GROUP_URL = os.getenv("DEFAULT_SUPPORT_GROUP_URL", "").strip()
    OWNER_ID = int(os.getenv("OWNER_ID", "0").strip() or "0")

try:
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
except ModuleNotFoundError:
    ACTIVE_HOSTS = {}
    PENDING_LOGINS = {}
    _FALLBACK_META = {
        "sudos": [],
        "blocked": [],
        "dp_url": DEFAULT_BANNER_URL,
        "secret_mode": False,
        "force_join_chat_id": DEFAULT_FORCE_JOIN_CHAT_ID,
        "force_join_link": DEFAULT_FORCE_JOIN_LINK,
        "support_group_url": DEFAULT_SUPPORT_GROUP_URL,
    }

    async def cancel_pending_login(user_id: int):
        PENDING_LOGINS.pop(user_id, None)

    def get_meta_state() -> dict:
        return _FALLBACK_META

    def load_all_sessions() -> dict:
        return {}

    async def logout_user_account(user_id: int):
        ACTIVE_HOSTS.pop(user_id, None)
        return True, "Logged out."

    async def restore_all_saved_sessions(api_id: int, api_hash: str):
        return None

    async def restart_user_account(user_id: int, api_id: int, api_hash: str):
        return False, "host_engine module repo mein nahi mila."

    def save_meta_state(meta: dict):
        _FALLBACK_META.update(meta)

    async def send_login_code(user_id: int, phone: str, api_id: int, api_hash: str):
        return False, "host_engine module repo mein nahi mila."

    async def submit_2fa_password(user_id: int, password: str, api_id: int, api_hash: str):
        return "error", "host_engine module repo mein nahi mila."

    async def submit_otp_code(user_id: int, otp_text: str, api_id: int, api_hash: str):
        return "error", "host_engine module repo mein nahi mila."

START_TIME = time.time()


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def is_sudo(uid: int) -> bool:
    meta = get_meta_state()
    return uid == OWNER_ID or uid in meta.get("sudos", [])


def is_blocked(uid: int) -> bool:
    if uid == OWNER_ID:
        return False
    meta = get_meta_state()
    return uid in meta.get("blocked", [])


def get_force_join_config() -> tuple[int, str, str]:
    meta = get_meta_state()
    chat_id = meta.get("force_join_chat_id", DEFAULT_FORCE_JOIN_CHAT_ID)
    join_link = meta.get("force_join_link") or DEFAULT_FORCE_JOIN_LINK
    support_url = meta.get("support_group_url") or DEFAULT_SUPPORT_GROUP_URL or join_link
    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        chat_id = 0
    return chat_id, join_link, support_url


async def is_user_in_force_chat(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    chat_id, _, _ = get_force_join_config()
    if not chat_id:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except TelegramError:
        return False


def force_join_keyboard() -> InlineKeyboardMarkup:
    _, join_link, support_url = get_force_join_config()
    row1 = []
    if join_link:
        row1.append(InlineKeyboardButton("📢 Join Group", url=join_link))
    if support_url and support_url != join_link:
        row1.append(InlineKeyboardButton("💬 Support", url=support_url))
    buttons = []
    if row1:
        buttons.append(row1)
    buttons.append([InlineKeyboardButton("✅ Joined / Verify", callback_data="verify_force_join")])
    return InlineKeyboardMarkup(buttons)


def home_keyboard() -> InlineKeyboardMarkup:
    _, _, support_url = get_force_join_config()
    row1 = [InlineKeyboardButton("📖 Help", callback_data="open_help")]
    if support_url:
        row1.append(InlineKeyboardButton("🌐 Support", url=support_url))
    return InlineKeyboardMarkup([row1])


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
        "🔹 /start - LAUNCH THE BOT WITH A GRAND WELCOME\n"
        "🔹 /help - DISCOVER ALL COMMANDS\n"
        "🔹 /commands - EXPLORE USERBOT FEATURES\n"
        "🔹 /host - DEPLOY YOUR OWN USERBOT\n"
        "🔹 /cancel - CANCEL ACTIVE LOGIN PROCESS\n"
        "🔹 /support - REQUEST SUPPORT FROM ADMIN\n"
        "🔹 /restart - REVIVE YOUR HOSTED USERBOT\n"
        "🔹 /supportraid - PRO SUPPORT RAID COMMAND (OWNERS / SUDO)\n"
        "🔹 /restartall - RESTART ALL USERBOTS (OWNERS ONLY)\n"
        "🔹 /refresh - REFRESH BOT STATE (OWNERS ONLY)\n"
        "🔹 /status - CHECK YOUR USERBOT'S PULSE\n"
        "🔹 /logout - SAFELY LOG OUT YOUR USERBOT\n"
        "🔹 /setforce &lt;chat_id&gt; &lt;link&gt; - SET FORCE JOIN (OWNERS ONLY)\n"
        "🔹 /setsupport &lt;link&gt; - SET SUPPORT LINK (OWNERS ONLY)\n"
        "🔹 /sudolist - VIEW SUDO USERS (OWNERS ONLY)\n"
        "🔹 /setdp - SET DISPLAY PHOTO (OWNERS ONLY)\n"
        "🔹 /block - BLOCK A USER (OWNERS ONLY)\n"
        "🔹 /unblock - UNBLOCK A USER (OWNERS ONLY)\n"
        "🔹 /blockeduser - VIEW BLOCKED USERS (OWNERS ONLY)\n"
        "🔹 /stats - VIEW BOT STATISTICS (OWNERS ONLY)\n"
        "🔹 /secretfunction - VIEW SECRET COMMANDS (OWNERS ONLY)"
    )


async def send_home_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meta = get_meta_state()
    photo = meta.get("dp_url") or DEFAULT_BANNER_URL
    caption = start_caption_html()
    target_msg = update.message or (update.callback_query.message if update.callback_query else None)
    if not target_msg:
        return

    if photo:
        try:
            await target_msg.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=home_keyboard(),
            )
            return
        except Exception:
            pass

    await target_msg.reply_text(caption, parse_mode="HTML", reply_markup=home_keyboard())


async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE, check_force_join: bool = True) -> bool:
    user = update.effective_user
    if not user:
        return False
    if is_blocked(user.id):
        if update.message:
            await update.message.reply_text("Aap is bot ke liye blocked hain.")
        return False
    if check_force_join and not is_owner(user.id):
        joined = await is_user_in_force_chat(context, user.id)
        if not joined:
            text = (
                "<b>🔒 Bot Access Locked!</b>\n\n"
                "Pehle hamara group join karein, uske baad <b>Joined / Verify</b> button dabayein."
            )
            if update.message:
                await update.message.reply_text(text, parse_mode="HTML", reply_markup=force_join_keyboard())
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    text, parse_mode="HTML", reply_markup=force_join_keyboard()
                )
            return False
    return True


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context, check_force_join=True):
        return
    await send_home_screen(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await update.message.reply_text(help_text_html(), parse_mode="HTML")


async def commands_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    txt = (
        "<b>⚡ USERBOT FEATURES ⚡</b>\n\n"
        "• .ping — Check userbot response\n"
        "• .tagall — Apne hosted account se group members ko tag karein\n"
        "• .stoptagall — Tagall stop karein\n"
        "• .replyraid &lt;user_id&gt; — DM random reply ON\n"
        "• .dreplyraid &lt;user_id&gt; — DM random reply OFF"
    )
    await update.message.reply_text(txt, parse_mode="HTML")


async def host_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = update.effective_user.id

    if uid in ACTIVE_HOSTS:
        await update.message.reply_text(
            "<b>Error Userbot Already Hosted!</b>\n"
            "Try /restart or /logout.\n"
            "Check /commands.",
            parse_mode="HTML",
        )
        return

    _, _, support_url = get_force_join_config()
    await cancel_pending_login(uid)
    await update.message.reply_text(
        f'Warning Join Our Support Group!\nJoin: <a href="{support_url}">Support Group</a>\nYou can still host.',
        parse_mode="HTML",
    )
    PENDING_LOGINS[uid] = {"step": "phone"}
    await update.message.reply_text("📱 Enter Phone Number (+91xxxxxxxxxx):")


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
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
    if not await guard(update, context):
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
    if not await guard(update, context):
        return
    _, _, support_url = get_force_join_config()
    await update.message.reply_text(
        f"Support ke liye Owner ID <code>{OWNER_ID}</code> par contact karein ya group join karein: {support_url}",
        parse_mode="HTML",
    )


async def setforce_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setforce -1001234567890 https://t.me/yourgroup")
        return
    try:
        chat_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("Chat ID numeric hona chahiye (jaise -1001234567890).")
        return
    link = context.args[1].strip()
    meta = get_meta_state()
    meta["force_join_chat_id"] = chat_id
    meta["force_join_link"] = link
    save_meta_state(meta)
    await update.message.reply_text(
        f"Force-Join updated:\n• Chat ID: <code>{chat_id}</code>\n• Link: {link}",
        parse_mode="HTML",
    )


async def setsupport_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setsupport https://t.me/yoursupport")
        return
    link = context.args[0].strip()
    meta = get_meta_state()
    meta["support_group_url"] = link
    save_meta_state(meta)
    await update.message.reply_text(f"Support link updated: {link}")


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
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
    if not await guard(update, context):
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
    if not await guard(update, context):
        return
    uid = update.effective_user.id
    uptime = int(time.time() - START_TIME)
    await update.message.reply_text(
        f"<b>Status</b>\n"
        f"• Uptime: {uptime}s\n"
        f"• Your Slot: {'Running' if uid in ACTIVE_HOSTS else 'Not Hosted'}\n"
        f"• Active Hosts: {len(ACTIVE_HOSTS)}",
        parse_mode="HTML",
    )


async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    ok, res = await logout_user_account(update.effective_user.id)
    await update.message.reply_text(res)


async def sudolist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    sudos = get_meta_state().get("sudos", [])
    if not sudos:
        await update.message.reply_text("Sudo list khali hai.")
        return
    lines = "\n".join(f"• {u}" for u in sudos)
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
    blocked = meta.setdefault("blocked", [])
    if target not in blocked:
        blocked.append(target)
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
    blocked = meta.setdefault("blocked", [])
    if target in blocked:
        blocked.remove(target)
    save_meta_state(meta)
    await update.message.reply_text(f"User {target} unblocked.")


async def blockeduser_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    blocked = get_meta_state().get("blocked", [])
    if not blocked:
        await update.message.reply_text("Koi blocked user nahi hai.")
        return
    lines = "\n".join(f"• {u}" for u in blocked)
    await update.message.reply_text(f"<b>Blocked Users:</b>\n{lines}", parse_mode="HTML")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    meta = get_meta_state()
    await update.message.reply_text(
        f"<b>Bot Stats</b>\n"
        f"• Active Hosts: {len(ACTIVE_HOSTS)}\n"
        f"• Sudo Users: {len(meta.get('sudos', []))}\n"
        f"• Blocked Users: {len(meta.get('blocked', []))}",
        parse_mode="HTML",
    )


async def secretfunction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("Access denied.")
        return
    meta = get_meta_state()
    meta["secret_mode"] = not meta.get("secret_mode", False)
    save_meta_state(meta)
    state_label = "ENABLED" if meta["secret_mode"] else "DISABLED"
    await update.message.reply_text(f"Secret mode: {state_label}")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    user = query.from_user
    if user and is_blocked(user.id):
        await query.answer("Aap blocked hain.", show_alert=True)
        return

    if query.data == "verify_force_join":
        joined = await is_user_in_force_chat(context, user.id)
        if not joined:
            await query.answer("Pehle group join karein, phir dobara try karein!", show_alert=True)
            return
        await query.answer("Verified! Access unlocked.")
        try:
            await query.message.delete()
        except Exception:
            pass
        await send_home_screen(update, context)
        return

    await query.answer()
    if query.data == "open_help":
        await query.message.reply_text(help_text_html(), parse_mode="HTML")


async def post_init(application: Application):
    if API_ID and API_HASH:
        await restore_all_saved_sessions(API_ID, API_HASH)


def main():
    if not BOT_TOKEN or not API_ID or not API_HASH:
        raise ValueError("BOT_TOKEN, API_ID, aur API_HASH environment variables set karein.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    handlers = [
        ("start", start_cmd),
        ("help", help_cmd),
        ("commands", commands_cmd),
        ("host", host_cmd),
        ("cancel", cancel_cmd),
        ("support", support_cmd),
        ("setforce", setforce_cmd),
        ("setsupport", setsupport_cmd),
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
    try:
        app.run_polling(stop_signals=None)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            loop.close()


if __name__ == "__main__":
    main()
