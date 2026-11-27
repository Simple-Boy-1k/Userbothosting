import asyncio
import json
import os
import random
import re
from pathlib import Path
from pymongo import MongoClient
from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.sessions import StringSession

STORE_FILE = Path("hoster_data.json")

# ================= FIRST DM TEXT & QUIT ALERT =================
FIRST_DM_HEADER = "Hey welcome to my dm! How are you...? 😊"
QUIT_MESSAGE = "🚪👋 Member group se quit kar gaya hai!"

TAG_DELAY_SECONDS = 2.5

RANDOM_MESSAGES = [
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

ACTIVE_HOSTS = {}
PENDING_LOGINS = {}
LOGIN_FLOW = {}

_db = None


def _get_db():
    global _db
    if _db is not None:
        return _db
    uri = os.getenv("MONGO_URI", "").strip()
    if not uri:
        return None
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    _db = client["zudo_hoster_db"]
    return _db


def _default_local_store() -> dict:
    return {
        "sessions": {},
        "sudos": [],
        "blocked": [],
        "dp_url": "",
        "secret_mode": False,
        "force_join_chat_id": 0,
        "force_join_link": "",
        "support_group_url": "",
    }


def _load_local() -> dict:
    base = _default_local_store()
    if STORE_FILE.exists():
        try:
            loaded = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                base.update(loaded)
        except Exception:
            pass
    return base


def _save_local(data: dict):
    STORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_session(user_id: int, string_session: str):
    db = _get_db()
    if db is not None:
        db["sessions"].update_one(
            {"_id": str(user_id)},
            {"$set": {"user_id": int(user_id), "session": string_session}},
            upsert=True,
        )
        return
    data = _load_local()
    data["sessions"][str(user_id)] = string_session
    _save_local(data)


def delete_session(user_id: int):
    db = _get_db()
    if db is not None:
        db["sessions"].delete_one({"_id": str(user_id)})
        return
    data = _load_local()
    data["sessions"].pop(str(user_id), None)
    _save_local(data)


def load_all_sessions() -> dict[int, str]:
    db = _get_db()
    if db is not None:
        out = {}
        for doc in db["sessions"].find({}):
            uid = doc.get("user_id") or doc.get("_id")
            sess = doc.get("session")
            if uid and sess and str(uid).isdigit():
                out[int(uid)] = sess
        return out
    data = _load_local()
    return {int(k): v for k, v in data.get("sessions", {}).items() if str(k).isdigit() and v}


def get_meta_state() -> dict:
    db = _get_db()
    if db is not None:
        doc = db["meta"].find_one({"_id": "config"}) or {}
        return {
            "sudos": list(dict.fromkeys(int(x) for x in doc.get("sudos", []) if str(x).isdigit())),
            "blocked": list(dict.fromkeys(int(x) for x in doc.get("blocked", []) if str(x).isdigit())),
            "dp_url": str(doc.get("dp_url") or ""),
            "secret_mode": bool(doc.get("secret_mode", False)),
            "force_join_chat_id": doc.get("force_join_chat_id", 0),
            "force_join_link": str(doc.get("force_join_link") or ""),
            "support_group_url": str(doc.get("support_group_url") or ""),
        }
    data = _load_local()
    return {
        "sudos": list(dict.fromkeys(int(x) for x in data.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in data.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(data.get("dp_url") or ""),
        "secret_mode": bool(data.get("secret_mode", False)),
        "force_join_chat_id": data.get("force_join_chat_id", 0),
        "force_join_link": str(data.get("force_join_link") or ""),
        "support_group_url": str(data.get("support_group_url") or ""),
    }


def save_meta_state(meta: dict):
    clean = {
        "sudos": list(dict.fromkeys(int(x) for x in meta.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in meta.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(meta.get("dp_url") or ""),
        "secret_mode": bool(meta.get("secret_mode", False)),
        "force_join_chat_id": int(meta.get("force_join_chat_id") or 0),
        "force_join_link": str(meta.get("force_join_link") or ""),
        "support_group_url": str(meta.get("support_group_url") or ""),
    }
    db = _get_db()
    if db is not None:
        db["meta"].update_one({"_id": "config"}, {"$set": clean}, upsert=True)
        return
    data = _load_local()
    data.update(clean)
    _save_local(data)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


async def send_first_dm_card(event):
    await event.reply(FIRST_DM_HEADER, link_preview=False)


def pick_random_message(host_state: dict, target_id: int) -> str:
    valid_msgs = [m.strip() for m in RANDOM_MESSAGES if isinstance(m, str) and m.strip()]
    if not valid_msgs:
        return "<b>Hello! 👋</b>"
    if len(valid_msgs) == 1:
        return valid_msgs[0]
    last_msg = host_state["last_msg"].get(target_id)
    pool = [m for m in valid_msgs if m != last_msg]
    chosen = random.choice(pool or valid_msgs)
    host_state["last_msg"][target_id] = chosen
    return chosen


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


async def _attach_handlers(client: TelegramClient, host_state: dict):
    raid_users = host_state["raid_users"]
    tagging_tasks: dict[int, asyncio.Task] = host_state["tagging_tasks"]
    welcomed_users = host_state["welcomed_users"]
    me = await client.get_me()
    my_id = me.id if me else 0

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_cmd(event):
        await event.edit("🏓 Pong! Userbot is active.")

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

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stoptagall$"))
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

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.replyraid\s+(\d+)$"))
    async def replyraid_add_cmd(event):
        target_id = int(event.pattern_match.group(1))
        raid_users.add(target_id)
        try:
            await event.delete()
        except Exception:
            pass
        await client.send_message(
            event.chat_id,
            f"🎯🔥 Auto-Reply / Raid ACTIVATED (DM + Group)!\n👤 Target: {target_id}",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dreplyraid\s+(\d+)$"))
    async def replyraid_del_cmd(event):
        target_id = int(event.pattern_match.group(1))
        raid_users.discard(target_id)
        try:
            await event.delete()
        except Exception:
            pass
        await client.send_message(
            event.chat_id,
            f"🎯🛑 Auto-Reply / Raid DEACTIVATED (DM + Group) for {target_id}!",
        )

    @client.on(events.ChatAction)
    async def quit_action_handler(event):
        if not event.is_group or not host_state.get("quit_enabled", True):
            return
        if event.user_left or event.user_kicked:
            try:
                user = await event.get_user()
                await _send_quit_alert(client, event.chat_id, user)
            except Exception:
                await client.send_message(event.chat_id, QUIT_MESSAGE)

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
            if sender_id in raid_users and await _is_userbot_mentioned(event, me):
                reply_text = pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text, parse_mode="html")
            return

        if event.is_private:
            if sender_id in raid_users:
                reply_text = pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text, parse_mode="html")
                return

            if sender_id not in welcomed_users:
                welcomed_users.add(sender_id)
                await asyncio.sleep(0.5)
                await send_first_dm_card(event)


def _cleanup_host_tasks(host_state: dict):
    tasks: dict[int, asyncio.Task] = host_state.get("tagging_tasks") or {}
    for cid in list(tasks.keys()):
        _stop_tagall_task(tasks, cid)


async def start_client_from_session(
    user_id: int,
    string_session: str,
    api_id: int,
    api_hash: str,
    persist: bool = True,
    is_restart: bool = False,
) -> tuple[bool, str]:
    existing = ACTIVE_HOSTS.pop(user_id, None)
    if existing:
        _cleanup_host_tasks(existing)
        try:
            await existing["client"].disconnect()
        except Exception:
            pass

    cleaned = string_session.strip()
    client = TelegramClient(
        StringSession(cleaned),
        api_id,
        api_hash,
        device_model="Desktop",
        system_version="Windows 11",
        app_version="5.6.3 x64",
        lang_code="en",
        system_lang_code="en-US",
    )
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return False, "Session valid ya authorized nahi hai."

        host_state = {
            "client": client,
            "session": cleaned,
            "raid_users": set(),
            "tagging_tasks": {},
            "welcomed_users": set(),
            "last_msg": {},
            "quit_enabled": True,
        }
        ACTIVE_HOSTS[user_id] = host_state
        await _attach_handlers(client, host_state)
        asyncio.create_task(client.run_until_disconnected())

        if persist:
            save_session(user_id, cleaned)

        if is_restart:
            return True, "<b>Success Userbot Restarted!</b>\nUse .ping."
        return True, "<b>Success Userbot Hosted!</b>\nUse .ping to check."
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"Host karne mein error aaya: {e}"


async def send_login_code(user_id: int, phone: str, api_id: int, api_hash: str) -> tuple[bool, str]:
    old = PENDING_LOGINS.pop(user_id, None)
    if old and old.get("client"):
        try:
            await old["client"].disconnect()
        except Exception:
            pass

    cleaned_phone = "".join(ch for ch in phone.strip() if ch.isdigit() or ch == "+")
    if not cleaned_phone.startswith("+"):
        cleaned_phone = f"+{cleaned_phone}"

    client = TelegramClient(
        StringSession(),
        api_id,
        api_hash,
        device_model="Desktop",
        system_version="Windows 11",
        app_version="5.6.3 x64",
        lang_code="en",
        system_lang_code="en-US",
    )
    try:
        await client.connect()
        sent = await client.send_code_request(cleaned_phone)
        PENDING_LOGINS[user_id] = {
            "step": "otp",
            "phone": cleaned_phone,
            "phone_code_hash": sent.phone_code_hash,
            "client": client,
        }
        return True, "🔑 Enter OTP (e.g., 1 2 3 4 5): Hurry, expires in 1-2 min!"
    except PhoneNumberInvalidError:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, "Phone number invalid hai. Country code ke saath sahi number daalein (jaise +919876543210)."
    except FloodWaitError as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"Telegram rate limit laga hai. {e.seconds} seconds baad try karein."
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"OTP bhejne mein error aaya: {e}"


async def submit_otp_code(user_id: int, otp_text: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "otp":
        return "error", "Koi active OTP request nahi mila. Pehle /host likhein."

    code = "".join(ch for ch in otp_text if ch.isdigit())
    if not code:
        return "retry", "Valid numeric OTP bhejein."

    client = pending["client"]
    phone = pending["phone"]
    phone_code_hash = pending["phone_code_hash"]

    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        session_str = client.session.save()
        await client.disconnect()
        PENDING_LOGINS.pop(user_id, None)

        ok, msg = await start_client_from_session(user_id, session_str, api_id, api_hash, persist=True)
        return ("done" if ok else "error"), msg
    except SessionPasswordNeededError:
        pending["step"] = "2fa"
        return "2fa", "🔒 Enter 2FA Password:"
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        PENDING_LOGINS.pop(user_id, None)
        return "error", f"Login fail ho gaya: {e}"


async def submit_2fa_password(user_id: int, password: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "2fa":
        return "error", "Koi active 2FA step nahi mila. Pehle /host likhein."

    client = pending["client"]
    try:
        await client.sign_in(password=password.strip())
        session_str = client.session.save()
        await client.disconnect()
        PENDING_LOGINS.pop(user_id, None)

        ok, msg = await start_client_from_session(user_id, session_str, api_id, api_hash, persist=True)
        return ("done" if ok else "error"), msg
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        PENDING_LOGINS.pop(user_id, None)
        return "error", f"2FA login fail ho gaya: {e}"


async def cancel_pending_login(user_id: int):
    pending = PENDING_LOGINS.pop(user_id, None)
    if pending and pending.get("client"):
        try:
            await pending["client"].disconnect()
        except Exception:
            pass


async def restart_user_account(user_id: int, api_id: int, api_hash: str) -> tuple[bool, str]:
    info = ACTIVE_HOSTS.get(user_id)
    if info:
        return await start_client_from_session(
            user_id, info["session"], api_id, api_hash, persist=True, is_restart=True
        )

    saved = load_all_sessions()
    if user_id in saved:
        return await start_client_from_session(
            user_id, saved[user_id], api_id, api_hash, persist=True, is_restart=True
        )

    return False, "Aapka koi hosted account nahi mila. Pehle /host likhein."


async def logout_user_account(user_id: int) -> tuple[bool, str]:
    await cancel_pending_login(user_id)
    info = ACTIVE_HOSTS.pop(user_id, None)
    delete_session(user_id)

    if not info:
        return False, "Logout karne ke liye koi active hosted account nahi mila."

    _cleanup_host_tasks(info)
    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "<b>Success Userbot Logged Out!</b>\nUse /host to re-host."


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_sessions()
    for uid, session_str in saved.items():
        await start_client_from_session(uid, session_str, api_id, api_hash, persist=False)
