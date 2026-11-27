import asyncio
import json
import os
import random
from pathlib import Path
from pymongo import MongoClient
from telethon import TelegramClient, events, types
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.sessions import StringSession

STORE_FILE = Path("hoster_data.json")

# ================= GROUP LINKS & FIRST DM TEXT =================
GROUP_LINK_1 = "https://t.me/+CBnAUbPjGdlmYzBk"
GROUP_LINK_2 = "https://t.me/+EVbG4sFK-tg1NjA1"

BTN_1_TEXT = "💬𝗚𝗥𝗜𝗟𝗦 𝗚𝗥𝗢𝗨𝗣𝟭"
BTN_2_TEXT = "🔥𝗚𝗥𝗜𝗟𝗦 𝗚𝗥𝗢𝗨𝗣𝟮"

FIRST_DM_HEADER = "🖤 𝗝𝗢𝗜𝗡 𝗠𝗬 𝗚𝗖 ✨
🔥 Good Vibes, Crazy People & Unlimited Fun! 😎"
QUIT_MESSAGE = "🚪👋 Member group se quit kar gaya hai!"

RANDOM_MESSAGES = [
    "𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄𝐈 𝐒𝐏𝐎𝐓𝐈𝐅𝐘 𝐃𝐀𝐋 𝐊𝐄",
    "𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
    "𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐒𝐔𝐀𝐑 𝐊𝐀 𝐋𝐎𝐔𝐃𝐀 𝐎𝐑 𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐎𝐃𝐀",
    "𝐊𝐈𝐓𝐍𝐈 𝐆𝐋𝐈𝐘𝐀 𝐏𝐃𝐖𝐄𝐆𝐀 𝐀𝐏𝐍𝐈 𝐌𝐀 𝐊𝐎",
    "𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐍 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 𝐌𝐄𝐈 𝐁𝐄𝐒𝐀𝐍 𝐊𝐄 𝐋𝐀𝐃𝐃𝐔 𝐁𝐇𝐀𝐑 𝐃𝐔𝐍𝐆𝐀 🤩🥳🔥😈",
    "𝐏𝐀𝐏𝐀 𝐊𝐈 𝐒𝐏𝐄𝐄𝐃 𝐌𝐓𝐂𝐇 𝐍𝐇𝐈 𝐇𝐎 𝐑𝐇𝐈 𝐊𝐘𝐀",
    "𝐊𝐮𝐭𝐭𝐞 𝐤𝐢 𝐣𝐚𝐭",
    "𝐀𝐩𝐧𝐢 𝐠𝐚𝐚𝐧𝐝 𝐦𝐞𝐢𝐧 𝐦𝐮𝐭𝐡𝐢 𝐝𝐚𝐚𝐥",
    "𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄 𝐒𝐔𝐓𝐋𝐈 𝐁𝐎𝐌𝐁 𝐅𝐎𝐃 𝐃𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐉𝐇𝐀𝐀𝐓𝐄 𝐉𝐀𝐋 𝐊𝐄 𝐊𝐇𝐀𝐀𝐊 𝐇𝐎 𝐉𝐀𝐘𝐄𝐆𝐈 💣",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩",
    "𝐀𝐩𝐧𝐢 𝐠𝐚𝐚𝐧𝐝 𝐦𝐞𝐢𝐧 𝐦𝐮𝐭𝐡𝐢 𝐝𝐚𝐚𝐥",
    "𝐉𝐡𝐚𝐚𝐧𝐭 𝐤𝐞 𝐩𝐢𝐬𝐬𝐮-",
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐀𝐀𝐀𝐆 𝐋𝐀𝐆𝐀𝐃𝐈𝐀 𝐌𝐄𝐑𝐀 𝐌𝐎𝐓𝐀 𝐋𝐔𝐍𝐃 𝐃𝐀𝐋𝐊𝐄 🔥🔥💦😆😆",
    "𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐎𝐓𝐎 𝐂𝐇𝐎𝐃 𝐂𝐇𝐎𝐃𝐊𝐄 𝐏𝐔𝐑𝐀 𝐅𝐀𝐀𝐃 𝐃𝐈𝐀 𝐂𝐇𝐔𝐓𝐇 𝐀𝐁𝐁 𝐓𝐄𝐑𝐈 𝐆𝐅 𝐊𝐎 𝐁𝐇𝐄𝐉 😆💦🤤",
    "𝐓𝐄𝐑𝐈 𝐆𝐅 𝐊 𝐒𝐀𝐀𝐓𝐇 𝐌𝐌𝐒 𝐁𝐀𝐍𝐀𝐀 𝐂𝐇𝐔𝐊𝐀 𝐇𝐔",
    "𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐒𝐔𝐃𝐎 𝐋𝐀𝐆𝐀 𝐊𝐄 𝐁𝐈𝐆𝐒𝐏𝐀𝐌 𝐋𝐀𝐆𝐀 𝐊𝐄 𝟗𝟗𝟗𝟗 𝐅𝐔𝐂𝐊 𝐋𝐀𝐆𝐀𝐀 𝐃𝐔 🤩🥳🔥",
    "𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋",
    "𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 30𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
    "𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐍𝐄 𝐒𝐇𝐎𝐑 𝐇𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐑𝐀𝐍𝐃𝐈 𝐂𝐇𝐎𝐑 𝐇𝐄 💋💋💦",
    "𝐒𝐔𝐍 𝐒𝐔𝐍 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐉𝐇𝐀𝐍𝐓𝐎 𝐊𝐄 𝐒𝐎𝐔𝐃𝐀𝐆𝐀𝐑 𝐀𝐏𝐍𝐈 𝐌𝐔𝐌𝐌𝐘 𝐊𝐈 𝐍𝐔𝐃𝐄𝐒 𝐁𝐇𝐄𝐉",
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐄𝐄𝐌𝐒 𝐒𝐄 𝐂𝐇𝐔𝐃𝐖𝐀𝐕𝐔𝐍𝐆𝐀 𝐌𝐀𝐃𝐄𝐑𝐂𝐇𝐎𝐎𝐃 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 💦🤣",
    "𝐊𝐈𝐅𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐆𝐀𝐍𝐃 𝐌𝐄 𝐃𝐄𝐓𝐎𝐋 𝐃𝐀𝐀𝐋 𝐃𝐔𝐍𝐆𝐀",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄 𝐂𝐇𝐀𝐍𝐆𝐄𝐒 𝐂𝐎𝐌𝐌𝐈𝐓 𝐊𝐑𝐔𝐆𝐀 𝐅𝐈𝐑 𝐓𝐄𝐑𝐈 𝐁𝐇𝐄𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐂𝐀𝐋𝐋𝐘 𝐔𝐏𝐃𝐀𝐓𝐄 𝐇𝐎𝐉𝐀𝐀𝐘𝐄𝐆𝐈 🤖🙏🤔",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥",
    "𝐓𝐄𝐑𝐈 𝐂𝐇𝐔𝐔𝐓 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐒𝐇𝐎𝐔𝐋𝐃𝐄𝐑𝐈𝐍𝐆 𝐊𝐀𝐑 𝐃𝐔𝐍𝐆𝐀𝐀 𝐇𝐈𝐋𝐀𝐓𝐄 𝐇𝐔𝐘𝐄 𝐁𝐇𝐈 𝐃𝐀𝐑𝐃 𝐇𝐎𝐆𝐀𝐀𝐀 😱🤮👺",
    "𝐑𝐀𝐍𝐈𝐃𝐈𝐈𝐈",
    "𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋",
    "𝐊𝐈𝐓𝐍𝐈 𝐂𝐇𝐎𝐃𝐔 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐀𝐁 𝐎𝐑..",
    "𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑",
    "𝐓𝐄𝐑𝐈𝐈𝐈 𝐌𝐀𝐀 𝐊𝐀𝐀 𝐁𝐉𝐒𝐎𝐃𝐀𝐀𝐀",
    "𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
    "𝐃𝐔𝐃𝐇 𝐇𝐈𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐄 𝐔𝐏𝐑 𝐍𝐈𝐂𝐇𝐄 🆙🆒😙",
    "𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 30𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐎 𝐂𝐇𝐎𝐃 𝐂𝐇𝐎𝐃𝐊𝐄 𝐕𝐈𝐃𝐄𝐎 𝐁𝐀𝐍𝐀𝐊𝐄 𝐗𝐍𝐗𝐗.𝐂𝐎𝐌 𝐏𝐄 𝐍𝐄𝐄𝐋𝐀𝐌 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐊𝐔𝐓𝐓𝐄 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 💦💋",
    "𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋",
    "𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐎 𝐊𝐎𝐋𝐊𝐀𝐓𝐀 𝐕𝐀𝐀𝐋𝐄 𝐉𝐈𝐓𝐔 𝐁𝐇𝐀𝐈𝐘𝐀 𝐊𝐀 𝐋𝐔𝐍𝐃 𝐌𝐔𝐁𝐀𝐑𝐀𝐊 🤩🤩",
    "𝐓𝐄𝐑𝐈 𝐌𝐔𝐌𝐌𝐘 𝐊𝐄 𝐒𝐀𝐀𝐓𝐇 𝐋𝐔𝐃𝐎 𝐊𝐇𝐄𝐋𝐓𝐄 𝐊𝐇𝐄𝐋𝐓𝐄 𝐔𝐒𝐊𝐄 𝐌𝐔𝐇 𝐌𝐄 𝐀𝐏𝐍𝐀 𝐋𝐎𝐃𝐀 𝐃𝐄 𝐃𝐔𝐍𝐆𝐀 ☝🏻☝🏻😬",
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐔𝐍𝐃 𝐊𝐀𝐀𝐋𝐀",
    "Ullu ke pathe",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥",
    "𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
    "𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋",
]

