import asyncio
import json
import os
import random
from pathlib import Path
from pymongo import MongoClient
from telethon import TelegramClient, events
from telethon.sessions import StringSession

STORE_FILE = Path("sessions_store.json")

RANDOM_MESSAGES = [
    "Kya chal raha hai? 😄",
    "Phir se DM kar diya? 👀",
    "Aaj bada yaad aa rahi hai kya?",
    "Bot bol raha hoon, boss abhi busy hain!",
    "Ek aur message aaya, ek aur random reply!",
    "Kya baat hai, ruk hi nahi rahe ho?",
    "Online toh dikh rahe ho, baat kya karni hai?",
    "Auto reply mode full on hai! ⚡",
    "Bolo bolo, sun raha hoon.",
    "Naya message = naya random reply!",
]

# user_id (int) -> {"client": TelegramClient, "session": str, "raid_users": set(), "tagging": set(), "last_msg": {}}
ACTIVE_HOSTS = {}

_mongo_collection = None


def _get_collection():
    global _mongo_collection
    if _mongo_collection is not None:
        return _mongo_collection
    mongo_uri = os.getenv("MONGO_URI", "").strip()
    if not mongo_uri:
        return None
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client["userbot_hoster_db"]
    _mongo_collection = db["hosted_sessions"]
    return _mongo_collection


def _save_session_record(user_id: int, string_session: str):
    col = _get_collection()
    if col is not None:
        col.update_one(
            {"_id": str(user_id)},
            {"$set": {"user_id": int(user_id), "session": string_session}},
            upsert=True,
        )
        return

    data = {}
    if STORE_FILE.exists():
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data[str(user_id)] = string_session
    STORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _delete_session_record(user_id: int):
    col = _get_collection()
    if col is not None:
        col.delete_one({"_id": str(user_id)})
        return

    if STORE_FILE.exists():
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            data.pop(str(user_id), None)
            STORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass


def load_all_saved_sessions() -> dict[int, str]:
    col = _get_collection()
    if col is not None:
        result = {}
        for doc in col.find({}):
            uid_raw = doc.get("user_id") or doc.get("_id")
            sess = doc.get("session")
            if uid_raw and sess and str(uid_raw).isdigit():
                result[int(uid_raw)] = sess
        return result

    if STORE_FILE.exists():
        try:
            raw = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            return {int(k): v for k, v in raw.items() if str(k).isdigit() and v}
        except Exception:
            return {}
    return {}


def pick_random_message(host_state: dict, target_id: int) -> str:
    if not RANDOM_MESSAGES:
        return "Hello!"
    if len(RANDOM_MESSAGES) == 1:
        return RANDOM_MESSAGES[0]
    last_msg = host_state["last_msg"].get(target_id)
    pool = [m for m in RANDOM_MESSAGES if m != last_msg]
    chosen = random.choice(pool or RANDOM_MESSAGES)
    host_state["last_msg"][target_id] = chosen
    return chosen


async def _attach_handlers(client: TelegramClient, host_state: dict):
    raid_users = host_state["raid_users"]
    tagging_chats = host_state["tagging"]

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tagall$"))
    async def tagall_cmd(event):
        if not event.is_group:
            await event.edit("Yeh command sirf group mein kaam karega.")
            return

        chat_id = event.chat_id
        if chat_id in tagging_chats:
            await event.edit("Is group mein tagall pehle se chal raha hai.")
            return

        tagging_chats.add(chat_id)
        try:
            await event.delete()
        except Exception:
            pass

        mentions = []
        async for member in client.iter_participants(chat_id):
            if chat_id not in tagging_chats:
                break
            if member.bot or member.deleted:
                continue

            safe_name = (member.first_name or "User").replace("[", "").replace("]", "")
            mentions.append(f"[{safe_name}](tg://user?id={member.id})")

            if len(mentions) == 5:
                await client.send_message(chat_id, " ".join(mentions))
                mentions = []
                await asyncio.sleep(1.5)

        if mentions and chat_id in tagging_chats:
            await client.send_message(chat_id, " ".join(mentions))

        tagging_chats.discard(chat_id)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stoptagall$"))
    async def stoptagall_cmd(event):
        if event.chat_id in tagging_chats:
            tagging_chats.discard(event.chat_id)
            await event.edit("Tagall rok diya gaya hai.")
        else:
            await event.edit("Is group mein koi active tagall nahi chal raha.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.replyraid\s+(\d+)$"))
    async def replyraid_add_cmd(event):
        target_id = int(event.pattern_match.group(1))
        raid_users.add(target_id)
        await event.edit(f"DM Replyraid ON: `{target_id}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.dreplyraid\s+(\d+)$"))
    async def replyraid_del_cmd(event):
        target_id = int(event.pattern_match.group(1))
        raid_users.discard(target_id)
        await event.edit(f"DM Replyraid OFF: `{target_id}`")

    @client.on(events.NewMessage(incoming=True))
    async def dm_auto_reply_handler(event):
        if not event.is_private:
            return
        if event.sender_id in raid_users:
            reply_text = pick_random_message(host_state, event.sender_id)
            await asyncio.sleep(0.8)
            await event.reply(reply_text)


async def host_user_account(
    user_id: int, string_session: str, api_id: int, api_hash: str, persist: bool = True
) -> tuple[bool, str]:
    existing = ACTIVE_HOSTS.pop(user_id, None)
    if existing:
        try:
            await existing["client"].disconnect()
        except Exception:
            pass

    cleaned_session = string_session.strip()
    client = TelegramClient(StringSession(cleaned_session), api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return False, "Session valid ya authorized nahi hai. Naya StringSession dein."

        host_state = {
            "client": client,
            "session": cleaned_session,
            "raid_users": set(),
            "tagging": set(),
            "last_msg": {},
        }
        ACTIVE_HOSTS[user_id] = host_state
        await _attach_handlers(client, host_state)
        asyncio.create_task(client.run_until_disconnected())

        if persist:
            _save_session_record(user_id, cleaned_session)

        return True, "Account host ho gaya hai! Ab `.tagall`, `.stoptagall`, `.replyraid <id>`, `.dreplyraid <id>` chalayein."
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"Host karne mein error aaya: {e}"


async def restart_user_account(user_id: int, api_id: int, api_hash: str) -> tuple[bool, str]:
    info = ACTIVE_HOSTS.get(user_id)
    if info:
        return await host_user_account(user_id, info["session"], api_id, api_hash, persist=True)

    saved = load_all_saved_sessions()
    if user_id in saved:
        return await host_user_account(user_id, saved[user_id], api_id, api_hash, persist=True)

    return False, "Aapka koi hosted account nahi mila. Pehle `/host <string_session>` karein."


async def logout_user_account(user_id: int) -> tuple[bool, str]:
    info = ACTIVE_HOSTS.pop(user_id, None)
    _delete_session_record(user_id)

    if not info:
        return False, "Logout karne ke liye koi active hosted account nahi mila."

    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "Account logout aur disconnect ho gaya hai."


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_saved_sessions()
    for uid, session_str in saved.items():
        await host_user_account(uid, session_str, api_id, api_hash, persist=False)
