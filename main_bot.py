import asyncio
import html
import os
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
    API_ID = int(os.getenv("API_ID", "0").strip() or "0")
    API_HASH = os.getenv("API_HASH", "").strip()
    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    CRAFTED_BY = os.getenv("CRAFTED_BY", "ADMIN").strip()
    DEFAULT_BANNER_URL = os.getenv("DEFAULT_BANNER_URL", "").strip()
    DEFAULT_FORCE_JOIN_CHAT_ID = int(os.getenv("DEFAULT_FORCE_JOIN_CHAT_ID", "0").strip() or "0")
    DEFAULT_FORCE_JOIN_LINK = os.getenv("DEFAULT_FORCE_JOIN_LINK", "").strip()
    DEFAULT_SUPPORT_GROUP_URL = os.getenv("DEFAULT_SUPPORT_GROUP_URL", "").strip()
    OWNER_ID = int(os.getenv("OWNER_ID", "0").strip() or "0")

from host_engine import (
    ACTIVE_HOSTS,
    PENDING_LOGINS,
    cancel_pending_login,
    clear_owner_random_messages,
    get_meta_state,
    get_owner_random_messages,
    load_all_sessions,
    logout_user_account,
    restore_all_saved_sessions,
    restart_user_account,
    send_login_code,
    set_owner_random_messages,
    submit_2fa_password,
    submit_otp_code,
)

START_TIME = time.time()
OWNER_RANDOM_INPUT_MODE: dict[int, str] = {}

COMMAND_CATEGORIES: dict[str, tuple[str, str]] = {
    "spam": (
        "✉️ Spam — Commands",
        "1. Command\n.spam &lt;count&gt; [chatid] &lt;message&gt; [@username]\n\n💡 Example\n.spam 5 @username Hello!\n\n2. Command\n.stopspam [id]",
    ),
    "tspam": (
        "⏱️ Timed Spam — Commands",
        "1. Command\n.tspam &lt;time&gt; [chatid/@username] &lt;count&gt; &lt;message&gt;\n\n💡 Example\n.tspam 1 @username 5 Test\n\n2. Command\n.stopspam [id]",
    ),
    "raid": (
        "💥 Raid — Commands",
        "1. Command\n.raid &lt;count&gt; [chatid] [@username]\n\nOwner ke set kiye hue random messages se alag-alag message bhejta hai.\n\n2. Command\n.stopraid [id]",
    ),
    "abusiveraid": (
        "🔥 Abusive Raid — Commands",
        "1. Command\n.raid &lt;count&gt; [chatid] [@username]\n\n2. Command\n.stopraid [id]",
    ),
    "shayari": (
        "💌 Shayari Raid — Commands",
        "1. Command\n.sraid &lt;count&gt; [username/userid]\n\nOwner ke set kiye hue random messages pool se alag-alag message bhejta hai.\n\n2. Command\n.stopsraid",
    ),
    "replyraid": (
        "🎯 Reply Raid — Commands",
        "1. Command\n.replyraid [username/userid]\n\n2. Command\n.dreplyraid [username/userid]",
    ),
    "tagging": (
        "🔔 Tagging — Commands",
        "1. Command\n.tagall [message]\n\n2. Command\n.stoptagall [id]",
    ),
    "welcome": (
        "🎉 Welcome &amp; Quit — Commands",
        "1. Command\n.setwlcm &lt;message&gt;\n2. Command\n.stopwlcm\n3. Command\n.wlcmmssg\n4. Command\n.startquit / .stopquit",
    ),
    "moderation": (
        "🚫 Moderation — Commands",
        ".ban / .unban / .mute / .unmute / .kick / .clear &lt;n&gt; / .rmall / /invall / .add",
    ),
    "fun": (
        "😂 Fun — Commands",
        ".joke / .flip / .roll &lt;n&gt; / .rps rock|paper|scissors / .calc &lt;expr&gt;",
    ),
    "custom": (
        "✍️ Customization — Commands",
        ".stylish &lt;name&gt; / .changeowner @username / .setemoji &lt;emoji|off&gt;",
    ),
    "clone": (
        "👤 Profile Clone — Commands",
        ".clone [username] / .dclone",
    ),
    "general": (
        "ℹ️ General — Commands",
        ".ping / .uptime / .info [@username] / .logout",
    ),
    "admin": (
        "🛠️ Admin — Commands",
        ".addsudo @username / .rmsudo @username / .activeusers",
    ),
    "sd": (
        "💾 Save Disappearing — Commands",
        ".sd (replied media/message par)",
    ),
    "broadcast": (
        "📢 Broadcast — Commands",
        ".broadcast &lt;message&gt;",
    ),
    "antisafe": (
        "🛡️ AntiSafe — Commands",
        ".antisafe on / .antisafe off",
    ),
    "approve": (
        "✅ Approve — Commands",
        ".approve (private DM mein)",
    ),
    "craid": (
        "⚡ CRAID — Commands",
        ".setraid &lt;channel_link&gt; / .craid &lt;count&gt;",
    ),
    "autoreply": (
        "🤖 AutoReply — Commands",
        ".autoreply &lt;message&gt; / .dautoreply",
    ),
    "clearall": (
        "☢️ Nuclear Clear — Commands",
        ".clearall / .clearall confirm",
    ),
}


