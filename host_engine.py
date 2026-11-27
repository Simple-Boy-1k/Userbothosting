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

BTN_1_TEXT = "💬 <b>𝗚𝗜𝗥𝗟𝗦 𝗚𝗥𝗢𝗨𝗣 𝟭</b>"
BTN_2_TEXT = "🔥 <b>𝗚𝗜𝗥𝗟𝗦 𝗚𝗥𝗢𝗨𝗣 𝟮</b>"

FIRST_DM_HEADER = "🖤 <b>𝗝𝗢𝗜𝗡 𝗠𝗬 𝗚𝗖</b> — <b>𝗚𝗼𝗼𝗱 𝗩𝗶𝗯𝗲𝘀, 𝗖𝗿𝗮𝘇𝘆 𝗣𝗲𝗼𝗽𝗹𝗲 &amp; 𝗨𝗻𝗹𝗶𝗺𝗶𝘁𝗲𝗱 𝗙𝘂𝗻!</b> 😎"
QUIT_MESSAGE = "🚪👋 <b>𝗠𝗲𝗺𝗯𝗲𝗿 𝗴𝗿𝗼𝘂𝗽 𝘀𝗲 𝗾𝘂𝗶𝘁 𝗸𝗮𝗿 𝗴𝗮𝘆𝗮 𝗵𝗮𝗶!</b>"

TAG_DELAY_SECONDS = 0.35

