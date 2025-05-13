from PIL import Image
import moviepy.editor as mp
from utils.logger import log_error

async def add_cover_image(file_path: str, context):
    """Add cover image to files."""
    db = context.bot_data.get("firestore_db")
    settings = db.collection("settings").document("bot_config").get().to_dict()
    cover_enabled = settings.get("cover_enabled", False)

    if not cover_enabled:
        return None

    try:
        if file_path.endswith((".jpg", ".png")):
            img = Image.open(file_path)
            # Add cover logic (e.g., watermark)
            img.save(file_path)
            return file_path
        elif file_path.endswith((".mp4", ".avi")):
            clip = mp.VideoFileClip(file_path)
            # Add cover frame logic
            clip.write(0, 1).save_frame(file_path.replace(".mp4", "_cover.jpg"))
            return file_path.replace(".mp4", "_cover.jpg")
        return None
    except Exception as e:
        log_error(f"Cover image error: {str(e)}")
        return None