ACTIVE_HOSTS = {}
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
        f"{FIRST_DM_HEADER}\n\n"
        f'<blockquote><b><a href="{safe_l1}">{BTN_1_TEXT}</a></b></blockquote>\n'
        f'<blockquote><b><a href="{safe_l2}">{BTN_2_TEXT}</a></b></blockquote>'
    )
    await event.reply(msg, parse_mode="html", link_preview=False)


def pick_random_message(host_state: dict, target_id: int) -> str:
    valid_msgs = [m.strip() for m in RANDOM_MESSAGES if isinstance(m, str) and m.strip()]
    if not valid_msgs:
        return "Hello! 👋"
    if len(valid_msgs) == 1:
        return valid_msgs[0]
    last_msg = host_state["last_msg"].get(target_id)
    pool = [m for m in valid_msgs if m != last_msg]
    chosen = random.choice(pool or valid_msgs)
    host_state["last_msg"][target_id] = chosen
    return chosen


def _clean_mention_name(name: str | None) -> str:
    cleaned = (name or "User").replace("[", "").replace("]", "").replace("(", "").replace(")", "").strip()
    return cleaned or "User"


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
                targets.append((member.id, _clean_mention_name(member.first_name)))
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
                    targets.append((sender.id, _clean_mention_name(getattr(sender, "first_name", None))))
        except Exception:
            pass

    return targets


