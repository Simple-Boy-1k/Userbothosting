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

START_TIME = time.time()

COMMAND_CATEGORIES: dict[str, tuple[str, str]] = {
    "spam": (
        "✉️ Spam — Commands",
        "1. Command\n"
        ".spam &lt;count&gt; [chatid] &lt;message&gt; [@username]\n\n"
        "📝 Explanation\n"
        "Ek message ko specified count ke according repeat kare.\n\n"
        "💡 Example\n"
        ".spam 5 @username Hello!\n\n"
        "⚠️ Note\n"
        "Sirf permission wale chats mein use karein.\n\n"
        "2. Command\n"
        ".stopspam [id]\n\n"
        "📝 Explanation\n"
        "Running spam task ko stop kare.\n\n"
        "💡 Example\n"
        ".stopspam 123",
    ),
    "tspam": (
        "⏱️ Timed Spam — Commands",
        "1. Command\n"
        ".tspam &lt;time&gt; [chatid/@username] &lt;count&gt; &lt;message&gt;\n\n"
        "📝 Explanation\n"
        "Messages ke beech specified delay ke saath repeat kare.\n\n"
        "💡 Example\n"
        ".tspam 1 @username 5 Test\n\n"
        "⚠️ Note\n"
        "Delay ki unit actual .tspam handler ke according hogi.\n\n"
        "2. Command\n"
        ".stopspam [id]\n\n"
        "📝 Explanation\n"
        "Running timed-spam task ko stop kare.\n\n"
        "💡 Example\n"
        ".stopspam 456",
    ),
    "raid": (
        "💥 Raid — Commands",
        "1. Command\n"
        ".raid &lt;count&gt; [chatid] [@username]\n\n"
        "📝 Explanation\n"
        "Configured raid messages ka sequence start kare.\n\n"
        "💡 Example\n"
        ".raid 10 @username\n\n"
        "⚠️ Note\n"
        "Harassment ya bina permission targeting ke liye use na karein.\n\n"
        "2. Command\n"
        ".stopraid [id]\n\n"
        "📝 Explanation\n"
        "Running raid task ko stop kare.\n\n"
        "💡 Example\n"
        ".stopraid 789",
    ),
    "abusiveraid": (
        "🔥 Abusive Raid — Commands",
        "1. Command\n"
        ".raid &lt;count&gt; [chatid] [@username]\n\n"
        "📝 Explanation\n"
        "Configured raid pool se messages bheje.\n\n"
        "💡 Example\n"
        ".raid 5 @username\n\n"
        "2. Command\n"
        ".stopraid [id]\n\n"
        "📝 Explanation\n"
        "Running raid task ko stop kare.\n\n"
        "💡 Example\n"
        ".stopraid",
    ),
    "shayari": (
        "💌 Shayari Raid — Commands",
        "1. Command\n"
        ".sraid &lt;count&gt; [username/userid]\n\n"
        "📝 Explanation\n"
        "Selected user ke liye shayari messages bheje. User ke message par reply karke bhi use kar sakte hain.\n\n"
        "💡 Example\n"
        ".sraid 5 @username\n\n"
        "2. Command\n"
        ".stopsraid\n\n"
        "📝 Explanation\n"
        "Running shayari task ko stop kare.\n\n"
        "💡 Example\n"
        ".stopsraid",
    ),
    "replyraid": (
        "🎯 Reply Raid — Commands",
        "1. Command\n"
        ".replyraid [username/userid]\n\n"
        "📝 Explanation\n"
        "Selected user ke reply ya mention par configured automatic raid response enable kare. Target ke message par reply karke bhi use kar sakte hain.\n\n"
        "💡 Example\n"
        ".replyraid @username\n\n"
        "⚠️ Note\n"
        "Harassment ya unwanted targeting ke liye use na karein.\n\n"
        "2. Command\n"
        ".dreplyraid [username/userid]\n\n"
        "📝 Explanation\n"
        "Selected user ke liye reply raid disable kare.\n\n"
        "💡 Example\n"
        ".dreplyraid @username",
    ),
    "tagging": (
        "🔔 Tagging — Commands",
        "1. Command\n"
        ".tagall [message]\n\n"
        "📝 Explanation\n"
        "Group members ko mention karne ka task start kare.\n\n"
        "💡 Example\n"
        ".tagall\n\n"
        "⚠️ Note\n"
        "Group permission aur Telegram limits apply hoti hain.\n\n"
        "2. Command\n"
        ".stoptagall [id]\n\n"
        "📝 Explanation\n"
        "Running member-tagging task ko stop kare.\n\n"
        "💡 Example\n"
        ".stoptagall 101",
    ),
    "welcome": (
        "🎉 Welcome — Commands",
        "1. Command\n"
        ".setwlcm &lt;message&gt;\n\n"
        "📝 Explanation\n"
        "New members ke liye custom welcome message set kare.\n\n"
        "💡 Example\n"
        ".setwlcm Welcome to our group!\n\n"
        "2. Command\n"
        ".stopwlcm\n\n"
        "📝 Explanation\n"
        "Welcome messages disable kare.\n\n"
        "💡 Example\n"
        ".stopwlcm\n\n"
        "3. Command\n"
        ".wlcmmssg\n\n"
        "📝 Explanation\n"
        "Welcome configuration ko existing handler ke default/reset behaviour par restore kare.\n\n"
        "💡 Example\n"
        ".wlcmmssg",
    ),
    "moderation": (
        "🚫 Moderation — Commands",
        "1. Command\n"
        ".ban @username [reason]\n\n"
        "📝 Explanation\n"
        "User ko group se ban kare.\n\n"
        "💡 Example\n"
        ".ban @username Spamming\n\n"
        "⚠️ Note\n"
        "Required admin permissions honi chahiye.\n\n"
        "2. Command\n"
        ".unban @username\n\n"
        "📝 Explanation\n"
        "Previously banned user ka ban remove kare.\n\n"
        "💡 Example\n"
        ".unban @username\n\n"
        "3. Command\n"
        ".mute @username [time(s/m/h/d)] [reason]\n\n"
        "📝 Explanation\n"
        "User ki messaging permission restrict kare (s, m, h, d).\n\n"
        "💡 Example\n"
        ".mute @username 1h Spamming\n\n"
        "4. Command\n"
        ".unmute @username\n\n"
        "📝 Explanation\n"
        "Muted user ki messaging permission restore kare.\n\n"
        "💡 Example\n"
        ".unmute @username\n\n"
        "5. Command\n"
        ".kick @username [reason]\n\n"
        "📝 Explanation\n"
        "User ko current group se remove kare.\n\n"
        "💡 Example\n"
        ".kick @username Disruptive behaviour\n\n"
        "6. Command\n"
        ".clear &lt;count&gt;\n\n"
        "📝 Explanation\n"
        "Specified number of messages delete kare.\n\n"
        "💡 Example\n"
        ".clear 10\n\n"
        "⚠️ Note\n"
        "Deletion permissions aur Telegram restrictions apply hoti hain.\n\n"
        "7. Command\n"
        ".rmall\n\n"
        "📝 Explanation\n"
        "Existing handler ke mutabik group members ko bulk remove kare.\n\n"
        "💡 Example\n"
        ".rmall\n\n"
        "⚠️ Note\n"
        "Destructive action: group owner ki explicit permission ke bina use na karein.\n\n"
        "8. Command\n"
        "/invall &lt;group_link/@username&gt;\n\n"
        "📝 Explanation\n"
        "Source group/channel ke members ko current chat mein add karne ka attempt kare.\n\n"
        "💡 Example\n"
        "/invall @PublicGroup\n\n"
        "⚠️ Note\n"
        "Admin permissions, user privacy, consent aur Telegram limits apply hoti hain.\n\n"
        "9. Command\n"
        ".add @username1 [@username2 ...]\n\n"
        "📝 Explanation\n"
        "Ek ya multiple users ko current group mein add kare.\n\n"
        "💡 Example\n"
        ".add @User1 @User2\n\n"
        "⚠️ Note\n"
        "User privacy settings aur required permissions apply hoti hain.",
    ),
    "fun": (
        "😂 Fun — Commands",
        "1. Command\n"
        ".joke\n\n"
        "📝 Explanation\n"
        "Random Hindi joke display kare.\n\n"
        "💡 Example\n"
        ".joke\n\n"
        "2. Command\n"
        ".flip\n\n"
        "📝 Explanation\n"
        "Coin toss ka result display kare.\n\n"
        "💡 Example\n"
        ".flip\n\n"
        "3. Command\n"
        ".roll &lt;number&gt;\n\n"
        "📝 Explanation\n"
        "Specified number ke according random roll generate kare.\n\n"
        "💡 Example\n"
        ".roll 6\n\n"
        "4. Command\n"
        ".rps rock|paper|scissors\n\n"
        "📝 Explanation\n"
        "Rock, paper, scissors game play kare.\n\n"
        "💡 Example\n"
        ".rps rock\n\n"
        "5. Command\n"
        ".calc &lt;expression&gt;\n\n"
        "📝 Explanation\n"
        "Mathematical expression calculate kare.\n\n"
        "💡 Example\n"
        ".calc 2 + 3",
    ),
    "custom": (
        "✍️ Customization — Commands",
        "1. Command\n"
        ".stylish &lt;name&gt;\n\n"
        "📝 Explanation\n"
        "Diye gaye text/name ke stylish variations generate kare.\n\n"
        "💡 Example\n"
        ".stylish Aditya\n\n"
        "2. Command\n"
        ".changeowner @username\n\n"
        "📝 Explanation\n"
        "Ping message mein display hone wala owner username change kare.\n\n"
        "💡 Example\n"
        ".changeowner @NewOwner\n\n"
        "⚠️ Note\n"
        "Ye help entry sirf ping display customization describe karti hai; account ownership transfer nahi.\n\n"
        "3. Command\n"
        ".setemoji &lt;emoji&gt;\n\n"
        "📝 Explanation\n"
        "Ping message mein display hone wala custom emoji set kare.\n\n"
        "💡 Example\n"
        ".setemoji ⚡\n\n"
        "⚠️ Note\n"
        "Emoji command ke baad space dekar likhein.\n\n"
        "4. Command\n"
        ".setemoji off\n\n"
        "📝 Explanation\n"
        "Ping message se custom emoji remove kare.\n\n"
        "💡 Example\n"
        ".setemoji off",
    ),
    "clone": (
        "👤 Profile Clone — Commands",
        "1. Command\n"
        ".clone [username]\n\n"
        "📝 Explanation\n"
        "Selected user's profile ko clone karne wala existing handler run kare. Username dein ya user ke message par reply karke command bhejein.\n\n"
        "💡 Example\n"
        ".clone @username\n"
        ".clone (user ke message par reply karke)\n\n"
        "⚠️ Note\n"
        "Sirf apne ya permission wale profile par use karein.\n\n"
        "2. Command\n"
        ".dclone\n\n"
        "📝 Explanation\n"
        "Clone se pehle saved original profile restore kare.\n\n"
        "💡 Example\n"
        ".dclone\n\n"
        "⚠️ Note\n"
        "Restore tabhi possible hai jab original profile ka backup save kiya ho.",
    ),
    "general": (
        "ℹ️ General — Commands",
        "1. Command\n"
        ".ping\n\n"
        "📝 Explanation\n"
        "Userbot ka response time check kare.\n\n"
        "💡 Example\n"
        ".ping\n\n"
        "2. Command\n"
        ".uptime\n\n"
        "📝 Explanation\n"
        "Userbot ka running duration display kare.\n\n"
        "💡 Example\n"
        ".uptime\n\n"
        "3. Command\n"
        ".info [@username]\n\n"
        "📝 Explanation\n"
        "User ya chat ki available information display kare.\n\n"
        "💡 Example\n"
        ".info @username\n\n"
        "4. Command\n"
        ".logout\n\n"
        "📝 Explanation\n"
        "Userbot account/session se logout kare.\n\n"
        "💡 Example\n"
        ".logout\n\n"
        "⚠️ Note\n"
        "Logout ke baad dobara login ki zarurat ho sakti hai.",
    ),
    "admin": (
        "🛠️ Admin — Commands",
        "1. Command\n"
        ".addsudo @username\n\n"
        "📝 Explanation\n"
        "Trusted user ko sudo access de.\n\n"
        "💡 Example\n"
        ".addsudo @username\n\n"
        "⚠️ Note\n"
        "Owner-only command. Sirf trusted users ko access dein.\n\n"
        "2. Command\n"
        ".rmsudo @username\n\n"
        "📝 Explanation\n"
        "User ka sudo access remove kare.\n\n"
        "💡 Example\n"
        ".rmsudo @username\n\n"
        "3. Command\n"
        ".activeusers\n\n"
        "📝 Explanation\n"
        "Active userbot users/sessions ki available list display kare.\n\n"
        "💡 Example\n"
        ".activeusers",
    ),
    "sd": (
        "💾 Save Disappearing — Commands",
        "1. Command\n"
        ".sd\n\n"
        "📝 Explanation\n"
        "Replied message/media ko Saved Messages mein save karne wala existing handler run kare.\n\n"
        "💡 Example\n"
        ".sd (supported message par reply karke)\n\n"
        "⚠️ Note\n"
        "Sender ki permission aur privacy respect karein.",
    ),
    "broadcast": (
        "📢 Broadcast — Commands",
        "1. Command\n"
        ".broadcast &lt;message&gt;\n\n"
        "📝 Explanation\n"
        "Configured groups mein announcement bheje, jahan messaging allowed ho.\n\n"
        "💡 Example\n"
        ".broadcast Hello everyone!\n\n"
        "⚠️ Note\n"
        "Sirf authorized groups mein use karein. Telegram rate limits aur chat permissions apply hoti hain.",
    ),
    "antisafe": (
        "🛡️ AntiSafe — Commands",
        "1. Command\n"
        ".antisafe on\n\n"
        "📝 Explanation\n"
        "Unapproved incoming DMs ke liye automatic deletion/protection enable kare.\n\n"
        "💡 Example\n"
        ".antisafe on\n\n"
        "⚠️ Note\n"
        "Exact deletion behaviour existing AntiSafe handler par depend karta hai.\n\n"
        "2. Command\n"
        ".antisafe off\n\n"
        "📝 Explanation\n"
        "AntiSafe protection disable kare.\n\n"
        "💡 Example\n"
        ".antisafe off",
    ),
    "approve": (
        "✅ Approve — Commands",
        "1. Command\n"
        ".approve\n\n"
        "📝 Explanation\n"
        "Current DM ke user ko AntiSafe deletion se exempt kare.\n\n"
        "💡 Example\n"
        ".approve (user ke private chat mein)",
    ),
    "craid": (
        "⚡ CRAID — Commands",
        "1. Command\n"
        ".craid &lt;count&gt;\n\n"
        "📝 Explanation\n"
        "Configured personal channel ke messages se reply-based raid task start kare.\n\n"
        "💡 Example\n"
        ".craid 50 (target message par reply karke)\n\n"
        "⚠️ Note\n"
        "Sirf permission wale chats mein use karein.\n\n"
        "2. Command\n"
        ".setraid &lt;channel_link&gt;\n\n"
        "📝 Explanation\n"
        "CRAID messages ke liye source channel set kare.\n\n"
        "💡 Example\n"
        ".setraid https://t.me/+abc123\n\n"
        "⚠️ Note\n"
        "Source channel ka access required hai.",
    ),
    "autoreply": (
        "🤖 AutoReply — Commands",
        "1. Command\n"
        ".autoreply &lt;message&gt;\n\n"
        "📝 Explanation\n"
        "Username mention/@tag hone par custom automatic reply enable kare.\n\n"
        "💡 Example\n"
        ".autoreply Abhi busy hoon, thodi der mein reply karunga.\n\n"
        "⚠️ Note\n"
        "Is feature ka intended trigger @mention hai; normal replies aur PMs nahi.\n\n"
        "2. Command\n"
        ".dautoreply\n\n"
        "📝 Explanation\n"
        "Mention-based automatic replies disable kare.\n\n"
        "💡 Example\n"
        ".dautoreply",
    ),
    "clearall": (
        "☢️ Nuclear Clear — Commands",
        "1. Command\n"
        ".clearall\n\n"
        "📝 Explanation\n"
        "Bulk history-clearing operation ka confirmation flow start kare.\n\n"
        "💡 Example\n"
        ".clearall\n\n"
        "⚠️ Note\n"
        "Destructive operation. Actual scope account access, Telegram permissions aur existing handler par depend karta hai.\n\n"
        "2. Command\n"
        ".clearall confirm\n\n"
        "📝 Explanation\n"
        "Pending history-clearing operation confirm kare.\n\n"
        "💡 Example\n"
        ".clearall confirm\n\n"
        "⚠️ Note\n"
        "Deleted data recover na ho sake. Confirmation dhyan se karein.",
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
    rows = [
        [
            InlineKeyboardButton("✉️ Spam", callback_data="cmdcat_spam"),
            InlineKeyboardButton("⏱️ Timed Spam", callback_data="cmdcat_tspam"),
            InlineKeyboardButton("💥 Raid", callback_data="cmdcat_raid"),
        ],
        [
            InlineKeyboardButton("🔥 Abusive Raid", callback_data="cmdcat_abusiveraid"),
            InlineKeyboardButton("💌 Shayari Raid", callback_data="cmdcat_shayari"),
            InlineKeyboardButton("🎯 Reply Raid", callback_data="cmdcat_replyraid"),
        ],
        [
            InlineKeyboardButton("🔔 Tagging", callback_data="cmdcat_tagging"),
            InlineKeyboardButton("🎉 Welcome", callback_data="cmdcat_welcome"),
            InlineKeyboardButton("🚫 Moderation", callback_data="cmdcat_moderation"),
        ],
        [
            InlineKeyboardButton("😂 Fun", callback_data="cmdcat_fun"),
            InlineKeyboardButton("✍️ Customization", callback_data="cmdcat_custom"),
            InlineKeyboardButton("👤 Profile Clone", callback_data="cmdcat_clone"),
        ],
        [
            InlineKeyboardButton("ℹ️ General", callback_data="cmdcat_general"),
            InlineKeyboardButton("🛠️ Admin", callback_data="cmdcat_admin"),
            InlineKeyboardButton("💾 Save Disappearing", callback_data="cmdcat_sd"),
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="cmdcat_broadcast"),
            InlineKeyboardButton("🛡️ AntiSafe", callback_data="cmdcat_antisafe"),
            InlineKeyboardButton("✅ Approve", callback_data="cmdcat_approve"),
        ],
        [
            InlineKeyboardButton("⚡ CRAID", callback_data="cmdcat_craid"),
            InlineKeyboardButton("🤖 AutoReply", callback_data="cmdcat_autoreply"),
            InlineKeyboardButton("☢️ Nuclear Clear", callback_data="cmdcat_clearall"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def back_to_commands_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back to Commands", callback_data="back_to_commands")]])


def commands_home_html() -> str:
    return (
        "<b>✨ Userbot Commands - Premium! ✨</b>\n\n"
        "💬 <b>*CLICK A BOX TO EXPLORE COMMANDS!*</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Categories:</b> 21\n"
        "🧾 <b>Command entries:</b> 54\n\n"
        "📖 <b>Syntax guide</b>\n"
        "&lt;value&gt; — Required argument\n"
        "[value] — Optional argument\n"
        "a|b — Available options mein se ek\n\n"
        "🎓 <b>Full Command Tutorial</b>\n\n"
        "🔹 <b>Select a category below</b>"
    )


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
    await update.message.reply_text(
        commands_home_html(),
        parse_mode="HTML",
        reply_markup=commands_menu_keyboard(),
    )


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

    if support_url:
        await update.message.reply_text(
            f'<b>Warning Join Our Support Group!</b>\nJoin: <a href="{support_url}">Support Group</a>\nYou can still host.',
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    else:
        await update.message.reply_text(
            "<b>Warning Join Our Support Group!</b>\nYou can still host.",
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


async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    _, _, support_url = get_force_join_config()
    link_line = f'\nJoin: <a href="{support_url}">Support Group</a>' if support_url else ""
    await update.message.reply_text(
        f"Support ke liye Owner ID {OWNER_ID} par contact karein.{link_line}",
        parse_mode="HTML",
        disable_web_page_preview=True,
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
    link = _normalize_tg_link(context.args[1])
    meta = get_meta_state()
    meta["force_join_chat_id"] = chat_id
    meta["force_join_link"] = link
    save_meta_state(meta)
    await update.message.reply_text(
        f'Force-Join updated:\n• Chat ID: {chat_id}\n• Link: <a href="{link}">Support Group</a>',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def setsupport_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Sirf Owner is command ka use kar sakte hain.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setsupport https://t.me/yoursupport")
        return
    link = _normalize_tg_link(context.args[0])
    meta = get_meta_state()
    meta["support_group_url"] = link
    save_meta_state(meta)
    await update.message.reply_text(
        f'Support link updated: <a href="{link}">Support Group</a>',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


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
    await update.message.reply_text(res, parse_mode="HTML")


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
    data = query.data or ""

    if data == "open_help":
        await query.message.reply_text(help_text_html(), parse_mode="HTML")
        return

    if data == "back_to_commands":
        try:
            await query.message.edit_text(
                commands_home_html(),
                parse_mode="HTML",
                reply_markup=commands_menu_keyboard(),
            )
        except Exception:
            await query.message.reply_text(
                commands_home_html(),
                parse_mode="HTML",
                reply_markup=commands_menu_keyboard(),
            )
        return

    if data.startswith("cmdcat_"):
        cat_key = data.replace("cmdcat_", "", 1)
        cat = COMMAND_CATEGORIES.get(cat_key)
        if cat:
            title, body = cat
            text = (
                f"<b>{title}</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{body}\n\n"
                "↩️ Categories par wapas jaane ke liye Back button dabayein."
            )
            try:
                await query.message.edit_text(
                    text,
                    parse_mode="HTML",
                    reply_markup=back_to_commands_keyboard(),
                )
            except Exception:
                await query.message.reply_text(
                    text,
                    parse_mode="HTML",
                    reply_markup=back_to_commands_keyboard(),
                )


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
