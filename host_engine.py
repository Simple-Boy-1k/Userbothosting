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

# Yahan apni marzi ke 50 random messages likhein
RANDOM_MESSAGES = [
    "𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",   # 01
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 �_K𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",   # 02
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐄𝐈 𝐒𝐏𝐎𝐓𝐈𝐅𝐘 𝐃𝐀𝐋 𝐊𝐄",   # 03
    "𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",   # 04
    "𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐒𝐔𝐀𝐑 𝐊𝐀 𝐋𝐎𝐔𝐃𝐀 𝐎𝐑 𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐎𝐃𝐀",   # 05
    "𝙆𝙄𝙏𝙉𝙄 𝙂𝙇𝙄𝙔𝘼 𝙋𝘿𝙒𝙀𝙂𝘼 𝘼𝙋𝙉𝙄 𝙈𝘼 𝙆𝙊",   # 06
    "𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐍 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄 𝐌𝐄𝐈 𝐁𝐄𝐒𝐀𝐍 𝐊𝐄 𝐋𝐀𝐃𝐃𝐔 𝐁𝐇𝐀𝐑 𝐃𝐔𝐍𝐆𝐀🤩🥳�fire😈",   # 07
    "𝙋𝘼𝙋𝘼 𝙆𝙄 𝙎𝙋𝙀𝙀𝘿 𝙈𝙏𝘾𝙃 𝙉𝙃𝙄 𝙃𝙊 𝙍𝙃𝙄 𝙆𝙔𝘼",   # 08
    "𝙆𝙪𝙩𝙩𝙚 𝙠𝙞 𝙟𝙖𝙩",   # 09
    "𝘼𝙥𝙣𝙞 𝙜𝙖𝙖𝙣𝙙 𝙢𝙚𝙞𝙣 𝙢𝙪𝙩𝙝𝙞 𝙙𝙖𝙖𝙡",   # 10
    "𝙎𝘼𝘽 𝘽𝙊𝙇𝙏𝙀 𝙈𝙐𝙅𝙃𝙆𝙊 𝙋𝘼𝙋𝘼 𝙆𝙔𝙊𝙐𝙉𝙆𝙄 𝙈𝙀𝙉𝙀 𝘽𝘼𝙉𝘼𝘿𝙄𝘼 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝙊 𝙋𝙍𝙀𝙂𝙉𝙀𝙉𝙏 🤣🤣",   # 11
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣",   # 12
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 �_K𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",   # 13
    "𝘼𝙥𝙣𝙞 𝙜𝙖𝙖𝙣𝙙 𝙢𝙚𝙞𝙣 𝙢𝙪𝙩𝙝𝙞 𝙙𝙖𝙖𝙡",   # 14
    "𝙅𝙝𝙖𝙖𝙣𝙩 𝙠𝙚 𝙥𝙞𝙨𝙨𝙪-",   # 15
    "𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙆𝙀 𝘽𝙃𝙊𝙎𝘿𝙀 𝙈𝙀 𝘼𝘼𝘼𝙂 𝙇𝘼𝙂𝘼𝘿𝙄𝘼 𝙈𝙀𝙍𝘼 𝙈𝙊𝙏𝘼 𝙇𝙐𝙉𝘿 𝘿𝘼𝙇𝙆𝙀 🔥🔥💦😆😆",   # 16
    "𝙎𝘼𝘽 𝘽𝙊𝙇𝙏𝙀 𝙈𝙐𝙅𝙃𝙆𝙊 𝙋𝘼𝙋𝘼 𝙆𝙔𝙊𝙐𝙉𝙆𝙄 𝙈𝙀𝙉𝙀 𝘽𝘼𝙉𝘼𝘿𝙄𝘼 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝙊 𝙋𝙍𝙀𝙂𝙉𝙀𝙉𝙏 🤣🤣",   # 17
    "𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙆𝙊𝙏𝙊 𝘾𝙃𝙊𝘿 𝘾𝙃𝙊𝘿𝙆𝙀 𝙋𝙐𝙍𝘼 𝙁𝘼𝘼𝘿 𝘿𝙄𝘼 𝘾𝙃𝙐𝙏𝙃 𝘼𝘽𝘽 𝙏𝙀𝙍𝙄 𝙂𝙁 𝙆𝙊 𝘽𝙃𝙀𝙅 😆💦🤤",   # 18
    "𝙏𝙀𝙍𝙄 𝙂𝙁 𝙆 𝙎𝘼𝘼𝙏𝙃 𝙈𝙈𝙎 𝘽𝘼𝙉𝘼𝘼 𝘾𝙃𝙐𝙆𝘼 𝙃𝙐",   # 19
    "𝙆𝙄𝙎𝘼𝙉 𝙆𝙊 𝙆𝙃𝙊𝘿𝙉𝘼 𝙊𝙍",   # 20
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗖𝗥𝗘𝗗𝗜𝗧 𝗖𝗔𝗥𝗗 𝗗𝗔𝗟 𝗞𝗘 𝗔𝗚𝗘 𝗦𝗘 500 𝗞𝗘 𝗞𝗔𝗔𝗥𝗘 �_K𝗔𝗔𝗥𝗘 𝗡𝗢𝗧𝗘 𝗡𝗜𝗞𝗔𝗟𝗨𝗡𝗚𝗔𝗔 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘💰💰🤩",   # 21
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐒𝐔𝐃𝐎 𝐋𝐀𝐆𝐀 𝐊𝐄 𝐁𝐈𝐆𝐒𝐏𝐀𝐌 𝐋𝐀𝐆𝐀 𝐊𝐄 𝟗𝟗𝟗𝟗 𝐅𝐔𝐂𝐊 𝐋𝐀𝐆𝐀𝐀 𝐃𝐔 🤩🥳🔥",   # 22
    "𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍",   # 23
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗝𝗔𝗥 𝗠𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 🤣🤣💋",   # 24
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 30𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",   # 25
    "𝙂𝘼𝙇𝙄 𝙂𝘼𝙇𝙄 𝙉𝙀 𝙎𝙃𝙊𝙍 𝙃𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝘾𝙃𝙊𝙍 𝙃𝙀 💋💋💦",   # 26
    "𝐒𝐔𝐍 𝐒𝐔𝐍 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 𝐉𝐇𝐀𝐍𝐓𝐎 𝐊𝐄 𝐒𝐎𝐔𝐃𝐀𝐆𝐀𝐑 𝐀𝐏𝐍𝐈 𝐌𝐔𝐌𝐌𝐘 𝐊𝐈 𝐍𝐔𝐃𝐄𝐒 𝐁𝐇𝐄𝐉",   # 27
    "𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",   # 28
    "𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝙊 𝘾𝙃𝙀𝙀𝙈𝙎 𝙎𝙀 𝘾𝙃𝙐𝘿𝙒𝘼𝙑𝙐𝙉𝙂𝘼 𝙈𝘼𝘿𝙀𝙍𝘾𝙃𝙊𝙊𝘿 𝙆𝙀 𝙋𝙄𝙇𝙇𝙀 💦🤣",   # 29
    "𝙆𝙄𝙁𝙎𝙎𝙎𝙎𝙎𝙎𝙎𝙎𝙎𝙎𝙎𝙎",   # 30
    "𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙆𝙀 𝙂𝘼𝙉𝘿 𝙈𝙀 𝘿𝙀𝙏𝙊𝙇 𝘿𝘼𝘼𝙇 𝘿𝙐𝙉𝙂𝘼",   # 31
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",   # 32
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐄 𝐍𝐔𝐃𝐄𝐒 𝐆𝐎𝐎𝐆𝐋𝐄 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐁𝐄𝐇𝐄𝐍 𝐊𝐄 𝐋𝐀𝐄𝐖𝐃𝐄 👻🔥",   # 33
    "𝗧𝗘𝗥𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗦𝗛𝗢𝗨𝗟𝗗𝗘𝗥𝗜𝗡𝗚 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔𝗔 𝗛𝗜𝗟𝗔𝗧𝗘 𝗛𝗨𝗬𝗘 𝗕𝗛𝗜 𝗗𝗔𝗥𝗗 𝗛𝗢𝗚𝗔𝗔𝗔😱🤮👺",   # 34
    "𝙍𝘼𝙉𝙄𝘿𝙄𝙄𝙄",   # 35
    "𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋",   # 36
    "𝙆𝙄𝙏𝙉𝙄 𝘾𝙃𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙈𝘼 𝘼𝘽 𝙊𝙍..",   # 37
    "𝙆𝙄𝙎𝘼𝙉 𝙆𝙊 𝙆𝙃𝙊𝘿𝙉𝘼 𝙊𝙍",   # 38
    "𝙏𝙀𝙍𝙄𝙄𝙄 𝙈𝘼𝘼 𝙆𝘼𝘼 𝘽𝙅𝙎𝙊𝘿𝘼𝘼𝘼",   # 39
    "𝙎𝘼𝘽 𝘽𝙊𝙇𝙏𝙀 𝙈𝙐𝙅𝙃𝙆𝙊 𝙋𝘼𝙋𝘼 𝙆𝙔𝙊𝙐𝙉𝙆𝙄 𝙈𝙀𝙉𝙀 𝘽𝘼𝙉𝘼𝘿𝙄𝘼 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼𝙆𝙊 𝙋𝙍𝙀𝙂𝙉𝙀𝙉𝙏 🤣🤣",   # 40
    "𝐃𝐔𝐃𝐇 𝐇𝐈𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐄𝐍 𝐊𝐄 𝐔𝐏𝐑 𝐍𝐈𝐂𝐇𝐄 🆙🆒😙",   # 41
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘𝗜 𝗢𝗡𝗘𝗣𝗟𝗨𝗦 𝗞𝗔 𝗪𝗥𝗔𝗣 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 30𝗪 𝗛𝗜𝗚𝗛 𝗣𝗢𝗪𝗘𝗥 💥😂😎",   # 42
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐎 𝐂𝐇𝐎𝐃 𝐂𝐇𝐎𝐃𝐊𝐄 𝐕𝐈𝐃𝐄𝐎 𝐁𝐀𝐍𝐀𝐊𝐄 𝐗𝐍𝐗𝐗.𝐂𝐎𝐌 𝐏𝐄 𝐍𝐄𝐄𝐋𝐀𝐌 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐊𝐔𝐓𝐓𝐄 𝐊𝐄 𝐏𝐈𝐋𝐋𝐄 💦💋",   # 43
    "𝙆𝙄𝙎𝘼𝙉 𝙆𝙊 𝙆𝙃𝙊𝘿𝙉𝘼 𝙊𝙍",   # 44
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗝𝗔𝗥 𝗠𝗘 𝗖�_H𝗢𝗗 𝗗𝗔𝗟𝗔 🤣🤣💋",   # 45
    "𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍𝐀 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣",   # 46
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌𝗞𝗢 𝗞𝗛𝗨𝗟𝗘 𝗕𝗔𝗝𝗔𝗥 𝗠𝗘 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 🤣🤣💋",   # 47
    "𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗞𝗢𝗟𝗞𝗔𝗧𝗔 𝗩𝗔𝗔𝗟𝗘 𝗝𝗜𝗧𝗨 𝗕𝗛𝗔𝗜𝗬𝗔 𝗞𝗔 𝗟𝗨𝗡𝗗 𝗠𝗨𝗕𝗔𝗥𝗔𝗞 🤩🤩",   # 48
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗢 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",   # 49
    "𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓𝐇 𝐌𝐄 𝐌𝐄𝐑𝐀 𝐋𝐔𝐍𝐃 𝐊𝐀𝐀𝐋𝐀",   # 50

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

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_cmd(event):
        await event.edit("🏓 Pong! Userbot is active.")

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
        try:
            await event.delete()
        except Exception:
            pass
        await client.send_message(
            event.chat_id,
            f"🎯 Reply raid ACTIVATED!\n👤 Target: {target_id}\n📝 Type: DEFAULT",
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
            f"🎯 Reply raid DEACTIVATED for {target_id}!",
        )

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

        if is_restart:
            return True, "Success Userbot Restarted! Use .ping."
        return True, "Success Userbot Hosted! Use .ping to check."
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
        return True, "🔑 Enter OTP (e.g., 1 2 3 4 5): Hurry, expires in 1-2 min!"
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

    try:
        await info["client"].disconnect()
    except Exception:
        pass

    return True, "Account logout aur disconnect ho gaya hai."


async def restore_all_saved_sessions(api_id: int, api_hash: str):
    saved = load_all_sessions()
    for uid, session_str in saved.items():
        await start_client_from_session(uid, session_str, api_id, api_hash, persist=False)
