import asyncio
import io
import math
import random
import re
import time
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import (
    EditBannedRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest

FIRST_DM_HEADER = "Hey welcome to my dm! How are you...? 😊"
QUIT_MESSAGE = "🚪👋 Member group se quit kar gaya hai!"
TAG_DELAY_SECONDS = 2.5

SHARED_MESSAGES = [
    "<b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b>",
    "<b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b>",
    "<b>𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗣𝗘 𝗖𝗛𝗔𝗟𝗔 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣</b>",
    "<b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b>",
    "<b>𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗦𝗘𝗘𝗗𝗛𝗔 𝗕𝗢𝗟 𝗥𝗔𝗛𝗔 𝗛𝗨𝗡</b>",
    "<b>𝗞𝗜𝗧𝗡𝗜 𝗚𝗔𝗟𝗜𝗬𝗔𝗡 𝗞𝗛𝗔𝗬𝗘𝗚𝗔 𝗔𝗝</b>",
    "<b>𝗕𝗘𝗦𝗔𝗡 𝗞𝗘 𝗟𝗔𝗗𝗗𝗨 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗕𝗨 🤩🥳🔥😈</b>",
    "<b>𝗦𝗣𝗘𝗘𝗗 𝗠𝗔𝗧𝗖𝗛 𝗡𝗔𝗛𝗜 𝗛𝗢 𝗥𝗔𝗛𝗜 𝗞𝗬𝗔</b>",
    "<b>𝗞𝘂𝘁𝘁𝗲 𝗸𝗶 𝗷𝗮𝗮𝘁</b>",
    "<b>𝗔𝗽𝗻𝗶 𝗷𝗮𝗴𝗮𝗵 𝗽𝗲 𝗯𝗮𝗶𝘁𝗵 𝗷𝗮𝗮</b>",
    "<b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b>",
    "<b>𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 💣</b>",
    "<b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b>",
    "<b>𝗔𝗽𝗻𝗶 𝗷𝗮𝗴𝗮𝗵 𝗽𝗲 𝗯𝗮𝗶𝘁𝗵 𝗷𝗮𝗮</b>",
    "<b>𝗝𝗵𝗮𝗮𝗻𝘁 𝗸𝗲 𝗽𝗶𝘀𝘀𝘂</b>",
    "<b>𝗔𝗔𝗚 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗖𝗛𝗔𝗧 𝗠𝗘𝗜𝗡 🔥🔥💦😆😆</b>",
    "<b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b>",
    "<b>𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗞𝗘 𝗥𝗔𝗞𝗛 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 😆💦🤤</b>",
    "<b>𝗠𝗠𝗦 𝗕𝗔𝗡𝗔 𝗖𝗛𝗨𝗞𝗔 𝗛𝗔𝗜 𝗔𝗕 𝗗𝗘𝗞𝗛</b>",
    "<b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b>",
    "<b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b>",
    "<b>𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝟵𝟵𝟵𝟵 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 🤩🥳🔥</b>",
    "<b>𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗦𝗔𝗠𝗔𝗝𝗛 𝗡𝗔𝗛𝗜 𝗔𝗬𝗔 𝗞𝗬𝗔 🤩👊👤😍</b>",
    "<b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b>",
    "<b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b>",
    "<b>𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘𝗜𝗡 𝗦𝗛𝗢𝗥 𝗛𝗔𝗜 𝗔𝗝 💋💋💦</b>",
    "<b>𝗦𝗨𝗡 𝗦𝗨𝗡 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗕𝗔𝗔𝗧 𝗦𝗨𝗡</b>",
    "<b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b>",
    "<b>𝗖𝗛𝗘𝗘𝗠𝗦 𝗦𝗘 𝗕𝗔𝗝𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗕𝗨 💦🤣</b>",
    "<b>𝗞𝗜𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦</b>",
    "<b>𝗗𝗘𝗧𝗢𝗟 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗦𝗔𝗔𝗙 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔</b>",
    "<b>𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗔𝗥 𝗗𝗜𝗬𝗘 𝗛𝗔𝗜𝗡 🤖🙏🤔</b>",
    "<b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b>",
    "<b>𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 😱🤮👺</b>",
    "<b>𝗥𝗔𝗡𝗜𝗗𝗜𝗜𝗜</b>",
    "<b>𝗜𝗧𝗡𝗔 𝗚𝗛𝗨𝗠𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗖𝗛𝗔𝗞𝗞𝗔𝗥 𝗔𝗔 𝗝𝗔𝗬𝗘𝗚𝗔 💦💋</b>",
    "<b>𝗞𝗜𝗧𝗡𝗔 𝗖𝗛𝗔𝗟𝗔𝗨𝗡 𝗔𝗕 𝗢𝗥..</b>",
    "<b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b>",
    "<b>𝗣𝗨𝗥𝗔 𝗦𝗜𝗦𝗧𝗘𝗠 𝗛𝗜𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝</b>",
    "<b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b>",
    "<b>𝗨𝗣𝗔𝗥 𝗡𝗜𝗖𝗛𝗘 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗦𝗔𝗕 🆙🆒😙</b>",
    "<b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b>",
    "<b>𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗡𝗘𝗘𝗟𝗔𝗠 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 💦💋</b>",
    "<b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b>",
    "<b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b>",
    "<b>𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘𝗜𝗡 𝗦𝗛𝗢𝗥 𝗛𝗔𝗜 𝗔𝗝 🤤🤣</b>",
    "<b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b>",
    "<b>𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗪𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗦𝗔𝗟𝗔𝗔𝗠 🤩🤩</b>",
    "<b>𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟 𝗞𝗛𝗔𝗧𝗔𝗠 ☝🏻☝🏻😬</b>",
    "<b>𝗞𝗔𝗔𝗟𝗔 𝗦𝗜𝗦𝗧𝗘𝗠 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗔𝗝</b>",
    "<b>𝗨𝗹𝗹𝘂 𝗸𝗲 𝗽𝗮𝘁𝘁𝗵𝗲</b>",
    "<b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b>",
    "<b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b>",
    "<b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b>",
    "<b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b>",
    "<b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b>",
]

RANDOM_MESSAGES = list(SHARED_MESSAGES)
SHAYARI_MESSAGES = list(SHARED_MESSAGES)
HINDI_JOKES = list(SHARED_MESSAGES)

_BOLD_SANS_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
)


