# ============================================================
#   Download Engine - yt-dlp
# ============================================================

import os
import asyncio
import yt_dlp


async def download_video(url: str, output_dir: str = "./downloads") -> dict:
    """
    Downloads video from YouTube / Facebook / Instagram.
    Returns: {'success': bool, 'file_path': str, 'title': str, 'error': str}
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format":           "best[ext=mp4]/best",          # Best MP4 quality
        "outtmpl":          f"{output_dir}/%(id)s.%(ext)s",
        "noplaylist":        True,
        "quiet":             True,
        "no_warnings":       True,
        "merge_output_format": "mp4",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        # Instagram & Facebook cookies (optional - for private/reels)
        # "cookiefile": "cookies.txt",
    }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            # Ensure .mp4 extension
            if not file_path.endswith(".mp4"):
                file_path = file_path.rsplit(".", 1)[0] + ".mp4"
            return {
                "success":   True,
                "file_path": file_path,
                "title":     info.get("title", "Video"),
                "duration":  info.get("duration", 0),
                "error":     None
            }

    try:
        result = await loop.run_in_executor(None, _download)
        return result
    except yt_dlp.utils.DownloadError as e:
        return {"success": False, "file_path": None, "title": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "file_path": None, "title": None, "error": str(e)}


def delete_file(file_path: str):
    """Safely delete a file from disk."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"[Delete Error]: {e}")