async def _run_tagall_in_chat(client: TelegramClient, chat_id: int, tagging_chats: set):
    if chat_id in tagging_chats:
        return
    tagging_chats.add(chat_id)
    try:
        targets = await _collect_group_targets(client, chat_id)
        if not targets:
            await client.send_message(chat_id, "⚠️ Is group mein tag karne ke liye koi member nahi mila.")
            return

        mentions = []
        for uid, uname in targets:
            if chat_id not in tagging_chats:
                break
            mentions.append(f"✨ [{uname}](tg://user?id={uid})")
            if len(mentions) == 5:
                await client.send_message(chat_id, " ".join(mentions), parse_mode="md")
                mentions = []
                await asyncio.sleep(1.5)

        if mentions and chat_id in tagging_chats:
            await client.send_message(chat_id, " ".join(mentions), parse_mode="md")
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
    uname = _clean_mention_name(getattr(user, "first_name", None)) if user else "Member"
    uid = getattr(user, "id", None)
    mention = f"[{uname}](tg://user?id={uid})" if uid else uname
    await client.send_message(
        chat_id,
        f"{QUIT_MESSAGE}\n👤 {mention}",
        parse_mode="md",
    )


async def _attach_handlers(client: TelegramClient, host_state: dict):
    raid_users = host_state["raid_users"]
    tagging_chats = host_state["tagging"]
    welcomed_users = host_state["welcomed_users"]
    me = await client.get_me()
    my_id = me.id if me else 0

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_cmd(event):
        await event.edit("🏓 Pong! Userbot is active.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.setlinks\s+(\S+)\s+(\S+)$"))
    async def setlinks_cmd(event):
        l1 = event.pattern_match.group(1)
        l2 = event.pattern_match.group(2)
        set_group_links(l1, l2)
        await event.edit(
            f"✅🔗 Group links update ho gaye!\n"
            f"1️⃣ {BTN_1_TEXT}\n"
            f"2️⃣ {BTN_2_TEXT}"
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.tagall$"))
    async def tagall_cmd(event):
        if not event.is_group:
            await event.edit("⚠️ Yeh command sirf group mein chalega.")
            return
        if event.chat_id in tagging_chats:
            await event.edit("⏳ Is group mein tagall pehle se chal raha hai.")
            return
        try:
            await event.delete()
        except Exception:
            pass
        await _run_tagall_in_chat(client, event.chat_id, tagging_chats)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stoptagall$"))
    async def stoptagall_cmd(event):
        if event.chat_id in tagging_chats:
            tagging_chats.discard(event.chat_id)
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
            txt = (event.raw_text or "").strip().lower()
            if txt == "stop tagall":
                tagging_chats.discard(event.chat_id)
                await event.reply("🛑✨ Tagall rok diya gaya hai!")
                return

            if txt == "tagall hii" or txt.startswith("tagall "):
                await _run_tagall_in_chat(client, event.chat_id, tagging_chats)
                return

            if sender_id in raid_users and await _is_userbot_mentioned(event, me):
                reply_text = pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text)
            return

        if event.is_private:
            if sender_id in raid_users:
                reply_text = pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(reply_text)
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
            return False, "Session valid ya authorized nahi hai."

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
            return True, "✅ Success Userbot Restarted! Use .ping."
        return True, "✅ Success Userbot Hosted! Use .ping to check."
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"❌ Host karne mein error aaya: {e}"


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
        return False, "❌ Phone number invalid hai. Country code ke saath sahi number daalein (jaise +919876543210)."
    except FloodWaitError as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"⏳ Telegram rate limit laga hai. {e.seconds} seconds baad try karein."
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return False, f"❌ OTP bhejne mein error aaya: {e}"


