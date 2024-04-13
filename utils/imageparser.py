import pytesseract
from PIL import Image
import asyncio
import functools 
from PIL import Image
import hashlib
from bot import logging

def reader(url):
    try:
        return pytesseract.image_to_string(lang="rus+eng", image=Image.open(url), config="--oem 3")
    except Exception as e:
        logging.exception(e)
    # return easyocr.Reader(["ru", "en"]).readtext(url, detail=0, paragraph=True, text_threshold=0.8)

async def get(url):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, functools.partial(reader, url=url))
        if not result:
            return " "
        result = result.replace("\n", " ")
        return result
    except Exception as e:
        logging.exception(e)

async def getHash(src):
    with open(src, 'rb') as f:
        image_data = f.read()
        hash = hashlib.md5(image_data).hexdigest()
        return hash[:15]