def _normalize_tg_link(url: str) -> str:
    clean = (url or "").strip()
    if not clean:
        return ""
    if clean.startswith("t.me/") or clean.startswith("telegram.me/"):
        return f"https://{clean}"
    return clean


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def is_blocked(uid: int) -> bool:
    if uid == OWNER_ID:
        return False
    meta = get_meta_state()
    return uid in meta.get("blocked", [])


def get_force_join_config() -> tuple[int, str, str]:
    meta = get_meta_state()
    chat_id = meta.get("force_join_chat_id", DEFAULT_FORCE_JOIN_CHAT_ID)
    join_link = _normalize_tg_link(meta.get("force_join_link") or DEFAULT_FORCE_JOIN_LINK)
    support_url = _normalize_tg_link(meta.get("support_group_url") or DEFAULT_SUPPORT_GROUP_URL or join_link)
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


def commands_menu_keyboard() -> InlineKeyboardMarkup:
    keys = list(COMMAND_CATEGORIES.keys())
    labels = {
        "spam": "✉️ Spam",
        "tspam": "⏱️ Timed Spam",
        "raid": "💥 Raid",
        "abusiveraid": "🔥 Abusive Raid",
        "shayari": "💌 Shayari Raid",
        "replyraid": "🎯 Reply Raid",
        "tagging": "🔔 Tagging",
        "welcome": "🎉 Welcome",
        "moderation": "🚫 Moderation",
        "fun": "😂 Fun",
        "custom": "✍️ Customization",
        "clone": "👤 Profile Clone",
        "general": "ℹ️ General",
        "admin": "🛠️ Admin",
        "sd": "💾 Save Disappearing",
        "broadcast": "📢 Broadcast",
        "antisafe": "🛡️ AntiSafe",
        "approve": "✅ Approve",
        "craid": "⚡ CRAID",
        "autoreply": "🤖 AutoReply",
        "clearall": "☢️ Nuclear Clear",
    }
    rows = []
    for i in range(0, len(keys), 3):
        rows.append(
            [InlineKeyboardButton(labels[k], callback_data=f"cmdcat_{k}") for k in keys[i : i + 3]]
        )
    return InlineKeyboardMarkup(rows)


def back_to_commands_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back to Commands", callback_data="back_to_commands")]])


def commands_home_html() -> str:
    return (
        "<b>✨ Userbot Commands - Premium! ✨</b>\n\n"
        "💬 <b>*CLICK A BOX TO EXPLORE COMMANDS!*</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Categories:</b> 21\n\n"
        "🔹 <b>Select a category below</b>"
    )


def start_caption_html() -> str:
    return (
        "<b>🏆 WELCOME TO THE PREMIUM USERBOT HOSTER BOT! 🏆</b>\n\n"
        f"<b>👑 CRAFTED BY: {CRAFTED_BY} 👑</b>\n\n"
        "<b>✨ EXPLORE COMMANDS WITH /help OR TAP BELOW! ✨</b>"
    )


def help_text_html(uid: int = 0) -> str:
    base = (
        "<b>🌟 PREMIUM HOSTER BOT COMMANDS 🌟</b>\n\n"
        "🔹 /start - Start bot\n"
        "🔹 /help - Help menu\n"
        "🔹 /commands - Userbot commands\n"
        "🔹 /host - Host account\n"
        "🔹 /cancel - Cancel login\n"
        "🔹 /restart - Restart userbot\n"
        "🔹 /logout - Logout userbot\n"
        "🔹 /status - Status check"
    )
    if is_owner(uid):
        base += (
            "\n\n<b>👑 OWNER RANDOM MESSAGE COMMANDS:</b>\n"
            "🔹 /setrandom - Naye random messages purani list mein jodein (10/50/unlimited lines ek saath)\n"
            "🔹 /addrandom - Existing list mein aur messages add karein\n"
            "🔹 /listrandom - Saved random messages count/preview dekhein\n"
            "🔹 /clearrandom - Saare custom random messages delete karein"
        )
    return base


