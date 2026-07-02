from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


def compress_image(image):
    img = Image.open(image)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Maximum size
    img.thumbnail((1920, 1920))

    output = BytesIO()

    img.save( output, format="WEBP", quality=80, optimize=True,)

    output.seek(0)

    return InMemoryUploadedFile( output, "ImageField", os.path.splitext(image.name)[0] + ".webp", "image/webp", output.getbuffer().nbytes, None,)