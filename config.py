import os
from dotenv import load_dotenv

load_dotenv()


def _parse_int(val: str, default: int = 0) -> int:
    try:
        return int((val or "").strip())
    except ValueError:
        return default


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
API_ID: int = _parse_int(os.getenv("API_ID", "0"), 0)
API_HASH: str = os.getenv("API_HASH", "").strip()
OWNER_ID: int = _parse_int(os.getenv("OWNER_ID", "0"), 0)

DEFAULT_BANNER_URL: str = os.getenv("START_BANNER_URL", "").strip()
DEFAULT_SUPPORT_GROUP_URL: str = os.getenv("SUPPORT_GROUP_URL", "https://t.me/").strip()
DEFAULT_FORCE_JOIN_CHAT_ID: int = _parse_int(os.getenv("FORCE_JOIN_CHAT_ID", "0"), 0)
DEFAULT_FORCE_JOIN_LINK: str = os.getenv("FORCE_JOIN_LINK", "").strip()
CRAFTED_BY: str = os.getenv("CRAFTED_BY", "•𝄞⃝𝀈 Ｓ⋏ ᰻⃪᱂ །༨ ⋏ ᰻⃪᱂ ꯭꯭᪳𝆺𝅥⍣❘꯭").strip()
MONGO_URI: str = os.getenv("MONGO_URI", "").strip()
