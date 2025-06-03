# image_processing/ocr_utils.py

import cv2
import os
import easyocr
from pdf2image import convert_from_path

def preprocess_image(image_path):
    # ... (ton code actuel pour preprocess_image) ...
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur : Impossible de lire l'image {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    equalized = cv2.equalizeHist(thresh)

    processed_image_path = 'preprocessed_image.jpg' # Pense à rendre ce chemin plus dynamique ou temporaire
    cv2.imwrite(processed_image_path, equalized)

    return processed_image_path

def extract_text_from_image(image_path):
    # ... (ton code actuel pour extract_text_from_image) ...
    if image_path is None:
        return ""
    reader = easyocr.Reader(['fr'])
    results = reader.readtext(image_path)
    text = ' '.join([detection[1] for detection in results])
    return text

def extract_text_from_pdf(pdf_path):
    # ... (ton code actuel pour extract_text_from_pdf) ...
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    if not images:
        return ""
    image_path = "temp_pdf_page.jpg" # Pense à rendre ce chemin plus dynamique ou temporaire
    images[0].save(image_path, 'JPEG')
    text = extract_text_from_image(image_path)
    os.remove(image_path)
    return text