def _escape_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _clean_mention_name(user) -> str:
    if not user:
        return "Member"
    first = (getattr(user, "first_name", None) or "").replace("<", "").replace(">", "").replace("&", "").strip()
    if first:
        return first
    uname = (getattr(user, "username", None) or "").replace("<", "").replace(">", "").replace("&", "").strip()
    if uname:
        return f"@{uname}"
    return "Member"


def _format_duration(seconds: int) -> str:
    days, rem = divmod(max(0, int(seconds)), 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def _parse_duration_seconds(raw: str | None) -> int | None:
    if not raw:
        return None
    m = re.match(r"^(\d+)([smhd])$", raw.strip().lower())
    if not m:
        return None
    val = int(m.group(1))
    unit = m.group(2)
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return val * mult


def _safe_calc(expr: str) -> str:
    clean = (expr or "").strip()
    if not re.fullmatch(r"[0-9+\-*/().%\s^]+", clean):
        return "Invalid expression. Sirf numbers aur + - * / % ( ) allow hain."
    clean = clean.replace("^", "**")
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        "round": round,
    }
    val = eval(clean, {"__builtins__": {}}, allowed_names)
    return str(val)


def _format_target_prefix(target_user) -> str:
    if not target_user:
        return ""
    uid = getattr(target_user, "id", None)
    uname = _clean_mention_name(target_user)
    if uid:
        return f'<a href="tg://user?id={uid}">{uname}</a> '
    return ""


async def _resolve_target_user(client: TelegramClient, event, token: str | None):
    if event.is_reply:
        try:
            rep = await event.get_reply_message()
            if rep and rep.sender_id:
                return await client.get_entity(rep.sender_id)
        except Exception:
            pass
    if token:
        cleaned = token.strip().lstrip("@")
        try:
            if cleaned.isdigit():
                return await client.get_entity(int(cleaned))
            return await client.get_entity(cleaned)
        except Exception:
            return None
    return None


def _pick_from_pool(host_state: dict, pool_key: str, pool_list: list[str], target_id: int) -> str:
    valid_msgs = [m.strip() for m in pool_list if isinstance(m, str) and m.strip()]
    if not valid_msgs:
        return "<b>Hello! 👋</b>"
    if len(valid_msgs) == 1:
        return valid_msgs[0]
    bucket = host_state.setdefault(pool_key, {})
    last_msg = bucket.get(target_id)
    candidates = [m for m in valid_msgs if m != last_msg]
    chosen = random.choice(candidates or valid_msgs)
    bucket[target_id] = chosen
    return chosen


def _pick_random_message(host_state: dict, target_id: int) -> str:
    return _pick_from_pool(host_state, "last_msg", RANDOM_MESSAGES, target_id)


def _pick_shayari_message(host_state: dict, target_id: int) -> str:
    return _pick_from_pool(host_state, "last_shayari", SHAYARI_MESSAGES, target_id)


def _pick_joke_message(host_state: dict, target_id: int) -> str:
    return _pick_from_pool(host_state, "last_joke", HINDI_JOKES, target_id)


