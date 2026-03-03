# ============================================================
#   Helper Functions - Token & Link Shortener
# ============================================================

import uuid
import aiohttp
from config import GPLINKS_API_KEY, BOT_USERNAME
from database import save_token


def generate_token(user_id: int) -> str:
    """Generate a unique token for user."""
    token = uuid.uuid4().hex[:12].upper()  # e.g. "A3F9B2C1D4E7"
    save_token(token, user_id)
    return token


async def shorten_link(long_url: str) -> str:
    """Shorten a URL using GPLinks API."""
    api_url = f"https://gplinks.co/api?api={GPLINKS_API_KEY}&url={long_url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data.get("status") == "success":
                    return data["shortenedUrl"]
    except Exception as e:
        print(f"[GPLinks Error]: {e}")
    return long_url  # fallback: original link


async def generate_verify_link(user_id: int) -> str:
    """
    1. Generate a unique token
    2. Create the verify deep-link
    3. Shorten it via GPLinks (user must view ad)
    4. Return shortened URL
    """
    token = generate_token(user_id)
    verify_url = f"https://t.me/{BOT_USERNAME}?start=verify_{token}"
    short_url  = await shorten_link(verify_url)
    return short_url
