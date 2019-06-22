"""
OCR engine binding to tesseract engine.

tesseract engine: https://github.com/tesseract-ocr/tesseract
tesseract language data: https://github.com/tesseract-ocr/tesseract/wiki/Data-Files#data-files-for-version-400-november-29-2016
tesserocr (python wrapper of tesseract): https://github.com/sirfz/tesserocr
"""


import tesserocr
from PIL import Image

image = Image.open('./pics/screen.png')
print(tesserocr.image_to_text(image))
print(tesserocr.get_languages())


# or ...
from tesserocr import PyTessBaseAPI

images = ['./pics/screen.png']

# you can set language here, but you need to install specify language data firstly.
with PyTessBaseAPI(lang='eng') as api:
    for img in images:
        api.SetImageFile(img)
        print(api.GetUTF8Text())
