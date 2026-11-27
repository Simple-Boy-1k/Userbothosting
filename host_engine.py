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

# ================= GROUP LINKS & FIRST DM TEXT =================
GROUP_LINK_1 = "https://t.me/+CBnAUbPjGdlmYzBk"
GROUP_LINK_2 = "https://t.me/+EVbG4sFK-tg1NjA1"

BTN_1_TEXT = "💬 𝗚𝗜𝗥𝗟𝗦 𝗚𝗥𝗢𝗨𝗣 𝟭"
BTN_2_TEXT = "🔥 𝗚𝗜𝗥𝗟𝗦 𝗚𝗥𝗢𝗨𝗣 𝟮"

FIRST_DM_HEADER = "🖤 𝗝𝗢𝗜𝗡 𝗠𝗬 𝗚𝗖 — Good Vibes, Crazy People &amp; Unlimited Fun! 😎"
QUIT_MESSAGE = "🚪👋 <b>𝗠𝗲𝗺𝗯𝗲𝗿 𝗴𝗿𝗼𝘂𝗽 𝘀𝗲 𝗾𝘂𝗶𝘁 𝗸𝗮𝗿 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶!</b>"

TAG_DELAY_SECONDS = 1.2

RANDOM_MESSAGES = [
    "<blockquote><b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b></blockquote>",
    "<blockquote><b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b></blockquote>",
    "<blockquote><b>𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗣𝗘 𝗖𝗛𝗔𝗟𝗔 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣</b></blockquote>",
    "<blockquote><b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b></blockquote>",
    "<blockquote><b>𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗦𝗘𝗘𝗗𝗛𝗔 𝗕𝗢𝗟 𝗥𝗔𝗛𝗔 𝗛𝗨𝗡</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗧𝗡𝗜 𝗚𝗔𝗟𝗜𝗬𝗔𝗡 𝗞𝗛𝗔𝗬𝗘𝗚𝗔 𝗔𝗝</b></blockquote>",
    "<blockquote><b>𝗕𝗘𝗦𝗔𝗡 𝗞𝗘 𝗟𝗔𝗗𝗗𝗨 𝗕𝗛𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗕𝗨 🤩🥳🔥😈</b></blockquote>",
    "<blockquote><b>𝗦𝗣𝗘𝗘𝗗 𝗠𝗔𝗧𝗖𝗛 𝗡𝗔𝗛𝗜 𝗛𝗢 𝗥𝗔𝗛𝗜 𝗞𝗬𝗔</b></blockquote>",
    "<blockquote><b>𝗞𝘂𝘁𝘁𝗲 𝗸𝗶 𝗷𝗮𝗮𝘁</b></blockquote>",
    "<blockquote><b>𝗔𝗽𝗻𝗶 𝗷𝗮𝗴𝗮𝗵 𝗽𝗲 𝗯𝗮𝗶𝘁𝗵 𝗷𝗮𝗮</b></blockquote>",
    "<blockquote><b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b></blockquote>",
    "<blockquote><b>𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 💣</b></blockquote>",
    "<blockquote><b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b></blockquote>",
    "<blockquote><b>𝗔𝗽𝗻𝗶 𝗷𝗮𝗴𝗮𝗵 𝗽𝗲 𝗯𝗮𝗶𝘁𝗵 𝗷𝗮𝗮</b></blockquote>",
    "<blockquote><b>𝗝𝗵𝗮𝗮𝗻𝘁 𝗸𝗲 𝗽𝗶𝘀𝘀𝘂</b></blockquote>",
    "<blockquote><b>𝗔𝗔𝗚 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗖𝗛𝗔𝗧 𝗠𝗘𝗜𝗡 🔥🔥💦😆😆</b></blockquote>",
    "<blockquote><b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b></blockquote>",
    "<blockquote><b>𝗣𝗨𝗥𝗔 𝗙𝗔𝗔𝗗 𝗞𝗘 𝗥𝗔𝗞𝗛 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 😆💦🤤</b></blockquote>",
    "<blockquote><b>𝗠𝗠𝗦 𝗕𝗔𝗡𝗔 𝗖𝗛𝗨𝗞𝗔 𝗛𝗔𝗜 𝗔𝗕 𝗗𝗘𝗞𝗛</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b></blockquote>",
    "<blockquote><b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗔𝗟 𝗞𝗘 𝟱𝟬𝟬 𝗞𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔 💰💰🤩</b></blockquote>",
    "<blockquote><b>𝗦𝗨𝗗𝗢 𝗟𝗔𝗚𝗔 𝗞𝗘 𝟵𝟵𝟵𝟵 𝗖𝗛𝗔𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 🤩🥳🔥</b></blockquote>",
    "<blockquote><b>𝗧𝗨𝗝𝗛𝗘 𝗔𝗕 𝗧𝗔𝗞 𝗦𝗔𝗠𝗔𝗝𝗛 𝗡𝗔𝗛𝗜 𝗔𝗬𝗔 𝗞𝗬𝗔 🤩👊👤😍</b></blockquote>",
    "<blockquote><b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b></blockquote>",
    "<blockquote><b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b></blockquote>",
    "<blockquote><b>𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘𝗜𝗡 𝗦𝗛𝗢𝗥 𝗛𝗔𝗜 𝗔𝗝 💋💋💦</b></blockquote>",
    "<blockquote><b>𝗦𝗨𝗡 𝗦𝗨𝗡 𝗦𝗨𝗔𝗥 𝗞𝗘 𝗣𝗜𝗟𝗟𝗘 𝗕𝗔𝗔𝗧 𝗦𝗨𝗡</b></blockquote>",
    "<blockquote><b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b></blockquote>",
    "<blockquote><b>𝗖𝗛𝗘𝗘𝗠𝗦 𝗦𝗘 𝗕𝗔𝗝𝗪𝗔 𝗗𝗨𝗡𝗚𝗔 𝗕𝗔𝗕𝗨 💦🤣</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦𝗦</b></blockquote>",
    "<blockquote><b>𝗗𝗘𝗧𝗢𝗟 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗦𝗔𝗔𝗙 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔</b></blockquote>",
    "<blockquote><b>𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗔𝗥 𝗗𝗜𝗬𝗘 𝗛𝗔𝗜𝗡 🤖🙏🤔</b></blockquote>",
    "<blockquote><b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b></blockquote>",
    "<blockquote><b>𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝 😱🤮👺</b></blockquote>",
    "<blockquote><b>𝗥𝗔𝗡𝗜𝗗𝗜𝗜𝗜</b></blockquote>",
    "<blockquote><b>𝗜𝗧𝗡𝗔 𝗚𝗛𝗨𝗠𝗔𝗨𝗡𝗚𝗔 𝗞𝗜 𝗖𝗛𝗔𝗞𝗞𝗔𝗥 𝗔𝗔 𝗝𝗔𝗬𝗘𝗚𝗔 💦💋</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗧𝗡𝗔 𝗖𝗛𝗔𝗟𝗔𝗨𝗡 𝗔𝗕 𝗢𝗥..</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b></blockquote>",
    "<blockquote><b>𝗣𝗨𝗥𝗔 𝗦𝗜𝗦𝗧𝗘𝗠 𝗛𝗜𝗟𝗔 𝗗𝗨𝗡𝗚𝗔 𝗔𝗝</b></blockquote>",
    "<blockquote><b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b></blockquote>",
    "<blockquote><b>𝗨𝗣𝗔𝗥 𝗡𝗜𝗖𝗛𝗘 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗦𝗔𝗕 🆙🆒😙</b></blockquote>",
    "<blockquote><b>𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝟯𝟬𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 💥😂😎</b></blockquote>",
    "<blockquote><b>𝗩𝗜𝗗𝗘𝗢 𝗕𝗔𝗡𝗔 𝗞𝗘 𝗡𝗘𝗘𝗟𝗔𝗠 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 💦💋</b></blockquote>",
    "<blockquote><b>𝗞𝗜𝗦𝗔𝗡 𝗞𝗢 𝗞𝗛𝗢𝗗𝗡𝗔 𝗢𝗥</b></blockquote>",
    "<blockquote><b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b></blockquote>",
    "<blockquote><b>𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘𝗜𝗡 𝗦𝗛𝗢𝗥 𝗛𝗔𝗜 𝗔𝗝 🤤🤣</b></blockquote>",
    "<blockquote><b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b></blockquote>",
    "<blockquote><b>𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗪𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗦𝗔𝗟𝗔𝗔𝗠 🤩🤩</b></blockquote>",
    "<blockquote><b>𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟 𝗞𝗛𝗔𝗧𝗔𝗠 ☝🏻☝🏻😬</b></blockquote>",
    "<blockquote><b>𝗞𝗔𝗔𝗟𝗔 𝗦𝗜𝗦𝗧𝗘𝗠 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗔 𝗛𝗔𝗜 𝗔𝗝</b></blockquote>",
    "<blockquote><b>𝗨𝗹𝗹𝘂 𝗸𝗲 𝗽𝗮𝘁𝘁𝗵𝗲</b></blockquote>",
    "<blockquote><b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b></blockquote>",
    "<blockquote><b>𝗚𝗢𝗢𝗚𝗟𝗘 𝗣𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 👻🔥</b></blockquote>",
    "<blockquote><b>𝗔𝗣𝗡𝗘 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗣𝗘𝗛𝗖𝗛𝗔𝗔𝗡 𝗟𝗘 𝗕𝗔𝗕𝗨</b></blockquote>",
    "<blockquote><b>𝗦𝗔𝗕 𝗕𝗢𝗟𝗧𝗘 𝗛𝗔𝗜𝗡 𝗕𝗔𝗔𝗣 𝗛𝗨𝗡 𝗠𝗔𝗜𝗡 🤣🤣</b></blockquote>",
    "<blockquote><b>𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗭𝗔𝗔𝗥 𝗠𝗘𝗜𝗡 𝗕𝗔𝗝𝗔 𝗗𝗔𝗟𝗔 🤣🤣💋</b></blockquote>",
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
        "group_links": [GROUP_LINK_1, GROUP_LINK_2],
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
        links = list(doc.get("group_links") or [GROUP_LINK_1, GROUP_LINK_2])
        while len(links) < 2:
            links.append(GROUP_LINK_2 if len(links) == 1 else GROUP_LINK_1)
        return {
            "sudos": list(dict.fromkeys(int(x) for x in doc.get("sudos", []) if str(x).isdigit())),
            "blocked": list(dict.fromkeys(int(x) for x in doc.get("blocked", []) if str(x).isdigit())),
            "dp_url": str(doc.get("dp_url") or ""),
            "secret_mode": bool(doc.get("secret_mode", False)),
            "group_links": [str(links[0]), str(links[1])],
        }
    data = _load_local()
    links = list(data.get("group_links") or [GROUP_LINK_1, GROUP_LINK_2])
    while len(links) < 2:
        links.append(GROUP_LINK_2 if len(links) == 1 else GROUP_LINK_1)
    return {
        "sudos": list(dict.fromkeys(int(x) for x in data.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in data.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(data.get("dp_url") or ""),
        "secret_mode": bool(data.get("secret_mode", False)),
        "group_links": [str(links[0]), str(links[1])],
    }


def save_meta_state(meta: dict):
    links = list(meta.get("group_links") or [GROUP_LINK_1, GROUP_LINK_2])
    while len(links) < 2:
        links.append(GROUP_LINK_2 if len(links) == 1 else GROUP_LINK_1)
    clean = {
        "sudos": list(dict.fromkeys(int(x) for x in meta.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in meta.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(meta.get("dp_url") or ""),
        "secret_mode": bool(meta.get("secret_mode", False)),
        "group_links": [str(links[0]), str(links[1])],
    }
    db = _get_db()
    if db is not None:
        db["meta"].update_one({"_id": "config"}, {"$set": clean}, upsert=True)
        return
    data = _load_local()
    data.update(clean)
    _save_local(data)


def set_group_links(link_1: str, link_2: str):
    global GROUP_LINK_1, GROUP_LINK_2
    GROUP_LINK_1 = link_1.strip()
    GROUP_LINK_2 = link_2.strip()
    meta = get_meta_state()
    meta["group_links"] = [GROUP_LINK_1, GROUP_LINK_2]
    save_meta_state(meta)


def get_active_group_links() -> tuple[str, str]:
    meta = get_meta_state()
    return meta["group_links"][0], meta["group_links"][1]


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


async def send_first_dm_card(event):
    link_1, link_2 = get_active_group_links()
    safe_l1 = _escape_html(link_1)
    safe_l2 = _escape_html(link_2)

    msg = (
        f"<blockquote><b>{FIRST_DM_HEADER}</b>\n\n"
        f'• <a href="{safe_l1}"><b>{BTN_1_TEXT}</b></a>\n'
        f'• <a href="{safe_l2}"><b>{BTN_2_TEXT}</b></a></blockquote>'
    )
    await event.reply(msg, parse_mode="html", link_preview=False)


def pick_random_message(host_state: dict, target_id: int) -> str:
    valid_msgs = [m.strip() for m in RANDOM_MESSAGES if isinstance(m, str) and m.strip()]
    if not valid_msgs:
        return "<blockquote><b>𝗛𝗲𝗹𝗹𝗼! 👋</b></blockquote>"
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
    tagging_chats: set,
    tag_text: str = "Hii",
    status_event=None,
):
    if chat_id in tagging_chats:
        return
    tagging_chats.add(chat_id)

    clean_tag_text = (tag_text or "Hii").strip() or "Hii"
    tagged_count = 0
    total_count = 0
    stopped_early = False

    try:
        targets = await _collect_group_targets(client, chat_id)
        total_count = len(targets)

        if not targets:
            await client.send_message(
                chat_id,
                "<blockquote>⚠️ <b>𝗜𝘀 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲𝗶𝗻 𝘁𝗮𝗴 𝗸𝗮𝗿𝗻𝗲 𝗸𝗲 𝗹𝗶𝘆𝗲 𝗸𝗼𝗶 𝗺𝗲𝗺𝗯𝗲𝗿 𝗻𝗮𝗵𝗶 𝗺𝗶𝗹𝗮.</b></blockquote>",
                parse_mode="html",
            )
            return

        start_text = (
            f"<blockquote>🚀✨ <b>𝗧𝗮𝗴𝗮𝗹𝗹 𝗦𝘁𝗮𝗿𝘁𝗲𝗱!</b>\n"
            f"💬 <b>𝗠𝗲𝘀𝘀𝗮𝗴𝗲:</b> <b>{clean_tag_text}</b>\n"
            f"👥 <b>𝗧𝗼𝘁𝗮𝗹 𝗠𝗲𝗺𝗯𝗲𝗿𝘀:</b> <code>{total_count}</code></blockquote>"
        )
        if status_event is not None:
            try:
                await status_event.edit(start_text, parse_mode="html")
            except Exception:
                await client.send_message(chat_id, start_text, parse_mode="html")
        else:
            await client.send_message(chat_id, start_text, parse_mode="html")

        for uid, uname in targets:
            if chat_id not in tagging_chats:
                stopped_early = True
                break
            await client.send_message(
                chat_id,
                f'<blockquote>✨ <b><a href="tg://user?id={uid}">{uname}</a></b> — <b>{clean_tag_text}</b></blockquote>',
                parse_mode="html",
            )
            tagged_count += 1
            await asyncio.sleep(TAG_DELAY_SECONDS)

        status_title = "🛑✨ <b>𝗧𝗮𝗴𝗮𝗹𝗹 𝗦𝘁𝗼𝗽𝗽𝗲𝗱!</b>" if stopped_early else "✅🎉 <b>𝗧𝗮𝗴𝗮𝗹𝗹 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱!</b>"
        await client.send_message(
            chat_id,
            f"<blockquote>{status_title}\n📊 <b>𝗧𝗮𝗴𝗴𝗲𝗱 𝗠𝗲𝗺𝗯𝗲𝗿𝘀:</b> <code>{tagged_count}</code> / <code>{total_count}</code></blockquote>",
            parse_mode="html",
        )
    finally:
        tagging_chats.discard(chat_id)


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
    mention = f'<b><a href="tg://user?id={uid}">{uname}</a></b>' if uid else f"<b>{uname}</b>"
    await client.send_message(
        chat_id,
        f"<blockquote>{QUIT_MESSAGE}\n👤 {mention}</blockquote>",
        parse_mode="html",
    )


async def _attach_handlers(client: TelegramClient, host_state: dict):
    raid_users = host_state["raid_users"]
    tagging_chats = host_state["tagging"]
    welcomed_users = host_state["welcomed_users"]
    me = await client.get_me()
    my_id = me.id if me else 0

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_cmd(event):
        await event.edit("<blockquote>🏓 <b>𝗣𝗼𝗻𝗴! 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗶𝘀 𝗮𝗰𝘁𝗶𝘃𝗲.</b></blockquote>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.setlinks\s+(\S+)\s+(\S+)$"))
    async def setlinks_cmd(event):
        l1 = event.pattern_match.group(1)
        l2 = event.pattern_match.group(2)
        set_group_links(l1, l2)
        await event.edit(
            f"<blockquote>✅🔗 <b>𝗚𝗿𝗼𝘂𝗽 𝗹𝗶𝗻𝗸𝘀 𝘂𝗽𝗱𝗮𝘁𝗲 𝗵𝗼 𝗴𝗮𝘆𝗲!</b>\n"
            f"1️⃣ <b>{BTN_1_TEXT}</b>\n"
            f"2️⃣ <b>{BTN_2_TEXT}</b></blockquote>",
            parse_mode="html",
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tagall(?:\s+([\s\S]+))?$"))
    async def tagall_cmd(event):
        if not event.is_group:
            await event.edit("<blockquote>⚠️ <b>𝗬𝗲𝗵 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝘀𝗶𝗿𝗳 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲𝗶𝗻 𝗰𝗵𝗮𝗹𝗲𝗴𝗮.</b></blockquote>", parse_mode="html")
            return
        if event.chat_id in tagging_chats:
            await event.edit("<blockquote>⏳ <b>𝗜𝘀 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲𝗶𝗻 𝘁𝗮𝗴𝗮𝗹𝗹 𝗽𝗲𝗵𝗹𝗲 𝘀𝗲 𝗰𝗵𝗮𝗹 𝗿𝗮𝗵𝗮 𝗵𝗮𝗶.</b></blockquote>", parse_mode="html")
            return
        tag_text = _extract_tag_text(event.raw_text or "")
        await _run_tagall_in_chat(
            client,
            event.chat_id,
            tagging_chats,
            tag_text=tag_text,
            status_event=event,
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stoptagall$"))
    async def stoptagall_cmd(event):
        if event.chat_id in tagging_chats:
            tagging_chats.discard(event.chat_id)
            await event.edit("<blockquote>🛑✨ <b>𝗧𝗮𝗴𝗮𝗹𝗹 𝗿𝗼𝗸 𝗱𝗶𝘆𝗮 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶!</b></blockquote>", parse_mode="html")
        else:
            await event.edit("<blockquote>ℹ️ <b>𝗜𝘀 𝗴𝗿𝗼𝘂𝗽 𝗺𝗲𝗶𝗻 𝗸𝗼𝗶 𝗮𝗰𝘁𝗶𝘃𝗲 𝘁𝗮𝗴𝗮𝗹𝗹 𝗻𝗮𝗵𝗶 𝗰𝗵𝗮𝗹 𝗿𝗮𝗵𝗮.</b></blockquote>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopquit$"))
    async def stopquit_cmd(event):
        host_state["quit_enabled"] = False
        await event.edit("<blockquote>🛑🚪 <b>𝗨𝘀𝗲𝗿 𝗾𝘂𝗶𝘁 𝗮𝗹𝗲𝗿𝘁 𝗢𝗙𝗙 𝗸𝗮𝗿 𝗱𝗶𝘆𝗮 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶.</b></blockquote>", parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.startquit$"))
    async def startquit_cmd(event):
        host_state["quit_enabled"] = True
        await event.edit("<blockquote>✅🚪 <b>𝗨𝘀𝗲𝗿 𝗾𝘂𝗶𝘁 𝗮𝗹𝗲𝗿𝘁 𝗢𝗡 𝗸𝗮𝗿 𝗱𝗶𝘆𝗮 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶.</b></blockquote>", parse_mode="html")

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
            f"<blockquote>🎯🔥 <b>𝗔𝘂𝘁𝗼-𝗥𝗲𝗽𝗹𝘆 / 𝗥𝗮𝗶𝗱 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 (𝗗𝗠 + 𝗚𝗿𝗼𝘂𝗽)!</b>\n👤 <b>𝗧𝗮𝗿𝗴𝗲𝘁:</b> <code>{target_id}</code></blockquote>",
            parse_mode="html",
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
            f"<blockquote>🎯🛑 <b>𝗔𝘂𝘁𝗼-𝗥𝗲𝗽𝗹𝘆 / 𝗥𝗮𝗶𝗱 𝗗𝗘𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 (𝗗𝗠 + 𝗚𝗿𝗼𝘂𝗽) 𝗳𝗼𝗿</b> <code>{target_id}</code>!</blockquote>",
            parse_mode="html",
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
                await client.send_message(event.chat_id, f"<blockquote>{QUIT_MESSAGE}</blockquote>", parse_mode="html")

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
            txt = (event.raw_text or "").strip().lower()
            if txt == "stop tagall":
                tagging_chats.discard(event.chat_id)
                return

            if re.match(r"^[.]?tagall(?:\s+.*)?$", (event.raw_text or "").strip(), flags=re.IGNORECASE):
                tag_text = _extract_tag_text(event.raw_text or "")
                await _run_tagall_in_chat(client, event.chat_id, tagging_chats, tag_text=tag_text)
                return

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
            return False, "<b>𝗦𝗲𝘀𝘀𝗶𝗼𝗻 𝘃𝗮𝗹𝗶𝗱 𝘆𝗮 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗻𝗮𝗵𝗶 𝗵𝗮𝗶.</b>"

        meta = get_meta_state()
        set_group_links(meta["group_links"][0], meta["group_links"][1])

        host_state = {
            "client": client,
            "session": cleaned,
            "raid_users": set(),
            "tagging": set(),
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
            return True, "✅ <b>𝗦𝘂𝗰𝗰𝗲𝘀𝘀 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗥𝗲𝘀𝘁𝗮𝗿𝘁𝗲𝗱! 𝗨𝘀𝗲 <code>.ping</code>.</b>"
        return True, "✅ <b>𝗦𝘂𝗰𝗰𝗲𝘀𝘀 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗛𝗼𝘀𝘁𝗲𝗱! 𝗨𝘀𝗲 <code>.ping</code> 𝘁𝗼 𝗰𝗵𝗲𝗰𝗸.</b>"
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"❌ <b>𝗛𝗼𝘀𝘁 𝗸𝗮𝗿𝗻𝗲 𝗺𝗲𝗶𝗻 𝗲𝗿𝗿𝗼𝗿 𝗮𝗮𝘆𝗮:</b> <code>{e}</code>"


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
        return True, "🔑 <b>𝗘𝗻𝘁𝗲𝗿 𝗢𝗧𝗣 (𝗲.𝗴., 1 2 3 4 5): 𝗛𝘂𝗿𝗿𝘆, 𝗲𝘅𝗽𝗶𝗿𝗲𝘀 𝗶𝗻 1-2 𝗺𝗶𝗻!</b>"
    except PhoneNumberInvalidError:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, "❌ <b>𝗣𝗵𝗼𝗻𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝗶𝗻𝘃𝗮𝗹𝗶𝗱 𝗵𝗮𝗶. 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 𝗰𝗼𝗱𝗲 𝗸𝗲 𝘀𝗮𝗮𝘁𝗵 𝘀𝗮𝗵𝗶 𝗻𝘂𝗺𝗯𝗲𝗿 𝗱𝗮𝗮𝗹𝗲𝗶𝗻 (𝗷𝗮𝗶𝘀𝗲 +919876543210).</b>"
    except FloodWaitError as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"⏳ <b>𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗿𝗮𝘁𝗲 𝗹𝗶𝗺𝗶𝘁 𝗹𝗮𝗴𝗮 𝗵𝗮𝗶.</b> <code>{e.seconds}</code> <b>𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗯𝗮𝗮𝗱 𝘁𝗿𝘆 𝗸𝗮𝗿𝗲𝗶𝗻.</b>"
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"❌ <b>𝗢𝗧𝗣 𝗯𝗵𝗲𝗷𝗻𝗲 𝗺𝗲𝗶𝗻 𝗲𝗿𝗿𝗼𝗿 𝗮𝗮𝘆𝗮:</b> <code>{e}</code>"


async def submit_otp_code(user_id: int, otp_text: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "otp":
        return "error", "❌ <b>𝗞𝗼𝗶 𝗮𝗰𝘁𝗶𝘃𝗲 𝗢𝗧𝗣 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝗻𝗮𝗵𝗶 𝗺𝗶𝗹𝗮. 𝗣𝗲𝗵𝗹𝗲 <code>/host</code> 𝗹𝗶𝗸𝗵𝗲𝗶𝗻.</b>"

    code = "".join(ch for ch in otp_text if ch.isdigit())
    if not code:
        return "retry", "⚠️ <b>𝗩𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗲𝗿𝗶𝗰 𝗢𝗧𝗣 𝗯𝗵𝗲𝗷𝗲𝗶𝗻.</b>"

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
        return "2fa", "🔒 <b>𝗘𝗻𝘁𝗲𝗿 2𝗙𝗔 𝗣𝗮𝘀𝘀𝘄𝗼𝗿𝗱:</b>"
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        PENDING_LOGINS.pop(user_id, None)
        return "error", f"❌ <b>𝗟𝗼𝗴𝗶𝗻 𝗳𝗮𝗶𝗹 𝗵𝗼 𝗴𝗮𝘆𝗮:</b> <code>{e}</code>"


async def submit_2fa_password(user_id: int, password: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "2fa":
        return "error", "❌ <b>𝗞𝗼𝗶 𝗮𝗰𝘁𝗶𝘃𝗲 2𝗙𝗔 𝘀𝘁𝗲𝗽 𝗻𝗮𝗵𝗶 𝗺𝗶𝗹𝗮. 𝗣𝗲𝗵𝗹𝗲 <code>/host</code> 𝗹𝗶𝗸𝗵𝗲𝗶𝗻.</b>"

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
        return "error", f"❌ <b>2𝗙𝗔 𝗹𝗼𝗴𝗶𝗻 𝗳𝗮𝗶𝗹 𝗵𝗼 𝗴𝗮𝘆𝗮:</b> <code>{e}</code>"


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

    return False, "ℹ️ <b>𝗔𝗮𝗽𝗸𝗮 𝗸𝗼𝗶 𝗵𝗼𝘀𝘁𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁 𝗻𝗮𝗵𝗶 𝗺𝗶𝗹𝗮. 𝗣𝗲𝗵𝗹𝗲 <code>/host</code> 𝗹𝗶𝗸𝗵𝗲𝗶𝗻.</b>"


async def logout_user_account(user_id: int) -> tuple[bool, str]:
    await cancel_pending_login(user_id)
    info = ACTIVE_HOSTS.pop(user_id, None)
    delete_session(user_id)

    if not info:
        return False, "ℹ️ <b>𝗟𝗼𝗴𝗼𝘂𝘁 𝗸𝗮𝗿𝗻𝗲 𝗸𝗲 𝗹𝗶𝘆𝗲 𝗸𝗼𝗶 𝗮𝗰𝘁𝗶𝘃𝗲 𝗵𝗼𝘀𝘁𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁 𝗻𝗮𝗵𝗶 𝗺𝗶𝗹𝗮.</b>"

    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "🚪✅ <b>𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗹𝗼𝗴𝗼𝘂𝘁 𝗮𝘂𝗿 𝗱𝗶𝘀𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗵𝗼 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶.</b>"


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_sessions()
    for uid, session_str in saved.items():
        await start_client_from_session(uid, session_str, api_id, api_hash, persist=False)


# ================= MAIN BOT CLIENT =================
API_ID = int(os.getenv("API_ID", "0").strip() or "0")
API_HASH = os.getenv("API_HASH", "").strip()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0").strip() or "0")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("API_ID, API_HASH, aur BOT_TOKEN environment variables set hona zaroori hai.")

bot = TelegramClient(
    StringSession(),
    API_ID,
    API_HASH,
    device_model="Desktop",
    system_version="Windows 11",
    app_version="5.6.3 x64",
)


def _is_admin(user_id: int) -> bool:
    return bool(OWNER_ID and int(user_id) == int(OWNER_ID))


def _help_text(is_owner: bool) -> str:
    base = (
        "<blockquote><b>🤖✨ 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗛𝗢𝗦𝗧𝗘𝗥 𝗕𝗢𝗧</b>\n\n"
        "• <code>/host</code> — <b>𝗔𝗽𝗻𝗮 𝗮𝗰𝗰𝗼𝘂𝗻𝘁 𝗵𝗼𝘀𝘁 𝗸𝗮𝗿𝗲𝗶𝗻 (𝗣𝗵𝗼𝗻𝗲 + 𝗢𝗧𝗣 + 2𝗙𝗔)</b>\n"
        "• <code>/restart</code> — <b>𝗛𝗼𝘀𝘁𝗲𝗱 𝘂𝘀𝗲𝗿𝗯𝗼𝘁 𝗿𝗲𝘀𝘁𝗮𝗿𝘁 𝗸𝗮𝗿𝗲𝗶𝗻</b>\n"
        "• <code>/logout</code> — <b>𝗦𝗲𝘀𝘀𝗶𝗼𝗻 𝗹𝗼𝗴𝗼𝘂𝘁 / 𝗿𝗲𝗺𝗼𝘃𝗲 𝗸𝗮𝗿𝗲𝗶𝗻</b>\n"
        "• <code>/cancel</code> — <b>𝗖𝗵𝗮𝗹𝘁𝗮 𝗵𝘂𝗮 𝗹𝗼𝗴𝗶𝗻 𝗰𝗮𝗻𝗰𝗲𝗹 𝗸𝗮𝗿𝗲𝗶𝗻</b></blockquote>"
    )
    if is_owner:
        base += (
            "\n<blockquote><b>👑 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:</b>\n"
            "• <code>/setlinks &lt;link1&gt; &lt;link2&gt;</code> — <b>𝗗𝗼𝗻𝗼 𝗴𝗿𝗼𝘂𝗽 𝗹𝗶𝗻𝗸𝘀 𝗯𝗮𝗱𝗹𝗲𝗶𝗻</b>\n"
            "• <code>/stats</code> — <b>𝗔𝗰𝘁𝗶𝘃𝗲 𝗵𝗼𝘀𝘁𝘀 𝗰𝗼𝘂𝗻𝘁 𝗱𝗲𝗸𝗵𝗲𝗶𝗻</b></blockquote>"
        )
    return base


@bot.on(events.NewMessage(incoming=True, pattern=r"^/start(?:\s+.*)?$"))
async def start_handler(event):
    if not event.is_private:
        return
    sender_id = event.sender_id
    if not sender_id:
        return
    await event.reply(_help_text(_is_admin(sender_id)), parse_mode="html", link_preview=False)
    await send_first_dm_card(event)


@bot.on(events.NewMessage(incoming=True, pattern=r"^/help$"))
async def help_handler(event):
    if not event.is_private:
        return
    await event.reply(_help_text(_is_admin(event.sender_id or 0)), parse_mode="html", link_preview=False)


@bot.on(events.NewMessage(incoming=True, pattern=r"^/cancel$"))
async def cancel_handler(event):
    if not event.is_private:
        return
    uid = event.sender_id
    if not uid:
        return
    LOGIN_FLOW.pop(uid, None)
    await cancel_pending_login(uid)
    await event.reply("<blockquote>🛑 <b>𝗟𝗼𝗴𝗶𝗻 / 𝗵𝗼𝘀𝘁𝗶𝗻𝗴 𝗽𝗿𝗼𝗰𝗲𝘀𝘀 𝗰𝗮𝗻𝗰𝗲𝗹 𝗸𝗮𝗿 𝗱𝗶𝘆𝗮 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶.</b></blockquote>", parse_mode="html")


@bot.on(events.NewMessage(incoming=True, pattern=r"^/host$"))
async def host_handler(event):
    if not event.is_private:
        return
    uid = event.sender_id
    if not uid:
        return

    LOGIN_FLOW[uid] = {"step": "phone"}
    await event.reply(
        "<blockquote>📱✨ <b>𝗔𝗽𝗻𝗮 𝗣𝗵𝗼𝗻𝗲 𝗡𝘂𝗺𝗯𝗲𝗿 𝗯𝗵𝗲𝗷𝗲𝗶𝗻 (𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗰𝗼𝗱𝗲 𝗸𝗲 𝘀𝗮𝗮𝘁𝗵, 𝗷𝗮𝗶𝘀𝗲 <code>+919876543210</code>):</b></blockquote>",
        parse_mode="html",
    )


@bot.on(events.NewMessage(incoming=True, pattern=r"^/restart$"))
async def restart_handler(event):
    if not event.is_private:
        return
    uid = event.sender_id
    if not uid:
        return

    ok, msg = await restart_user_account(uid, API_ID, API_HASH)
    await event.reply(f"<blockquote>{msg}</blockquote>", parse_mode="html")


@bot.on(events.NewMessage(incoming=True, pattern=r"^/logout$"))
async def logout_handler(event):
    if not event.is_private:
        return
    uid = event.sender_id
    if not uid:
        return

    LOGIN_FLOW.pop(uid, None)
    _, msg = await logout_user_account(uid)
    await event.reply(f"<blockquote>{msg}</blockquote>", parse_mode="html")


@bot.on(events.NewMessage(incoming=True, pattern=r"^/setlinks\s+(\S+)\s+(\S+)$"))
async def setlinks_handler(event):
    if not event.is_private:
        return
    if not _is_admin(event.sender_id or 0):
        await event.reply("<blockquote>⚠️ <b>𝗬𝗲𝗵 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝘀𝗶𝗿𝗳 𝗢𝘄𝗻𝗲𝗿 𝗸𝗲 𝗹𝗶𝘆𝗲 𝗵𝗮𝗶.</b></blockquote>", parse_mode="html")
        return

    l1 = event.pattern_match.group(1)
    l2 = event.pattern_match.group(2)
    set_group_links(l1, l2)
    await event.reply(
        f"<blockquote>✅🔗 <b>𝗚𝗿𝗼𝘂𝗽 𝗹𝗶𝗻𝗸𝘀 𝘂𝗽𝗱𝗮𝘁𝗲 𝗵𝗼 𝗴𝗮𝘆𝗲!</b>\n"
        f"1️⃣ <b>{BTN_1_TEXT}</b>\n"
        f"2️⃣ <b>{BTN_2_TEXT}</b></blockquote>",
        parse_mode="html",
        link_preview=False,
    )


@bot.on(events.NewMessage(incoming=True, pattern=r"^/stats$"))
async def stats_handler(event):
    if not event.is_private or not _is_admin(event.sender_id or 0):
        return
    active_cnt = len(ACTIVE_HOSTS)
    pending_cnt = len(PENDING_LOGINS)
    l1, l2 = get_active_group_links()
    await event.reply(
        f"<blockquote>📊✨ <b>𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦</b>\n"
        f"🟢 <b>𝗔𝗰𝘁𝗶𝘃𝗲 𝗛𝗼𝘀𝘁𝘀:</b> <code>{active_cnt}</code>\n"
        f"⏳ <b>𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗟𝗼𝗴𝗶𝗻𝘀:</b> <code>{pending_cnt}</code>\n"
        f"🔗 <b>𝗟𝗶𝗻𝗸 𝟭:</b> <code>{l1}</code>\n"
        f"🔗 <b>𝗟𝗶𝗻𝗸 𝟮:</b> <code>{l2}</code></blockquote>",
        parse_mode="html",
        link_preview=False,
    )


@bot.on(events.NewMessage(incoming=True))
async def private_flow_handler(event):
    if not event.is_private:
        return
    uid = event.sender_id
    if not uid:
        return

    text = (event.raw_text or "").strip()
    if not text or text.startswith("/"):
        return

    flow = LOGIN_FLOW.get(uid)
    if not flow:
        return

    step = flow.get("step")

    if step == "phone":
        ok, reply_msg = await send_login_code(uid, text, API_ID, API_HASH)
        await event.reply(f"<blockquote>{reply_msg}</blockquote>", parse_mode="html")
        if ok:
            flow["step"] = "otp"
        else:
            LOGIN_FLOW.pop(uid, None)
        return

    if step == "otp":
        status, reply_msg = await submit_otp_code(uid, text, API_ID, API_HASH)
        await event.reply(f"<blockquote>{reply_msg}</blockquote>", parse_mode="html")
        if status == "2fa":
            flow["step"] = "2fa"
        elif status in {"done", "error"}:
            LOGIN_FLOW.pop(uid, None)
        return

    if step == "2fa":
        status, reply_msg = await submit_2fa_password(uid, text, API_ID, API_HASH)
        await event.reply(f"<blockquote>{reply_msg}</blockquote>", parse_mode="html")
        if status in {"done", "error"}:
            LOGIN_FLOW.pop(uid, None)
        return


async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await restore_all_saved_sessions(API_ID, API_HASH)
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
