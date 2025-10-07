import io, os
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image_file(file, *, max_size=(1600, 1600), format="WEBP", quality=80):
    """
    Returns a new InMemoryUploadedFile with resized/compressed image.
    - max_size: longest side limit
    - format: "WEBP" keeps great quality & small size (supports alpha)
    """
    file.seek(0)
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)  # honor EXIF orientation
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    # Resize in place (keeps aspect ratio)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Save to buffer
    buf = io.BytesIO()
    save_kwargs = {"format": format, "quality": quality}
    # webp can optimize; pillow ignores if not applicable
    save_kwargs["method"] = 6  # best webp compression
    img.save(buf, **save_kwargs)
    buf.seek(0)

    # Make a new name with .webp
    base, _ext = os.path.splitext(getattr(file, "name", "upload"))
    new_name = f"{base}.webp"
    # Build a Django UploadedFile
    return InMemoryUploadedFile(
        file=buf,
        field_name=None,
        name=new_name,
        content_type="image/webp",
        size=buf.getbuffer().nbytes,
        charset=None,
    )