def _extract_tag_text(raw_text: str) -> str:
    txt = (raw_text or "").strip()
    match = re.match(r"^[.]?tagall(?:\s+(.*))?$", txt, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return "Hii"
    extra = (match.group(1) or "").strip()
    return _escape_html(extra) if extra else "Hii"


async def _collect_group_targets(client: TelegramClient, chat_id: int) -> list[tuple[int, str]]:
    me = await client.get_me()
    my_id = me.id if me else 0
    targets: list[tuple[int, str]] = []
    seen_ids: set[int] = set()

    try:
        entity = await client.get_entity(chat_id)
        async for member in client.iter_participants(entity, aggressive=True):
            if not member or member.bot or member.deleted or member.id == my_id:
                continue
            if member.id not in seen_ids:
                seen_ids.add(member.id)
                targets.append((member.id, _clean_mention_name(member)))
    except Exception:
        pass

    if not targets:
        try:
            async for msg in client.iter_messages(chat_id, limit=200):
                sender = msg.sender
                if not sender or getattr(sender, "bot", False) or getattr(sender, "deleted", False):
                    continue
                if sender.id and sender.id != my_id and sender.id not in seen_ids:
                    seen_ids.add(sender.id)
                    targets.append((sender.id, _clean_mention_name(sender)))
        except Exception:
            pass

    return targets


def _register_background_task(host_state: dict, task: asyncio.Task) -> int:
    seq = host_state.get("task_seq", 100) + 1
    host_state["task_seq"] = seq
    host_state["background_tasks"][seq] = task

    def _on_done(_t):
        host_state["background_tasks"].pop(seq, None)

    task.add_done_callback(_on_done)
    return seq


def _cancel_background_task(host_state: dict, task_id: int | None = None) -> int:
    bg = host_state.get("background_tasks") or {}
    if task_id is not None:
        t = bg.pop(task_id, None)
        if t and not t.done():
            t.cancel()
            return 1
        return 0
    count = 0
    for tid in list(bg.keys()):
        t = bg.pop(tid, None)
        if t and not t.done():
            t.cancel()
            count += 1
    return count


async def _run_tagall_in_chat(
    client: TelegramClient,
    chat_id: int,
    tagging_tasks: dict[int, asyncio.Task],
    tag_text: str = "Hii",
    status_event=None,
):
    current_task = asyncio.current_task()
    clean_tag_text = (tag_text or "Hii").strip() or "Hii"
    tagged_count = 0
    total_count = 0
    stopped_early = False

    try:
        targets = await _collect_group_targets(client, chat_id)
        total_count = len(targets)

        if not targets:
            await client.send_message(chat_id, "⚠️ Is group mein tag karne ke liye koi member nahi mila.")
            return

        start_text = f"🚀✨ Tagall Started! ({total_count}) — {clean_tag_text}"
        if status_event is not None:
            try:
                await status_event.edit(start_text)
            except Exception:
                await client.send_message(chat_id, start_text)
        else:
            await client.send_message(chat_id, start_text)

        for uid, uname in targets:
            if tagging_tasks.get(chat_id) is not current_task:
                stopped_early = True
                break
            await client.send_message(
                chat_id,
                f'✨ <a href="tg://user?id={uid}">{uname}</a> — {clean_tag_text}',
                parse_mode="html",
            )
            tagged_count += 1
            await asyncio.sleep(TAG_DELAY_SECONDS + random.uniform(0.2, 0.8))

        status_title = "🛑✨ Tagall Stopped!" if stopped_early else "✅🎉 Tagall Completed!"
        await client.send_message(chat_id, f"{status_title} ({tagged_count}/{total_count})")
    except asyncio.CancelledError:
        stopped_early = True
        await client.send_message(chat_id, f"🛑✨ Tagall Stopped! ({tagged_count}/{total_count})")
        raise
    finally:
        if tagging_tasks.get(chat_id) is current_task:
            tagging_tasks.pop(chat_id, None)


def _stop_tagall_task(tagging_tasks: dict[int, asyncio.Task], chat_id: int) -> bool:
    task = tagging_tasks.pop(chat_id, None)
    if not task:
        return False
    if not task.done():
        task.cancel()
    return True


async def _is_userbot_mentioned(event, me) -> bool:
    raw = (event.raw_text or "").lower()
    if me and me.username and f"@{me.username.lower()}" in raw:
        return True
    if me and f"tg://user?id={me.id}" in raw:
        return True
    if event.is_reply:
        try:
            replied = await event.get_reply_message()
            if replied and me and replied.sender_id == me.id:
                return True
        except Exception:
            pass
    return False


async def _send_quit_alert(client: TelegramClient, chat_id: int, user):
    uname = _clean_mention_name(user)
    uid = getattr(user, "id", None) if user else None
    mention = f'<a href="tg://user?id={uid}">{uname}</a>' if uid else uname
    await client.send_message(chat_id, f"{QUIT_MESSAGE}\n👤 {mention}", parse_mode="html")


async def attach_userbot_handlers(client: TelegramClient, host_state: dict, active_hosts_ref: dict):
    raid_users: set[int] = host_state["raid_users"]
    approved_users: set[int] = host_state.setdefault("approved_users", set())
    host_state.setdefault("background_tasks", {})
    host_state.setdefault("task_seq", 100)
    host_state.setdefault("ping_owner", None)
    host_state.setdefault("ping_emoji", "⚡")
    host_state.setdefault("custom_welcome", None)
    host_state.setdefault("welcome_enabled", True)
    host_state.setdefault("quit_enabled", True)
    host_state.setdefault("autoreply_msg", None)
    host_state.setdefault("raid_channel", None)
    host_state.setdefault("antisafe_enabled", False)
    host_state.setdefault("pending_clearall", False)
    host_state.setdefault("profile_backup", None)
    host_state.setdefault("last_msg", {})
    host_state.setdefault("last_shayari", {})
    host_state.setdefault("last_joke", {})

    tagging_tasks: dict[int, asyncio.Task] = host_state["tagging_tasks"]
    welcomed_users: set[int] = host_state["welcomed_users"]
    me = await client.get_me()
    my_id = me.id if me else 0

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_cmd(event):
        start_ts = time.perf_counter()
        emoji = host_state.get("ping_emoji") or "⚡"
        owner_tag = host_state.get("ping_owner")
        elapsed_ms = int((time.perf_counter() - start_ts) * 1000)
        extra = f"\n👑 Owner: {_escape_html(owner_tag)}" if owner_tag else ""
        await event.edit(f"🏓 Pong! {emoji} <code>{max(1, elapsed_ms)}ms</code>{extra}", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.uptime$"))
    async def uptime_cmd(event):
        up = _format_duration(int(time.time() - host_state.get("started_at", time.time())))
        await event.edit(f"⏱️ Uptime: <b>{up}</b>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.info(?:\s+(.+))?$"))
    async def info_cmd(event):
        arg = (event.pattern_match.group(1) or "").strip()
        target = await _resolve_target_user(client, event, arg or None)
        if not target and not arg:
            target = await event.get_chat()
        if not target:
            await event.edit("⚠️ User ya chat nahi mila.")
            return
        uid = getattr(target, "id", "N/A")
        title = getattr(target, "title", None) or _clean_mention_name(target)
        uname = getattr(target, "username", None)
        uname_str = f"@{uname}" if uname else "None"
        await event.edit(
            f"ℹ️ <b>Info</b>\n"
            f"• Name/Title: <b>{_escape_html(str(title))}</b>\n"
            f"• ID: <code>{uid}</code>\n"
            f"• Username: {uname_str}",
            parse_mode="html",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.logout$"))
    async def logout_userbot_cmd(event):
        await event.edit("🚪 Logging out userbot...")
        try:
            await client.log_out()
        except Exception:
            await client.disconnect()

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tagall(?:\s+([\s\S]+))?$"))
    async def tagall_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Yeh command sirf group mein chalega.")
            return
        existing_task = tagging_tasks.get(event.chat_id)
        if existing_task and not existing_task.done():
            await event.edit("⏳ Is group mein tagall pehle se chal raha hai.")
            return
        tag_text = _extract_tag_text(event.raw_text or "")
        task = asyncio.create_task(
            _run_tagall_in_chat(
                client,
                event.chat_id,
                tagging_tasks,
                tag_text=tag_text,
                status_event=event,
            )
        )
        tagging_tasks[event.chat_id] = task

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stoptagall(?:\s+\d+)?$"))
    async def stoptagall_cmd(event):
        if _stop_tagall_task(tagging_tasks, event.chat_id):
            await event.edit("🛑✨ Tagall rok diya gaya hai!")
        else:
            await event.edit("ℹ️ Is group mein koi active tagall nahi chal raha.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopquit$"))
    async def stopquit_cmd(event):
        host_state["quit_enabled"] = False
        await event.edit("🛑🚪 User quit alert OFF kar diya gaya hai.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.startquit$"))
    async def startquit_cmd(event):
        host_state["quit_enabled"] = True
        await event.edit("✅🚪 User quit alert ON kar diya gaya hai.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.replyraid(?:\s+(.+))?$"))
    async def replyraid_add_cmd(event):
        arg = (event.pattern_match.group(1) or "").strip()
        target = await _resolve_target_user(client, event, arg or None)
        if not target:
            await event.edit("⚠️ Target user ka username/ID dein ya message par reply karein.")
            return
        raid_users.add(target.id)
        try:
            await event.delete()
        except Exception:
            pass
        await client.send_message(
            event.chat_id,
            f"🎯🔥 Auto-Reply / Raid ACTIVATED (DM + Group)!\n👤 Target: <code>{target.id}</code>",
            parse_mode="html",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dreplyraid(?:\s+(.+))?$"))
    async def replyraid_del_cmd(event):
        arg = (event.pattern_match.group(1) or "").strip()
        target = await _resolve_target_user(client, event, arg or None)
        if not target:
            await event.edit("⚠️ Target user ka username/ID dein ya message par reply karein.")
            return
        raid_users.discard(target.id)
        try:
            await event.delete()
        except Exception:
            pass
        await client.send_message(
            event.chat_id,
            f"🎯🛑 Auto-Reply / Raid DEACTIVATED (DM + Group) for <code>{target.id}</code>!",
            parse_mode="html",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.sraid\s+(\d+)(?:\s+(.+))?$"))
    async def sraid_cmd(event):
        count = max(1, min(50, int(event.pattern_match.group(1))))
        arg = (event.pattern_match.group(2) or "").strip()
        target = await _resolve_target_user(client, event, arg or None)
        prefix = _format_target_prefix(target)

        async def _worker():
            for _ in range(count):
                msg = _pick_shayari_message(host_state, target.id if target else my_id)
                await client.send_message(event.chat_id, f"{prefix}{msg}", parse_mode="html")
                await asyncio.sleep(1.2)

        task_id = _register_background_task(host_state, asyncio.create_task(_worker()))
        await event.edit(f"💌 Shayari raid started ({count} msgs) — Task ID: <code>{task_id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopsraid$"))
    async def stopsraid_cmd(event):
        stopped = _cancel_background_task(host_state)
        await event.edit(f"🛑 Shayari task stopped ({stopped}).")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.spam\s+(\d+)\s+([\s\S]+)$"))
    async def spam_cmd(event):
        count = max(1, min(100, int(event.pattern_match.group(1))))
        rest = event.pattern_match.group(2).strip()
        parts = rest.split(maxsplit=1)
        dest = event.chat_id
        msg_text = rest
        if parts and (parts[0].startswith("@") or re.fullmatch(r"-?\d{5,}", parts[0])):
            try:
                ent = await client.get_entity(int(parts[0]) if parts[0].lstrip("-").isdigit() else parts[0])
                dest = getattr(ent, "id", dest)
                msg_text = parts[1] if len(parts) > 1 else "Hello!"
            except Exception:
                pass

        async def _worker():
            for _ in range(count):
                await client.send_message(dest, msg_text)
                await asyncio.sleep(0.6)

        task_id = _register_background_task(host_state, asyncio.create_task(_worker()))
        await event.edit(f"✉️ Spam started ({count}x) — Task ID: <code>{task_id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tspam\s+([0-9.]+)\s+([\s\S]+)$"))
    async def tspam_cmd(event):
        delay = max(0.2, min(60.0, float(event.pattern_match.group(1))))
        rest = event.pattern_match.group(2).strip()
        tokens = rest.split()
        dest = event.chat_id
        idx = 0
        if tokens and (tokens[0].startswith("@") or re.fullmatch(r"-?\d{5,}", tokens[0])):
            try:
                ent = await client.get_entity(int(tokens[0]) if tokens[0].lstrip("-").isdigit() else tokens[0])
                dest = getattr(ent, "id", dest)
                idx += 1
            except Exception:
                pass
        count = 5
        if idx < len(tokens) and tokens[idx].isdigit():
            count = max(1, min(100, int(tokens[idx])))
            idx += 1
        msg_text = " ".join(tokens[idx:]).strip() or "Test"

        async def _worker():
            for _ in range(count):
                await client.send_message(dest, msg_text)
                await asyncio.sleep(delay)

        task_id = _register_background_task(host_state, asyncio.create_task(_worker()))
        await event.edit(f"⏱️ Timed spam started ({count}x, {delay}s) — Task ID: <code>{task_id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopspam(?:\s+(\d+))?$"))
    async def stopspam_cmd(event):
        tid = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else None
        stopped = _cancel_background_task(host_state, tid)
        await event.edit(f"🛑 Spam task stopped ({stopped}).")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.raid\s+(\d+)(?:\s+([\s\S]+))?$"))
    async def raid_cmd(event):
        count = max(1, min(100, int(event.pattern_match.group(1))))
        extra = (event.pattern_match.group(2) or "").strip()
        dest = event.chat_id
        target_user = None
        for tok in extra.split():
            if tok.startswith("@"):
                target_user = await _resolve_target_user(client, event, tok)
            elif re.fullmatch(r"-?\d{5,}", tok):
                try:
                    ent = await client.get_entity(int(tok))
                    dest = getattr(ent, "id", dest)
                except Exception:
                    pass
        if not target_user and event.is_reply:
            target_user = await _resolve_target_user(client, event, None)

        prefix = _format_target_prefix(target_user)

        async def _worker():
            for _ in range(count):
                line = _pick_random_message(host_state, target_user.id if target_user else my_id)
                await client.send_message(dest, f"{prefix}{line}", parse_mode="html")
                await asyncio.sleep(0.8)

        task_id = _register_background_task(host_state, asyncio.create_task(_worker()))
        await event.edit(f"💥 Raid started ({count}x) — Task ID: <code>{task_id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopraid(?:\s+(\d+))?$"))
    async def stopraid_cmd(event):
        tid = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else None
        stopped = _cancel_background_task(host_state, tid)
        await event.edit(f"🛑 Raid task stopped ({stopped}).")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.setraid\s+(\S+)$"))
    async def setraid_cmd(event):
        link = event.pattern_match.group(1).strip()
        try:
            ent = await client.get_entity(link)
            host_state["raid_channel"] = getattr(ent, "id", link)
            await event.edit(f"✅ CRAID source channel set: <code>{host_state['raid_channel']}</code>", parse_mode="html")
        except Exception as e:
            await event.edit(f"⚠️ Channel set nahi ho saka: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.craid\s+(\d+)$"))
    async def craid_cmd(event):
        count = max(1, min(100, int(event.pattern_match.group(1))))
        src = host_state.get("raid_channel")
        if not src:
            await event.edit("⚠️ Pehle <code>.setraid &lt;channel_link&gt;</code> se source channel set karein.", parse_mode="html")
            return
        rep = await event.get_reply_message() if event.is_reply else None

        async def _worker():
            msgs = []
            async for m in client.iter_messages(src, limit=50):
                if m.text or m.media:
                    msgs.append(m)
            if not msgs:
                return
            for i in range(count):
                src_msg = msgs[i % len(msgs)]
                await client.send_message(
                    event.chat_id,
                    src_msg.text or "⚡",
                    file=src_msg.media,
                    reply_to=rep.id if rep else None,
                )
                await asyncio.sleep(0.9)

        task_id = _register_background_task(host_state, asyncio.create_task(_worker()))
        await event.edit(f"⚡ CRAID started ({count}x) — Task ID: <code>{task_id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.broadcast\s+([\s\S]+)$"))
    async def broadcast_cmd(event):
        text = event.pattern_match.group(1).strip()
        sent_ok = 0
        async for dlg in client.iter_dialogs():
            if dlg.is_group or dlg.is_channel:
                try:
                    await client.send_message(dlg.id, text)
                    sent_ok += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
        await event.edit(f"📢 Broadcast sent to <b>{sent_ok}</b> chats.", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.autoreply\s+([\s\S]+)$"))
    async def autoreply_on_cmd(event):
        host_state["autoreply_msg"] = event.pattern_match.group(1).strip()
        await event.edit("🤖 Mention auto-reply <b>ON</b> kar diya gaya hai.", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dautoreply$"))
    async def autoreply_off_cmd(event):
        host_state["autoreply_msg"] = None
        await event.edit("🤖 Mention auto-reply <b>OFF</b> kar diya gaya hai.", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^\.antisafe\s+(on|off)$"))
    async def antisafe_cmd(event):
        mode = event.pattern_match.group(1).lower()
        host_state["antisafe_enabled"] = mode == "on"
        await event.edit(f"🛡️ AntiSafe <b>{mode.upper()}</b>.", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.approve$"))
    async def approve_cmd(event):
        if event.is_private and event.chat_id:
            approved_users.add(event.chat_id)
            await event.edit("✅ User approved for AntiSafe.")
        else:
            await event.edit("⚠️ Yeh command private DM mein use karein.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.sd$"))
    async def sd_cmd(event):
        if not event.is_reply:
            await event.edit("⚠️ Jis message/media ko save karna hai uspar reply karein.")
            return
        rep = await event.get_reply_message()
        try:
            if rep.media:
                bio = io.BytesIO()
                await client.download_media(rep, file=bio)
                bio.seek(0)
                bio.name = getattr(rep.file, "name", None) or "saved_media"
                await client.send_file("me", bio, caption=rep.text or "")
            else:
                await client.send_message("me", rep.text or "")
            await event.edit("💾 Saved Messages mein save ho gaya.")
        except Exception as e:
            await event.edit(f"⚠️ Save nahi ho saka: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.setwlcm\s+([\s\S]+)$"))
    async def setwlcm_cmd(event):
        host_state["custom_welcome"] = event.pattern_match.group(1).strip()
        host_state["welcome_enabled"] = True
        await event.edit("✅ Custom welcome message set ho gaya.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopwlcm$"))
    async def stopwlcm_cmd(event):
        host_state["welcome_enabled"] = False
        await event.edit("🛑 Welcome messages disable kar diye gaye hain.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.wlcmmssg$"))
    async def wlcmmssg_cmd(event):
        host_state["custom_welcome"] = None
        host_state["welcome_enabled"] = True
        await event.edit("♻️ Welcome configuration default par restore ho gayi.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stylish\s+([\s\S]+)$"))
    async def stylish_cmd(event):
        name = event.pattern_match.group(1).strip()
        b_txt = name.translate(_BOLD_SANS_MAP)
        await event.edit(
            f"✨ <b>Stylish Variations</b>\n"
            f"1. <code>{b_txt}</code>\n"
            f"2. <code>★ {b_txt} ★</code>\n"
            f"3. <code>꧁ {b_txt} ꧂</code>",
            parse_mode="html",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.changeowner\s+(\S+)$"))
    async def changeowner_cmd(event):
        host_state["ping_owner"] = event.pattern_match.group(1).strip()
        await event.edit(f"✅ Ping owner updated: {_escape_html(host_state['ping_owner'])}", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.setemoji\s+(.+)$"))
    async def setemoji_cmd(event):
        val = event.pattern_match.group(1).strip()
        if val.lower() == "off":
            host_state["ping_emoji"] = ""
            await event.edit("✅ Custom ping emoji removed.")
        else:
            host_state["ping_emoji"] = val
            await event.edit(f"✅ Custom ping emoji set: {val}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.clone(?:\s+(\S+))?$"))
    async def clone_cmd(event):
        arg = (event.pattern_match.group(1) or "").strip()
        target = await _resolve_target_user(client, event, arg or None)
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        try:
            me_full = await client(GetFullUserRequest("me"))
            if host_state.get("profile_backup") is None:
                host_state["profile_backup"] = {
                    "first_name": me.first_name or "",
                    "last_name": me.last_name or "",
                    "about": getattr(me_full.full_user, "about", "") or "",
                }
            t_full = await client(GetFullUserRequest(target))
            await client(
                UpdateProfileRequest(
                    first_name=getattr(target, "first_name", "") or "User",
                    last_name=getattr(target, "last_name", "") or "",
                    about=(getattr(t_full.full_user, "about", "") or "")[:70],
                )
            )
            photos = await client.get_profile_photos(target, limit=1)
            if photos:
                bio = io.BytesIO()
                await client.download_media(photos[0], file=bio)
                bio.seek(0)
                uploaded = await client.upload_file(bio)
                await client(UploadProfilePhotoRequest(file=uploaded))
            await event.edit(f"👤 Profile cloned: <b>{_clean_mention_name(target)}</b>", parse_mode="html")
        except Exception as e:
            await event.edit(f"⚠️ Clone error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dclone$"))
    async def dclone_cmd(event):
        backup = host_state.get("profile_backup")
        if not backup:
            await event.edit("⚠️ Koi saved profile backup nahi mila.")
            return
        try:
            await client(
                UpdateProfileRequest(
                    first_name=backup.get("first_name", ""),
                    last_name=backup.get("last_name", ""),
                    about=backup.get("about", ""),
                )
            )
            my_photos = await client.get_profile_photos("me", limit=1)
            if my_photos:
                await client(
                    DeletePhotosRequest(
                        id=[
                            types.InputPhoto(
                                id=my_photos[0].id,
                                access_hash=my_photos[0].access_hash,
                                file_reference=my_photos[0].file_reference,
                            )
                        ]
                    )
                )
            await event.edit("✅ Original profile restore ho gayi.")
        except Exception as e:
            await event.edit(f"⚠️ Restore error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.joke$"))
    async def joke_cmd(event):
        msg = _pick_joke_message(host_state, event.chat_id or my_id)
        await event.edit(msg, parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.flip$"))
    async def flip_cmd(event):
        await event.edit(f"🪙 Coin Flip: <b>{random.choice(['Heads', 'Tails'])}</b>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.roll\s+(\d+)$"))
    async def roll_cmd(event):
        upper = max(1, int(event.pattern_match.group(1)))
        await event.edit(f"🎲 Roll (1-{upper}): <b>{random.randint(1, upper)}</b>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^\.rps\s+(rock|paper|scissors)$"))
    async def rps_cmd(event):
        user_choice = event.pattern_match.group(1).lower()
        bot_choice = random.choice(["rock", "paper", "scissors"])
        wins = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}
        if user_choice == bot_choice:
            res = "Draw!"
        elif (user_choice, bot_choice) in wins:
            res = "You Win!"
        else:
            res = "Bot Wins!"
        await event.edit(f"✊✋✌️ You: <b>{user_choice}</b> vs <b>{bot_choice}</b> — <b>{res}</b>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.calc\s+([\s\S]+)$"))
    async def calc_cmd(event):
        expr = event.pattern_match.group(1).strip()
        try:
            ans = _safe_calc(expr)
            await event.edit(f"🧮 <code>{_escape_html(expr)}</code> = <b>{_escape_html(ans)}</b>", parse_mode="html")
        except Exception as e:
            await event.edit(f"⚠️ Calc error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ban(?:\s+(\S+)(?:\s+([\s\S]+))?)?$"))
    async def ban_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        rights = types.ChatBannedRights(until_date=None, view_messages=True)
        await client(EditBannedRequest(event.chat_id, target.id, rights))
        reason = (event.pattern_match.group(2) or "").strip()
        await event.edit(f"🚫 Banned {_clean_mention_name(target)}" + (f" — {reason}" if reason else ""))

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.unban(?:\s+(\S+))?$"))
    async def unban_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        rights = types.ChatBannedRights(until_date=None, view_messages=False)
        await client(EditBannedRequest(event.chat_id, target.id, rights))
        await event.edit(f"✅ Unbanned {_clean_mention_name(target)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.mute(?:\s+(\S+)(?:\s+(\d+[smhd]))?(?:\s+([\s\S]+))?)?$"))
    async def mute_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        dur_secs = _parse_duration_seconds(event.pattern_match.group(2))
        until = int(time.time()) + dur_secs if dur_secs else None
        rights = types.ChatBannedRights(until_date=until, send_messages=True)
        await client(EditBannedRequest(event.chat_id, target.id, rights))
        await event.edit(f"🔇 Muted {_clean_mention_name(target)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.unmute(?:\s+(\S+))?$"))
    async def unmute_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        rights = types.ChatBannedRights(until_date=None, send_messages=False)
        await client(EditBannedRequest(event.chat_id, target.id, rights))
        await event.edit(f"🔊 Unmuted {_clean_mention_name(target)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.kick(?:\s+(\S+)(?:\s+([\s\S]+))?)?$"))
    async def kick_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ Target user dein ya reply karein.")
            return
        ban_r = types.ChatBannedRights(until_date=None, view_messages=True)
        unban_r = types.ChatBannedRights(until_date=None, view_messages=False)
        await client(EditBannedRequest(event.chat_id, target.id, ban_r))
        await client(EditBannedRequest(event.chat_id, target.id, unban_r))
        await event.edit(f"👢 Kicked {_clean_mention_name(target)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.clear\s+(\d+)$"))
    async def clear_cmd(event):
        cnt = max(1, min(100, int(event.pattern_match.group(1))))
        msg_ids = []
        async for m in client.iter_messages(event.chat_id, limit=cnt + 1):
            if m.id != event.id:
                msg_ids.append(m.id)
        if msg_ids:
            await client.delete_messages(event.chat_id, msg_ids)
        await event.edit(f"🧹 Deleted {len(msg_ids)} messages.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.rmall$"))
    async def rmall_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        removed = 0
        ban_r = types.ChatBannedRights(until_date=None, view_messages=True)
        async for p in client.iter_participants(event.chat_id):
            if p.id != my_id and not getattr(p, "bot", False):
                try:
                    await client(EditBannedRequest(event.chat_id, p.id, ban_r))
                    removed += 1
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
        await event.edit(f"🗑️ Removed {removed} members.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.add(?:\s+([\s\S]+))?$"))
    async def add_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        raw = (event.pattern_match.group(1) or "").strip()
        if not raw:
            await event.edit("⚠️ Kam se kam ek @username dein.")
            return
        users = []
        for tok in raw.split():
            u = await _resolve_target_user(client, event, tok)
            if u:
                users.append(u)
        if not users:
            await event.edit("⚠️ Valid users nahi mile.")
            return
        try:
            await client(InviteToChannelRequest(event.chat_id, users))
            await event.edit(f"✅ Invited {len(users)} user(s).")
        except Exception as e:
            await event.edit(f"⚠️ Add error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^/invall(?:\s+(\S+))?$"))
    async def invall_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Sirf group mein chalega.")
            return
        src_tok = (event.pattern_match.group(1) or "").strip()
        if not src_tok:
            await event.edit("⚠️ Usage: /invall @PublicGroup")
            return
        added = 0
        try:
            src_ent = await client.get_entity(int(src_tok) if src_tok.lstrip("-").isdigit() else src_tok)
            async for p in client.iter_participants(src_ent, limit=50):
                if p.id != my_id and not getattr(p, "bot", False):
                    try:
                        await client(InviteToChannelRequest(event.chat_id, [p]))
                        added += 1
                        await asyncio.sleep(1.0)
                    except Exception:
                        pass
            await event.edit(f"👥 Invall attempted/added: {added}")
        except Exception as e:
            await event.edit(f"⚠️ Invall error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^\.clearall(?:\s+(confirm))?$"))
    async def clearall_cmd(event):
        conf = (event.pattern_match.group(1) or "").lower()
        if conf != "confirm":
            host_state["pending_clearall"] = True
            await event.edit(
                "☢️ <b>Nuclear Clear Confirmation</b>\n"
                "Current chat ki history clear karne ke liye <code>.clearall confirm</code> bhejein.",
                parse_mode="html",
            )
            return
        if not host_state.get("pending_clearall"):
            await event.edit("⚠️ Pehle <code>.clearall</code> likhein.", parse_mode="html")
            return
        host_state["pending_clearall"] = False
        try:
            await client(functions.messages.DeleteHistoryRequest(peer=event.chat_id, max_id=0, just_clear=True, revoke=True))
            await event.edit("☢️ Chat history cleared.")
        except Exception as e:
            await event.edit(f"⚠️ Clearall error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.addsudo\s+(\S+)$"))
    async def addsudo_cmd(event):
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ User nahi mila.")
            return
        sudos = host_state.setdefault("ub_sudos", set())
        sudos.add(target.id)
        await event.edit(f"✅ Sudo added: <code>{target.id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.rmsudo\s+(\S+)$"))
    async def rmsudo_cmd(event):
        target = await _resolve_target_user(client, event, event.pattern_match.group(1))
        if not target:
            await event.edit("⚠️ User nahi mila.")
            return
        sudos = host_state.setdefault("ub_sudos", set())
        sudos.discard(target.id)
        await event.edit(f"🗑️ Sudo removed: <code>{target.id}</code>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.activeusers$"))
    async def activeusers_cmd(event):
        ids = list(active_hosts_ref.keys())
        if not ids:
            await event.edit("ℹ️ Koi active hosted user nahi hai.")
            return
        lines = "\n".join(f"• <code>{u}</code>" for u in ids)
        await event.edit(f"👥 <b>Active Hosted Users ({len(ids)}):</b>\n{lines}", parse_mode="html")

    @client.on(events.ChatAction)
    async def chat_action_handler(event):
        if not event.is_group:
            return
        if (event.user_left or event.user_kicked) and host_state.get("quit_enabled", True):
            try:
                user = await event.get_user()
                await _send_quit_alert(client, event.chat_id, user)
            except Exception:
                await client.send_message(event.chat_id, QUIT_MESSAGE)
            return

        if (event.user_joined or event.user_added) and host_state.get("welcome_enabled", True):
            custom = host_state.get("custom_welcome")
            if custom:
                try:
                    u = await event.get_user()
                    uname = _clean_mention_name(u)
                    await client.send_message(event.chat_id, custom.replace("{name}", uname))
                except Exception:
                    await client.send_message(event.chat_id, custom)

    @client.on(events.Raw)
    async def raw_quit_handler(event):
        if not host_state.get("quit_enabled", True):
            return
        if isinstance(event, types.UpdateChannelParticipant):
            if event.prev_participant and not event.new_participant:
                try:
                    chat_id = int(f"-100{event.channel_id}")
                    uid = getattr(event.prev_participant, "user_id", None)
                    user_obj = await client.get_entity(uid) if uid else None
                    await _send_quit_alert(client, chat_id, user_obj)
                except Exception:
                    pass

    @client.on(events.NewMessage(incoming=True))
    async def dm_and_group_handler(event):
        sender_id = event.sender_id
        if not sender_id or sender_id == my_id:
            return

        if event.is_group:
            mentioned = await _is_userbot_mentioned(event, me)
            if sender_id in raid_users and mentioned:
                reply_text = _pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text, parse_mode="html")
                return

            ar_msg = host_state.get("autoreply_msg")
            if ar_msg and mentioned:
                await asyncio.sleep(0.5)
                await event.reply(ar_msg)
            return

        if event.is_private:
            if host_state.get("antisafe_enabled") and sender_id not in approved_users:
                try:
                    await event.delete()
                except Exception:
                    pass
                return

            if sender_id in raid_users:
                reply_text = _pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text, parse_mode="html")
                return

            if sender_id not in welcomed_users:
                welcomed_users.add(sender_id)
                await asyncio.sleep(0.5)
                await event.reply(FIRST_DM_HEADER, link_preview=False)
