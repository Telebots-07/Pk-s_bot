from PIL import Image, ImageDraw, ImageFont
from utils.logger import log_error

async def add_banner(file_path: str, text: str):
    """Add banner text to images."""
    try:
        img = Image.open(file_path)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), text, font=font, fill=(255, 255, 255))
        img.save(file_path)
        return file_path
    except Exception as e:
        log_error(f"Banner error: {str(e)}")
        return None
