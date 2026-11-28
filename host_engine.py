import asyncio
import json
import os
import time
from pathlib import Path
from pymongo import MongoClient
from telethon import TelegramClient
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.sessions import StringSession

from userbot_features import attach_userbot_handlers

STORE_FILE = Path("hoster_data.json")

ACTIVE_HOSTS: dict[int, dict] = {}
PENDING_LOGINS: dict[int, dict] = {}
LOGIN_FLOW: dict[int, str] = {}

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
        "custom_random_messages": [],
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


def parse_bulk_random_messages(raw_text: str) -> list[str]:
    if not raw_text:
        return []
    if "||" in raw_text and "\n" not in raw_text.strip():
        parts = raw_text.split("||")
    else:
        parts = raw_text.splitlines()
    out: list[str] = []
    for line in parts:
        cleaned = line.strip()
        if cleaned:
            out.append(cleaned)
    return out


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
        out: dict[int, str] = {}
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
        raw_msgs = doc.get("custom_random_messages", [])
        msgs = [str(m).strip() for m in raw_msgs if isinstance(m, str) and m.strip()] if isinstance(raw_msgs, list) else []
        return {
            "sudos": list(dict.fromkeys(int(x) for x in doc.get("sudos", []) if str(x).isdigit())),
            "blocked": list(dict.fromkeys(int(x) for x in doc.get("blocked", []) if str(x).isdigit())),
            "dp_url": str(doc.get("dp_url") or ""),
            "secret_mode": bool(doc.get("secret_mode", False)),
            "force_join_chat_id": doc.get("force_join_chat_id", 0),
            "force_join_link": str(doc.get("force_join_link") or ""),
            "support_group_url": str(doc.get("support_group_url") or ""),
            "custom_random_messages": msgs,
        }
    data = _load_local()
    raw_msgs = data.get("custom_random_messages", [])
    msgs = [str(m).strip() for m in raw_msgs if isinstance(m, str) and m.strip()] if isinstance(raw_msgs, list) else []
    return {
        "sudos": list(dict.fromkeys(int(x) for x in data.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in data.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(data.get("dp_url") or ""),
        "secret_mode": bool(data.get("secret_mode", False)),
        "force_join_chat_id": data.get("force_join_chat_id", 0),
        "force_join_link": str(data.get("force_join_link") or ""),
        "support_group_url": str(data.get("support_group_url") or ""),
        "custom_random_messages": msgs,
    }


def save_meta_state(meta: dict):
    raw_msgs = meta.get("custom_random_messages", [])
    msgs = [str(m).strip() for m in raw_msgs if isinstance(m, str) and m.strip()] if isinstance(raw_msgs, list) else []
    clean = {
        "sudos": list(dict.fromkeys(int(x) for x in meta.get("sudos", []) if str(x).isdigit())),
        "blocked": list(dict.fromkeys(int(x) for x in meta.get("blocked", []) if str(x).isdigit())),
        "dp_url": str(meta.get("dp_url") or ""),
        "secret_mode": bool(meta.get("secret_mode", False)),
        "force_join_chat_id": int(meta.get("force_join_chat_id") or 0),
        "force_join_link": str(meta.get("force_join_link") or ""),
        "support_group_url": str(meta.get("support_group_url") or ""),
        "custom_random_messages": msgs,
    }
    db = _get_db()
    if db is not None:
        db["meta"].update_one({"_id": "config"}, {"$set": clean}, upsert=True)
        return
    data = _load_local()
    data.update(clean)
    _save_local(data)


def set_owner_random_messages(raw_text: str, append: bool = True) -> list[str]:
    new_items = parse_bulk_random_messages(raw_text)
    meta = get_meta_state()
    if append:
        existing = meta.get("custom_random_messages", [])
        combined = existing + new_items
    else:
        combined = new_items
    meta["custom_random_messages"] = combined
    save_meta_state(meta)
    return combined


def clear_owner_random_messages():
    meta = get_meta_state()
    meta["custom_random_messages"] = []
    save_meta_state(meta)


def get_owner_random_messages() -> list[str]:
    return get_meta_state().get("custom_random_messages", [])


def _cleanup_host_tasks(host_state: dict):
    tasks: dict[int, asyncio.Task] = host_state.get("tagging_tasks") or {}
    for cid, task in list(tasks.items()):
        tasks.pop(cid, None)
        if task and not task.done():
            task.cancel()

    bg: dict[int, asyncio.Task] = host_state.get("background_tasks") or {}
    for tid, task in list(bg.items()):
        bg.pop(tid, None)
        if task and not task.done():
            task.cancel()


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
            "approved_users": set(),
            "tagging_tasks": {},
            "background_tasks": {},
            "task_seq": 100,
            "welcomed_users": set(),
            "last_msg": {},
            "quit_enabled": True,
            "welcome_enabled": True,
            "started_at": time.time(),
        }
        ACTIVE_HOSTS[user_id] = host_state
        await attach_userbot_handlers(client, host_state, ACTIVE_HOSTS)
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
