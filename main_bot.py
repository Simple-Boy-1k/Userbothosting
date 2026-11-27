import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from userbot_engine import (
    ACTIVE_HOSTS,
    PENDING_LOGINS,
    BTN_1_TEXT,
    BTN_2_TEXT,
    cancel_pending_login,
    get_active_group_links,
    logout_user_account,
    restart_user_account,
    restore_all_saved_sessions,
    send_first_dm_card,
    send_login_code,
    set_group_links,
    submit_2fa_password,
    submit_otp_code,
)

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

LOGIN_FLOW = {}


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
        f"1️⃣ {BTN_1_TEXT}\n"
        f"2️⃣ {BTN_2_TEXT}</blockquote>",
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