async def submit_otp_code(user_id: int, otp_text: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "otp":
        return "error", "❌ Koi active OTP request nahi mila. Pehle /host likhein."

    code = "".join(ch for ch in otp_text if ch.isdigit())
    if not code:
        return "retry", "⚠️ Valid numeric OTP bhejein."

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
        return "error", f"❌ Login fail ho gaya: {e}"


async def submit_2fa_password(user_id: int, password: str, api_id: int, api_hash: str) -> tuple[str, str]:
    pending = PENDING_LOGINS.get(user_id)
    if not pending or pending.get("step") != "2fa":
        return "error", "❌ Koi active 2FA step nahi mila. Pehle /host likhein."

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
        return "error", f"❌ 2FA login fail ho gaya: {e}"


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

    return False, "ℹ️ Aapka koi hosted account nahi mila. Pehle /host likhein."


async def logout_user_account(user_id: int) -> tuple[bool, str]:
    await cancel_pending_login(user_id)
    info = ACTIVE_HOSTS.pop(user_id, None)
    delete_session(user_id)

    if not info:
        return False, "ℹ️ Logout karne ke liye koi active hosted account nahi mila."

    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "🚪✅ Account logout aur disconnect ho gaya hai."


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_sessions()
    for uid, session_str in saved.items():
        await start_client_from_session(uid, session_str, api_id, api_hash, persist=False)