RANDOM_MESSAGES = [
    "<b>𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄𝐈 𝐒𝐏𝐎𝐓𝐈𝐅𝐘 𝐃𝐀𝐋 𝐊𝐄</b>",
    "<b>𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃</b>",
    "<b>𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐒𝐔𝐀𝐑 𝐊𝐀 𝐋𝐎𝐔𝐃𝐀 𝐎𝐑 𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐎𝐃𝐀</b>",
    "<b>𝐊𝐈𝐓𝐍𝐈 𝐆𝐋𝐈𝐘𝐀 𝐏𝐃𝐖𝐄𝐆𝐀 𝐀𝐏𝐍𝐈 𝐌𝐀 𝐊𝐎</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐍 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 𝐌𝐄𝐈 𝐁𝐄𝐒𝐀𝐍 𝐊𝐄 𝐋𝐀𝐃𝐃𝐔 𝐁𝐇𝐀𝐑 𝐃𝐔𝐍𝐆𝐀 🤩🥳🔥😈</b>",
    "<b>𝐏𝐀𝐏𝐀 𝐊𝐈 𝐒𝐏𝐄𝐄𝐃 𝐌𝐓𝐂𝐇 𝐍𝐇𝐈 𝐇𝐎 𝐑𝐇𝐈 𝐊𝐘𝐀</b>",
    "<b>𝐊𝐮𝐭𝐭𝐞 𝐤𝐢 𝐣𝐚𝐭</b>",
    "<b>𝐀𝐩𝐧𝐢 𝐠𝐚𝐚𝐧𝐝 𝐦𝐞𝐢𝐧 𝐦𝐮𝐭𝐡𝐢 𝐝𝐚𝐚𝐥</b>",
    "<b>𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄 𝐒𝐔𝐓𝐋𝐈 𝐁𝐎𝐌𝐁 𝐅𝐎𝐃 𝐃𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐉𝐇𝐀𝐀𝐓𝐄 𝐉𝐀𝐋 𝐊𝐄 𝐊𝐇𝐀𝐀𝐊 𝐇𝐎 𝐉𝐀𝐘𝐄𝐆𝐈 💣</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩</b>",
    "<b>𝐀𝐩𝐧𝐢 𝐠𝐚𝐚𝐧𝐝 𝐦𝐞𝐢𝐧 𝐦𝐮𝐭𝐡𝐢 𝐝𝐚𝐚𝐥</b>",
    "<b>𝐉𝐡𝐚𝐚𝐧𝐭 𝐤𝐞 𝐩𝐢𝐬𝐬𝐮-</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄 𝐀𝐀𝐀𝐆 𝐋𝐀𝐆𝐀𝐃𝐈𝐀 𝐌𝐄𝐑𝐀 𝐌𝐎𝐓𝐀 𝐋𝐔𝐍𝐃 𝐃𝐀𝐋𝐊𝐄 🔥🔥💦😆😆</b>",
    "<b>𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐎𝐓𝐎 𝐂𝐇𝐎𝐃 𝐂𝐇𝐎𝐃𝐊𝐄 𝐏𝐔𝐑𝐀 𝐅𝐀𝐀𝐃 𝐃𝐈𝐀 𝐂𝐇𝐔𝐓𝐇 𝐀𝐁𝐁 𝐓𝐄𝐑𝐈 𝐆𝐅 𝐊𝐎 𝐁𝐇𝐄𝐉 😆💦🤤</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐆𝐅 𝐊 𝐒𝐀𝐀𝐓𝐇 𝐌𝐌𝐒 𝐁𝐀𝐍𝐀𝐀 𝐂𝐇𝐔𝐊𝐀 𝐇𝐔</b>",
    "<b>𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐂𝐑𝐄𝐃𝐈𝐓 𝐂𝐀𝐑𝐃 𝐃𝐀𝐋 𝐊𝐄 𝐀𝐆𝐄 𝐒𝐄 500 𝐊𝐄 𝐊𝐀𝐀𝐑𝐄 𝐍𝐎𝐓𝐄 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 💰💰🤩</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐒𝐔𝐃𝐎 𝐋𝐀𝐆𝐀 𝐊𝐄 𝐁𝐈𝐆𝐒𝐏𝐀𝐌 𝐋𝐀𝐆𝐀 𝐊𝐄 𝟗𝟗𝟗𝟗 𝐅𝐔𝐂𝐊 𝐋𝐀𝐆𝐀𝐀 𝐃𝐔 🤩🥳🔥</b>",
    "<b>𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 30𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎</b>",
    "<b>𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐍𝐄 𝐒𝐇𝐎𝐑 𝐇𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐑𝐀𝐍𝐃𝐈 𝐂𝐇𝐎𝐑 𝐇𝐄 💋💋💦</b>",
    "<b>𝐒𝐔𝐍 𝐒𝐔𝐍 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐉𝐇𝐀𝐍𝐓𝐎 𝐊𝐄 𝐒𝐎𝐔𝐃𝐀𝐆𝐀𝐑 𝐀𝐏𝐍𝐈 𝐌𝐔𝐌𝐌𝐘 𝐊𝐈 𝐍𝐔𝐃𝐄𝐒 𝐁𝐇𝐄𝐉</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐄𝐄𝐌𝐒 𝐒𝐄 𝐂𝐇𝐔𝐃𝐖𝐀𝐕𝐔𝐍𝐆𝐀 𝐌𝐀𝐃𝐄𝐑𝐂𝐇𝐎𝐎𝐃 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 💦🤣</b>",
    "<b>𝐊𝐈𝐅𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒𝐒</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐆𝐀𝐍𝐃 𝐌𝐄 𝐃𝐄𝐓𝐎𝐋 𝐃𝐀𝐀𝐋 𝐃𝐔𝐍𝐆𝐀</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄 𝐂𝐇𝐀𝐍𝐆𝐄𝐒 𝐂𝐎𝐌𝐌𝐈𝐓 𝐊𝐑𝐔𝐆𝐀 𝐅𝐈𝐑 𝐓𝐄𝐑𝐈 𝐁𝐇𝐄𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐂𝐀𝐋𝐋𝐘 𝐔𝐏𝐃𝐀𝐓𝐄 𝐇𝐎𝐉𝐀𝐀𝐘𝐄𝐆𝐈 🤖🙏🤔</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐂𝐇𝐔𝐔𝐓 𝐊𝐈 𝐂𝐇𝐔𝐔𝐓 𝐌𝐄𝐈 𝐒𝐇𝐎𝐔𝐋𝐃𝐄𝐑𝐈𝐍𝐆 𝐊𝐀𝐑 𝐃𝐔𝐍𝐆𝐀𝐀 𝐇𝐈𝐋𝐀𝐓𝐄 𝐇𝐔𝐘𝐄 𝐁𝐇𝐈 𝐃𝐀𝐑𝐃 𝐇𝐎𝐆𝐀𝐀𝐀 😱🤮👺</b>",
    "<b>𝐑𝐀𝐍𝐈𝐃𝐈𝐈𝐈</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋</b>",
    "<b>𝐊𝐈𝐓𝐍𝐈 𝐂𝐇𝐎𝐃𝐔 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐀𝐁 𝐎𝐑..</b>",
    "<b>𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑</b>",
    "<b>𝐓𝐄𝐑𝐈𝐈𝐈 𝐌𝐀𝐀 𝐊𝐀𝐀 𝐁𝐉𝐒𝐎𝐃𝐀𝐀𝐀</b>",
    "<b>𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣</b>",
    "<b>𝐃𝐔𝐃𝐇 𝐇𝐈𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐄 𝐔𝐏𝐑 𝐍𝐈𝐂𝐇𝐄 🆙🆒😙</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 30𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐎 𝐂𝐇𝐎𝐃 𝐂𝐇𝐎𝐃𝐊𝐄 𝐕𝐈𝐃𝐄𝐎 𝐁𝐀𝐍𝐀𝐊𝐄 𝐗𝐍𝐗𝐗.𝐂𝐎𝐌 𝐏𝐄 𝐍𝐄𝐄𝐋𝐀𝐌 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐊𝐔𝐓𝐓𝐄 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 💦💋</b>",
    "<b>𝐊𝐈𝐒𝐀𝐍 𝐊𝐎 𝐊𝐇𝐎𝐃𝐍𝐀 𝐎𝐑</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋</b>",
    "<b>𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐎 𝐊𝐎𝐋𝐊𝐀𝐓𝐀 𝐕𝐀𝐀𝐋𝐄 𝐉𝐈𝐓𝐔 𝐁𝐇𝐀𝐈𝐘𝐀 𝐊𝐀 𝐋𝐔𝐍𝐃 𝐌𝐔𝐁𝐀𝐑𝐀𝐊 🤩🤩</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐔𝐌𝐌𝐘 𝐊𝐄 𝐒𝐀𝐀𝐓𝐇 𝐋𝐔𝐃𝐎 𝐊𝐇𝐄𝐋𝐓𝐄 𝐊𝐇𝐄𝐋𝐓𝐄 𝐔𝐒𝐊𝐄 𝐌𝐔𝐇 𝐌𝐄 𝐀𝐏𝐍𝐀 𝐋𝐎𝐃𝐀 𝐃𝐄 𝐃𝐔𝐍𝐆𝐀 ☝🏻☝🏻😬</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐔𝐍𝐃 𝐊𝐀𝐀𝐋𝐀</b>",
    "<b>Ullu ke pathe</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥</b>",
    "<b>𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃</b>",
    "<b>𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣</b>",
    "<b>𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐊𝐇𝐔𝐋𝐄 𝐁𝐀𝐉𝐀𝐑 𝐌𝐄 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 🤣🤣💋</b>",
]

