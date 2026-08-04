# backend/test_quality.py
import cv2
import numpy as np

def test_quality(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Blur detection
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(f"Blur score: {laplacian_var}")
    
    # Brightness
    brightness = float(np.mean(gray))
    print(f"Brightness: {brightness}")
    
    # Contrast
    contrast = float(np.std(gray))
    print(f"Contrast: {contrast}")
    
    # Decision
    if laplacian_var < 100:
        print("❌ BLURRY")
    else:
        print("✅ SHARP")

if __name__ == "__main__":
    test_quality("path/to/your/blurry_image.jpg")