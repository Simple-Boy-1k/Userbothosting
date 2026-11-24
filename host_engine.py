import asyncio
import json
import os
import random
from pathlib import Path
from pymongo import MongoClient
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

STORE_FILE = Path("hoster_data.json")

FIRST_DM_WELCOME = "Hey welcome to my dm! How are you...? 😊"

# Yahan apni marzi ke 50 random messages likhein (har line mein apna text daal sakte hain)
RANDOM_MESSAGES = [
    "Message 01 yahan likhein",   # 01
    "Message 02 yahan likhein",   # 02
    "Message 03 yahan likhein",   # 03
    "Message 04 yahan likhein",   # 04
    "Message 05 yahan likhein",   # 05
    "Message 06 yahan likhein",   # 06
    "Message 07 yahan likhein",   # 07
    "Message 08 yahan likhein",   # 08
    "Message 09 yahan likhein",   # 09
    "Message 10 yahan likhein",   # 10
    "Message 11 yahan likhein",   # 11
    "Message 12 yahan likhein",   # 12
    "Message 13 yahan likhein",   # 13
    "Message 14 yahan likhein",   # 14
    "Message 15 yahan likhein",   # 15
    "Message 16 yahan likhein",   # 16
    "Message 17 yahan likhein",   # 17
    "Message 18 yahan likhein",   # 18
    "Message 19 yahan likhein",   # 19
    "Message 20 yahan likhein",   # 20
    "Message 21 yahan likhein",   # 21
    "Message 22 yahan likhein",   # 22
    "Message 23 yahan likhein",   # 23
    "Message 24 yahan likhein",   # 24
    "Message 25 yahan likhein",   # 25
    "Message 26 yahan likhein",   # 26
    "Message 27 yahan likhein",   # 27
    "Message 28 yahan likhein",   # 28
    "Message 29 yahan likhein",   # 29
    "Message 30 yahan likhein",   # 30
    "Message 31 yahan likhein",   # 31
    "Message 32 yahan likhein",   # 32
    "Message 33 yahan likhein",   # 33
    "Message 34 yahan likhein",   # 34
    "Message 35 yahan likhein",   # 35
    "Message 36 yahan likhein",   # 36
    "Message 37 yahan likhein",   # 37
    "Message 38 yahan likhein",   # 38
    "Message 39 yahan likhein",   # 39
    "Message 40 yahan likhein",   # 40
    "Message 41 yahan likhein",   # 41
    "Message 42 yahan likhein",   # 42
    "Message 43 yahan likhein",   # 43
    "Message 44 yahan likhein",   # 44
    "Message 45 yahan likhein",   # 45
    "Message 46 yahan likhein",   # 46
    "Message 47 yahan likhein",   # 47
    "Message 48 yahan likhein",   # 48
    "Message 49 yahan likhein",   # 49
    "Message 50 yahan likhein",   # 50
]

# user_id (int) -> {
#   "client": TelegramClient,
#   "session": str,
#   "raid_users": set(),
#   "tagging": set(),
#   "welcomed_users": set(),
#   "last_msg": {},
# }
ACTIVE_HOSTS = {}

