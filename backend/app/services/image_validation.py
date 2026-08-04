from PIL import Image, ImageFilter
import io
import numpy as np

class ImageQualityValidator:
    def __init__(self):
        self.min_width = 224
        self.min_height = 224

    def validate(self, image_bytes: bytes) -> dict:
        issues = []
        quality_score = 100
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            if width < self.min_width or height < self.min_height:
                issues.append(f"Resolution too low. Minimum: {self.min_width}x{self.min_height}")
                quality_score -= 30
            # No blur detection, but we can check if image is mostly uniform
            if len(set(img.getdata())) < 10:
                issues.append("Image appears to be blank or has no visible lesion.")
                quality_score -= 40
            return {
                'is_valid': len(issues) == 0 and quality_score >= 50,
                'issues': issues,
                'quality_score': max(0, quality_score),
                'details': {'width': width, 'height': height}
            }
        except Exception as e:
            return {
                'is_valid': False,
                'issues': [f'Validation error: {str(e)}'],
                'quality_score': 0,
                'details': {}
            }