ACTIVE_HOSTS = {}
PENDING_LOGINS = {}
VERIFIED_JOIN_USERS = set()

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
        "verified_users": [],
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
            "verified_users": list(dict.fromkeys(int(x) for x in doc.get("verified_users", []) if str(x).isdigit())),
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
        "verified_users": list(dict.fromkeys(int(x) for x in data.get("verified_users", []) if str(x).isdigit())),
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
        "verified_users": list(dict.fromkeys(int(x) for x in meta.get("verified_users", []) if str(x).isdigit())),
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


def mark_user_verified(user_id: int):
    VERIFIED_JOIN_USERS.add(int(user_id))
    meta = get_meta_state()
    if int(user_id) not in meta["verified_users"]:
        meta["verified_users"].append(int(user_id))
        save_meta_state(meta)


def is_user_verified(user_id: int) -> bool:
    if int(user_id) in VERIFIED_JOIN_USERS:
        return True
    meta = get_meta_state()
    if int(user_id) in meta["verified_users"]:
        VERIFIED_JOIN_USERS.add(int(user_id))
        return True
    return False


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


async def send_force_join_prompt(event):
    link_1, link_2 = get_active_group_links()
    safe_l1 = _escape_html(link_1)
    safe_l2 = _escape_html(link_2)

    msg = (
        f"<blockquote><b>🔒✨ 𝗣𝗘𝗛𝗟𝗘 𝗗𝗢𝗡𝗢 𝗚𝗥𝗢𝗨𝗣𝗦 𝗣𝗘 𝗝𝗢𝗜𝗡 / 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗗𝗔𝗔𝗟𝗘𝗜𝗡!</b>\n\n"
        f'• <a href="{safe_l1}">{BTN_1_TEXT}</a>\n'
        f'• <a href="{safe_l2}">{BTN_2_TEXT}</a>\n\n'
        f"✅ <b>𝗗𝗼𝗻𝗼 𝗽𝗲 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝗱𝗮𝗮𝗹𝗻𝗲 𝗸𝗲 𝗯𝗮𝗮𝗱 <code>check joined</code> 𝗹𝗶𝗸𝗵𝗲𝗶𝗻!</b></blockquote>"
    )
    await event.reply(msg, parse_mode="html", link_preview=False)


async def send_first_dm_card(event):
    link_1, link_2 = get_active_group_links()
    safe_l1 = _escape_html(link_1)
    safe_l2 = _escape_html(link_2)

    msg = (
        f"<blockquote><b>{FIRST_DM_HEADER}</b>\n\n"
        f'• <a href="{safe_l1}">{BTN_1_TEXT}</a>\n'
        f'• <a href="{safe_l2}">{BTN_2_TEXT}</a></blockquote>'
    )
    await event.reply(msg, parse_mode="html", link_preview=False)