# user_id (int) -> {"step": "phone"|"otp"|"2fa", "phone": str, "phone_code_hash": str, "client": TelegramClient}
PENDING_LOGINS = {}

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
        }
    data = _load_local()
    return {
        "sudos": list(dict.fromkeys(int(x) for x in data.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in data.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(data.get("dp_url") or ""),
        "secret_mode": bool(data.get("secret_mode", False)),
    }


def save_meta_state(meta: dict):
    clean = {
        "sudos": list(dict.fromkeys(int(x) for x in meta.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in meta.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(meta.get("dp_url") or ""),
        "secret_mode": bool(meta.get("secret_mode", False)),
    }
    db = _get_db()
    if db is not None:
        db["meta"].update_one({"_id": "config"}, {"$set": clean}, upsert=True)
        return
    data = _load_local()
    data.update(clean)
    _save_local(data)


def pick_random_message(host_state: dict, target_id: int) -> str:
    valid_msgs = [m.strip() for m in RANDOM_MESSAGES if isinstance(m, str) and m.strip()]
    if not valid_msgs:
        return "Hello!"
    if len(valid_msgs) == 1:
        return valid_msgs[0]
    last_msg = host_state["last_msg"].get(target_id)
    pool = [m for m in valid_msgs if m != last_msg]
    chosen = random.choice(pool or valid_msgs)
    host_state["last_msg"][target_id] = chosen
    return chosen


async def _attach_handlers(client: TelegramClient, host_state: dict):
    raid_users = host_state["raid_users"]
    tagging_chats = host_state["tagging"]
    welcomed_users = host_state["welcomed_users"]

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tagall$"))
    async def tagall_cmd(event):
        if not event.is_group:
            await event.edit("Yeh command sirf group mein chalega.")
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
    async def dm_auto_handler(event):
        if not event.is_private:
            return

        sender_id = event.sender_id
        if not sender_id:
            return

        # 1. Agar ID replyraid list mein hai toh har message par random reply bhejein
        if sender_id in raid_users:
            reply_text = pick_random_message(host_state, sender_id)
            await asyncio.sleep(0.8)
            await event.reply(reply_text)
            return

        # 2. Pehli baar DM aane par automatic welcome message bhejein
        if sender_id not in welcomed_users:
            welcomed_users.add(sender_id)
            await asyncio.sleep(0.5)
            await event.reply(FIRST_DM_WELCOME)


async def start_client_from_session(
    user_id: int, string_session: str, api_id: int, api_hash: str, persist: bool = True
) -> tuple[bool, str]:
    existing = ACTIVE_HOSTS.pop(user_id, None)
    if existing:
        try:
            await existing["client"].disconnect()
        except Exception:
            pass

    cleaned = string_session.strip()
    client = TelegramClient(StringSession(cleaned), api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return False, "Session valid ya authorized nahi hai."

        host_state = {
            "client": client,
            "session": cleaned,
            "raid_users": set(),
            "tagging": set(),
            "welcomed_users": set(),
            "last_msg": {},
        }
        ACTIVE_HOSTS[user_id] = host_state
        await _attach_handlers(client, host_state)
        asyncio.create_task(client.run_until_disconnected())

        if persist:
            save_session(user_id, cleaned)

        return True, "Account successfully host ho gaya hai! Ab `.tagall`, `.stoptagall`, `.replyraid <id>`, `.dreplyraid <id>` chalayein."
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

    cleaned_phone = phone.strip().replace(" ", "")
    client = TelegramClient(StringSession(), api_id, api_hash)
    try:
        await client.connect()
        sent = await client.send_code_request(cleaned_phone)
        PENDING_LOGINS[user_id] = {
            "step": "otp",
            "phone": cleaned_phone,
            "phone_code_hash": sent.phone_code_hash,
            "client": client,
        }
        return True, "OTP bhej diya gaya hai! Kripya apna **OTP** bhejein (jaise `1 2 3 4 5` ya `12345`):"
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"OTP bhejne mein error aaya: {e}"


async def submit_otp_code(user_id: int, otp_text: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "otp":
        return "error", "Koi active OTP request nahi mila. Pehle `/host` likhein."

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
        return "2fa", "Is account par **2FA Password** set hai. Kripya apna **2FA Password** bhejein:"
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
        return "error", "Koi active 2FA step nahi mila. Pehle `/host` likhein."

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
        return await start_client_from_session(user_id, info["session"], api_id, api_hash, persist=True)

    saved = load_all_sessions()
    if user_id in saved:
        return await start_client_from_session(user_id, saved[user_id], api_id, api_hash, persist=True)

    return False, "Aapka koi hosted account nahi mila. Pehle `/host` likhein."


async def logout_user_account(user_id: int) -> tuple[bool, str]:
    await cancel_pending_login(user_id)
    info = ACTIVE_HOSTS.pop(user_id, None)
    delete_session(user_id)

    if not info:
        return False, "Logout karne ke liye koi active hosted account nahi mila."

    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "Account logout aur disconnect ho gaya hai."


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_sessions()
    for uid, session_str in saved.items():
        await start_client_from_session(uid, session_str, api_id, api_hash, persist=False)