async def send_home_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meta = get_meta_state()
    photo = meta.get("dp_url") or DEFAULT_BANNER_URL
    caption = start_caption_html()
    target_msg = update.message or (update.callback_query.message if update.callback_query else None)
    if not target_msg:
        return
    if photo:
        try:
            await target_msg.reply_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=home_keyboard())
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
            text = "<b>🔒 Bot Access Locked!</b>\n\nPehle group join karein, phir <b>Joined / Verify</b> dabayein."
            if update.message:
                await update.message.reply_text(text, parse_mode="HTML", reply_markup=force_join_keyboard())
            elif update.callback_query:
                await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=force_join_keyboard())
            return False
    return True


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context, check_force_join=True):
        return
    await send_home_screen(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text(help_text_html(uid), parse_mode="HTML")


async def commands_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await update.message.reply_text(commands_home_html(), parse_mode="HTML", reply_markup=commands_menu_keyboard())


async def setrandom_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text("Sirf Owner random messages set kar sakte hain.")
        return
    raw_arg = update.message.text.partition(" ")[2] if update.message and update.message.text else ""
    if raw_arg.strip():
        saved = set_owner_random_messages(raw_arg, append=True)
        await update.message.reply_text(
            f"✅ Naye messages purani list mein jud gaye! Total random messages: <b>{len(saved)}</b>.",
            parse_mode="HTML",
        )
        return
    OWNER_RANDOM_INPUT_MODE[uid] = "append"
    await update.message.reply_text(
        "✍️ <b>Random Messages Set / Add Mode</b>\n\n"
        "Jitne chahein utne messages (10, 50, ya aur) ek saath bhejein — pehle wale messages safe rahenge aur naye unme jud jaayenge.\n"
        "Sab hatane ke liye /clearrandom aur cancel ke liye /cancel likhein.",
        parse_mode="HTML",
    )


async def addrandom_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text("Sirf Owner random messages add kar sakte hain.")
        return
    raw_arg = update.message.text.partition(" ")[2] if update.message and update.message.text else ""
    if raw_arg.strip():
        saved = set_owner_random_messages(raw_arg, append=True)
        await update.message.reply_text(
            f"✅ Messages add ho gaye! Total random messages: <b>{len(saved)}</b>.",
            parse_mode="HTML",
        )
        return
    OWNER_RANDOM_INPUT_MODE[uid] = "append"
    await update.message.reply_text(
        "➕ <b>Add More Random Messages</b>\n\n"
        "Jo naye messages (10, 50, ya unlimited) purani list mein jodne hain, unhe ek saath bhej dein.\n"
        "Cancel karne ke liye /cancel likhein.",
        parse_mode="HTML",
    )


async def listrandom_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text("Sirf Owner random messages list dekh sakte hain.")
        return
    msgs = get_owner_random_messages()
    if not msgs:
        await update.message.reply_text("Abhi koi random message set nahi hai. /setrandom se set karein.")
        return
    preview = "\n".join(f"{i + 1}. {html.escape(m)}" for i, m in enumerate(msgs[:25]))
    extra = f"\n...aur {len(msgs) - 25} messages" if len(msgs) > 25 else ""
    await update.message.reply_text(
        f"🎲 <b>Total Random Messages: {len(msgs)}</b>\n\n{preview}{extra}",
        parse_mode="HTML",
    )


async def clearrandom_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text("Sirf Owner random messages clear kar sakte hain.")
        return
    clear_owner_random_messages()
    OWNER_RANDOM_INPUT_MODE.pop(uid, None)
    await update.message.reply_text("🗑️ Saare custom random messages clear kar diye gaye hain.")


async def host_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = update.effective_user.id
    if uid in ACTIVE_HOSTS:
        await update.message.reply_text("<b>Error Userbot Already Hosted!</b>\nTry /restart or /logout.", parse_mode="HTML")
        return
    await cancel_pending_login(uid)
    PENDING_LOGINS[uid] = {"step": "phone"}
    await update.message.reply_text("📱 Enter Phone Number (+91xxxxxxxxxx):")


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = update.effective_user.id
    cancelled_anything = False
    if uid in OWNER_RANDOM_INPUT_MODE:
        OWNER_RANDOM_INPUT_MODE.pop(uid, None)
        cancelled_anything = True
    if uid in PENDING_LOGINS:
        await cancel_pending_login(uid)
        cancelled_anything = True
    if cancelled_anything:
        await update.message.reply_text("Active process cancel kar diya gaya hai.")
    else:
        await update.message.reply_text("Koi active process nahi hai.")


async def text_step_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not await guard(update, context):
        return
    uid = update.effective_user.id
    raw_text = update.message.text

    if is_owner(uid) and uid in OWNER_RANDOM_INPUT_MODE:
        OWNER_RANDOM_INPUT_MODE.pop(uid, None)
        saved = set_owner_random_messages(raw_text, append=True)
        await update.message.reply_text(
            f"✅ Messages save ho gaye! Ab total <b>{len(saved)}</b> random messages active hain.\n"
            "Users ke raid / sraid / replyraid / joke par ab inhi mein se alag-alag message aayega.",
            parse_mode="HTML",
        )
        return

    pending = PENDING_LOGINS.get(uid)
    if not pending:
        return
    text = raw_text.strip()
    step = pending.get("step")

    if step == "phone":
        ok, res = await send_login_code(uid, text, API_ID, API_HASH)
        await update.message.reply_text(res, parse_mode="HTML")
        if not ok:
            PENDING_LOGINS.pop(uid, None)
    elif step == "otp":
        status, res = await submit_otp_code(uid, text, API_ID, API_HASH)
        if status == "done":
            wait_msg = await update.message.reply_text("🛸 Hosting userbot, please wait...")
            await wait_msg.edit_text(res, parse_mode="HTML")
        else:
            await update.message.reply_text(res, parse_mode="HTML")
    elif step == "2fa":
        wait_msg = await update.message.reply_text("🛸 Hosting userbot, please wait...")
        status, res = await submit_2fa_password(uid, text, API_ID, API_HASH)
        await wait_msg.edit_text(res, parse_mode="HTML")
        try:
            await update.message.delete()
        except Exception:
            pass


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
    await msg.edit_text(res, parse_mode="HTML")


async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    ok, res = await logout_user_account(update.effective_user.id)
    await update.message.reply_text(res, parse_mode="HTML")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = update.effective_user.id
    uptime = int(time.time() - START_TIME)
    await update.message.reply_text(
        f"<b>Status</b>\n• Uptime: {uptime}s\n• Your Slot: {'Running' if uid in ACTIVE_HOSTS else 'Not Hosted'}\n• Active Hosts: {len(ACTIVE_HOSTS)}",
        parse_mode="HTML",
    )


async def verify_force_join_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    joined = await is_user_in_force_chat(context, query.from_user.id)
    if not joined:
        await query.answer("Pehle group join karein, phir dobara try karein!", show_alert=True)
        return
    await query.answer("Verified!")
    try:
        await query.message.delete()
    except Exception:
        pass
    await send_home_screen(update, context)


async def open_help_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id if query.from_user else 0
    await query.message.reply_text(help_text_html(uid), parse_mode="HTML")


async def back_to_commands_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.edit_text(commands_home_html(), parse_mode="HTML", reply_markup=commands_menu_keyboard())
    except Exception:
        await query.message.reply_text(commands_home_html(), parse_mode="HTML", reply_markup=commands_menu_keyboard())


async def cmdcat_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_key = (query.data or "").replace("cmdcat_", "", 1)
    cat = COMMAND_CATEGORIES.get(cat_key)
    if not cat:
        return
    title, body = cat
    text = f"<b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{body}"
    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_commands_keyboard())
    except Exception:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=back_to_commands_keyboard())


async def post_init(application: Application):
    if API_ID and API_HASH:
        await restore_all_saved_sessions(API_ID, API_HASH)


def main():
    if not BOT_TOKEN or not API_ID or not API_HASH:
        raise ValueError("BOT_TOKEN, API_ID, aur API_HASH environment variables set karein.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("commands", commands_cmd))
    app.add_handler(CommandHandler("setrandom", setrandom_cmd))
    app.add_handler(CommandHandler("addrandom", addrandom_cmd))
    app.add_handler(CommandHandler("listrandom", listrandom_cmd))
    app.add_handler(CommandHandler("clearrandom", clearrandom_cmd))
    app.add_handler(CommandHandler("host", host_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
    app.add_handler(CommandHandler("logout", logout_cmd))
    app.add_handler(CommandHandler("status", status_cmd))

    app.add_handler(CallbackQueryHandler(verify_force_join_cb, pattern=r"^verify_force_join$"))
    app.add_handler(CallbackQueryHandler(open_help_cb, pattern=r"^open_help$"))
    app.add_handler(CallbackQueryHandler(back_to_commands_cb, pattern=r"^back_to_commands$"))
    app.add_handler(CallbackQueryHandler(cmdcat_cb, pattern=r"^cmdcat_"))

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
