# main.py
# Lancer l'environnement : source myenv/Scripts/activate
# image docker : docker pull paddlepaddle/paddle:3.0.0-gpu-cuda12.6-cudnn9.5-trt10.5

import os
import json
import sys
import time

# Importe les fonctions des modules créés
from image_processing.ocr_utils import preprocess_image, extract_text_from_image, extract_text_from_pdf
from text_interpretation.analyzer import interpret_text, debug_structure_analysis

# S'assurer de l'encodage pour la console si besoin
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)


def process_file(file_path):
    start_time = time.time()  # Enregistre le temps de départ
    extracted_text = ""
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        processed_image_path = preprocess_image(file_path)
        if processed_image_path:
            extracted_text = extract_text_from_image(processed_image_path)
            os.remove(processed_image_path)  # Nettoie le fichier temporaire
    elif file_path.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        print("Format de fichier non supporté.")
        return json.dumps({
            "amount": None, "currency": "eur", "location_name": "Inconnu",
            "category": "Autre", "date": None, "hour": None, "country": "france"
        }, indent=4)

    print(f"Texte extrait (brut) : \n{extracted_text}\n")
    debug_structure_analysis(extracted_text)  # Debug de la structure

    interpreted_data = interpret_text(extracted_text)
    print(f"Informations de dépense extraites : \n{interpreted_data}")

    end_time = time.time()  # Enregistre le temps de fin
    execution_time = end_time - start_time  # Calcule la durée
    print(f"--- Temps d'exécution total : {execution_time:.2f} secondes ---")  # Affiche le temps formaté

    return interpreted_data


# --- Chemin vers le fichier à traiter ---
# file_path = 'data/facture.pdf' -- TODO - ajuster le script pour les factures
# file_path = 'data/ticket.JPG'
file_path = 'data/ticket_coquillettes.jpg'

if __name__ == "__main__":
    process_file(file_path)