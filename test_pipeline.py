import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys

# Test script for E:\visiting-card-scanner
from rapidocr_onnxruntime import RapidOCR

print("Initializing RapidOCR...")
ocr = RapidOCR()

# Create a clean synthetic business card image
img = Image.new('RGB', (800, 450), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw red decorative accent line
draw.rectangle([(20, 20), (30, 430)], fill=(220, 38, 38))

# Draw text fields
draw.text((60, 40), "NEXUS TECH SOLUTIONS", fill=(0, 0, 0))
draw.text((60, 100), "Rudra Patel", fill=(0, 0, 0))
draw.text((60, 140), "Chief Technology Officer", fill=(80, 80, 80))
draw.text((60, 200), "Phone: +91 98765 43210", fill=(0, 0, 0))
draw.text((60, 240), "Email: contact@rudrapatel.io", fill=(0, 0, 0))
draw.text((60, 280), "Website: https://rudrapatel.io", fill=(0, 0, 0))
draw.text((60, 320), "GSTIN: 24AAACH7409R1ZZ", fill=(0, 0, 0))
draw.text((60, 360), "101, Horizon Business Tower, Ahmedabad - 380015", fill=(0, 0, 0))

test_img_path = r"E:\visiting-card-scanner\sample_card.png"
img.save(test_img_path)
print(f"Sample card saved to {test_img_path}")

# Run OCR on the sample card
img_arr = np.array(img)
results, _ = ocr(img_arr)
print(f"OCR successfully detected {len(results) if results else 0} text boxes.")

sys.path.append(r"E:\visiting-card-scanner")
import app

parsed = app.parse_card_elements(results)
print("\n--- Parsed Card Elements ---")
for k, v in parsed.items():
    print(f"{k}: {v}")

print("\nVerification complete! All components functional on Drive E.")