async def _check_single_link_joined_or_requested(client: TelegramClient, user_id: int, link: str) -> bool:
    raw = (link or "").strip()
    if not raw:
        return True

    try:
        if "/+" in raw or "joinchat/" in raw:
            invite_hash = (
                raw.split("/+", 1)[1].split("?", 1)[0].strip()
                if "/+" in raw
                else raw.split("joinchat/", 1)[1].split("?", 1)[0].strip()
            )
            info = await client(functions.messages.CheckChatInviteRequest(hash=invite_hash))
            chat_obj = getattr(info, "chat", None)
            if chat_obj:
                try:
                    await client.get_permissions(chat_obj, user_id)
                    return True
                except Exception:
                    pass
                try:
                    reqs = await client(
                        functions.messages.GetChatInviteRequestsRequest(
                            peer=chat_obj,
                            limit=50,
                        )
                    )
                    for r in getattr(reqs, "requests", []) or []:
                        if getattr(r, "user_id", None) == user_id:
                            return True
                except Exception:
                    pass
            return False
        else:
            entity = await client.get_entity(raw)
            try:
                await client.get_permissions(entity, user_id)
                return True
            except Exception:
                return False
    except Exception:
        return False


async def verify_both_groups_for_user(client: TelegramClient, user_id: int) -> tuple[bool, bool, bool]:
    link_1, link_2 = get_active_group_links()
    ok1 = await _check_single_link_joined_or_requested(client, user_id, link_1)
    ok2 = await _check_single_link_joined_or_requested(client, user_id, link_2)
    return (ok1 and ok2), ok1, ok2


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

        # Turant ek-ek karke (1 member per message) custom text ke saath tag karega
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
            f"1️⃣ {BTN_1_TEXT}\n"
            f"2️⃣ {BTN_2_TEXT}</blockquote>",
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
        # Command message delete nahi hoga; turant start karke aage tag chalega
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
                await event.reply(f"<blockquote>{reply_text}</blockquote>", parse_mode="html")
            return

        if event.is_private:
            raw_txt = (event.raw_text or "").strip().lower()

            if raw_txt in {"check joined", ".checkjoined", "joined"}:
                both_ok, g1_ok, g2_ok = await verify_both_groups_for_user(client, sender_id)
                if both_ok:
                    mark_user_verified(sender_id)
                    welcomed_users.add(sender_id)
                    await event.reply(
                        "<blockquote>✅🎉 <b>𝗗𝗼𝗻𝗼 𝗴𝗿𝗼𝘂𝗽𝘀 𝗽𝗲 𝗷𝗼𝗶𝗻 / 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝘃𝗲𝗿𝗶𝗳𝘆 𝗵𝗼 𝗴𝗮𝘆𝗮! 𝗔𝗯 𝗮𝗮𝗴𝗲 𝗸𝗮 𝗮𝗰𝗰𝗲𝘀𝘀 𝗼𝗽𝗲𝗻 𝗵𝗮𝗶.</b></blockquote>",
                        parse_mode="html",
                    )
                    await send_first_dm_card(event)
                else:
                    s1 = "✅" if g1_ok else "❌"
                    s2 = "✅" if g2_ok else "❌"
                    await event.reply(
                        f"<blockquote>⚠️ <b>𝗣𝗲𝗵𝗹𝗲 𝗱𝗼𝗻𝗼 𝗴𝗿𝗼𝘂𝗽𝘀 𝗽𝗲 𝗷𝗼𝗶𝗻 / 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝗱𝗮𝗮𝗹𝗲𝗶𝗻:</b>\n"
                        f"{s1} {BTN_1_TEXT}\n"
                        f"{s2} {BTN_2_TEXT}\n\n"
                        f"👉 <b>𝗗𝗼𝗻𝗼 𝗸𝗲 𝗯𝗮𝗮𝗱 <code>check joined</code> 𝗯𝗵𝗲𝗷𝗲𝗶𝗻!</b></blockquote>",
                        parse_mode="html",
                    )
                return

            if not is_user_verified(sender_id) and raw_txt in {"/start", "start", "hi", "hii", "hello", "hey"}:
                await send_force_join_prompt(event)
                return

            if sender_id in raid_users:
                reply_text = pick_random_message(host_state, sender_id)
                await asyncio.sleep(0.8)
                await event.reply(f"<blockquote>{reply_text}</blockquote>", parse_mode="html")
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
        VERIFIED_JOIN_USERS.update(meta.get("verified_users", []))

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
