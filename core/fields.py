import os
from io import BytesIO
from PIL import Image
from django.db.models import ImageField
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

def compress_image(file, max_width=1200, max_height=1200, quality=80):
    if not file:
        return None
    try:
        # Open the image using Pillow
        file.seek(0)
        img = Image.open(file)
        
        # Resize if it exceeds maximum resolution
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
        # Save the image as WebP in-memory
        output = BytesIO()
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img.save(output, format='WEBP', quality=quality)
        else:
            img.convert('RGB').save(output, format='WEBP', quality=quality)
            
        output.seek(0)
        
        # Generate new filename with .webp extension
        original_name = file.name
        base_name, _ = os.path.splitext(os.path.basename(original_name))
        new_name = f"{base_name}.webp"
        
        return ContentFile(output.read(), name=new_name)
    except Exception as e:
        # If compression fails, fallback to the original file to ensure reliability
        return file

class CompressedImageField(ImageField):
    def __init__(self, *args, max_width=1200, max_height=1200, quality=80, **kwargs):
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality
        super().__init__(*args, **kwargs)
        
    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not file._committed and hasattr(file, 'file') and isinstance(file.file, UploadedFile):
            compressed = compress_image(file, self.max_width, self.max_height, self.quality)
            if compressed:
                file.file = compressed
                file.name = compressed.name
        return super().pre_save(model_instance, add)
