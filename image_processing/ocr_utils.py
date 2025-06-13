# image_processing/ocr_utils.py

import cv2
import os
import numpy as np
import subprocess
import tempfile
import json
from pdf2image import convert_from_path

# Configuration Docker
DOCKER_IMAGE = "paddlepaddle/paddle:2.4.2-gpu-cuda11.2-cudnn8"
DOCKER_IMAGE_CPU = "paddlepaddle/paddle:2.4.2"
CONTAINER_NAME = "paddle_ocr_service"


def check_docker():
    """Vérifier si Docker est disponible"""
    try:
        result = subprocess.run(['docker', '--version'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker disponible: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker non disponible")
            return False
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")
        return False


def setup_docker_container():
    """Configurer le container PaddleOCR"""
    print("🐳 Configuration du container PaddleOCR...")

    try:
        # Vérifier si le container existe déjà
        result = subprocess.run(['docker', 'ps', '-a', '--filter', f'name={CONTAINER_NAME}'],
                                capture_output=True, text=True)

        if CONTAINER_NAME in result.stdout:
            print("♻️  Container existant trouvé, redémarrage...")
            subprocess.run(['docker', 'start', CONTAINER_NAME], check=True)
        else:
            print("🚀 Création d'un nouveau container...")

            # Essayer GPU d'abord, puis CPU si échec
            try:
                cmd = [
                    'docker', 'run', '-d', '--gpus', 'all',
                    '--name', CONTAINER_NAME,
                    '-v', f'{os.getcwd()}:/workspace',
                    DOCKER_IMAGE,
                    'sleep', 'infinity'
                ]
                subprocess.run(cmd, check=True)
                print("✅ Container GPU créé avec succès")
            except subprocess.CalledProcessError:
                print("⚠️  GPU non disponible, utilisation CPU...")
                cmd = [
                    'docker', 'run', '-d',
                    '--name', CONTAINER_NAME,
                    '-v', f'{os.getcwd()}:/workspace',
                    DOCKER_IMAGE_CPU,
                    'sleep', 'infinity'
                ]
                subprocess.run(cmd, check=True)
                print("✅ Container CPU créé avec succès")

        # Installer PaddleOCR dans le container
        print("📦 Installation de PaddleOCR dans le container...")
        install_cmd = ['docker', 'exec', CONTAINER_NAME, 'pip', 'install', 'paddleocr']
        subprocess.run(install_cmd, check=True)

        # Test d'installation
        test_cmd = ['docker', 'exec', CONTAINER_NAME, 'python', '-c',
                    'from paddleocr import PaddleOCR; print("PaddleOCR OK")']
        result = subprocess.run(test_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ PaddleOCR installé et fonctionnel dans Docker")
            return True
        else:
            print(f"❌ Erreur installation PaddleOCR: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur configuration Docker: {e}")
        return False


def docker_ocr_extract(image_path):
    """Extraire le texte via Docker PaddleOCR"""
    if not os.path.exists(image_path):
        return "Fichier image non trouvé"

    # Copier l'image dans le répertoire de travail (accessible par Docker)
    temp_dir = os.path.join(os.getcwd(), 'temp_docker')
    os.makedirs(temp_dir, exist_ok=True)

    temp_image_path = os.path.join(temp_dir, 'image_to_process.jpg')

    # Copier l'image
    import shutil
    shutil.copy2(image_path, temp_image_path)

    # Créer le script Python pour l'OCR
    ocr_script = f'''
import json
from paddleocr import PaddleOCR

try:
    # Initialiser PaddleOCR avec GPU si disponible
    ocr = PaddleOCR(use_angle_cls=True, lang='fr', use_gpu=True, show_log=False)

    # Traiter l'image
    image_path = '/workspace/temp_docker/image_to_process.jpg'
    results = ocr.ocr(image_path, cls=True)

    # Extraire le texte
    extracted_data = []
    if results and results[0]:
        for line in results[0]:
            bbox, (text, confidence) = line
            extracted_data.append({{
                "text": text,
                "confidence": confidence
            }})

    # Sortie JSON
    output = {{
        "success": True,
        "data": extracted_data,
        "total_chars": sum(len(item["text"]) for item in extracted_data)
    }}

    print(json.dumps(output, ensure_ascii=False))

except Exception as e:
    # En cas d'erreur, essayer CPU
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='fr', use_gpu=False, show_log=False)
        results = ocr.ocr('/workspace/temp_docker/image_to_process.jpg', cls=True)

        extracted_data = []
        if results and results[0]:
            for line in results[0]:
                bbox, (text, confidence) = line
                extracted_data.append({{
                    "text": text,
                    "confidence": confidence
                }})

        output = {{
            "success": True,
            "data": extracted_data,
            "mode": "CPU_fallback",
            "total_chars": sum(len(item["text"]) for item in extracted_data)
        }}

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e2:
        error_output = {{
            "success": False,
            "error": str(e2)
        }}
        print(json.dumps(error_output, ensure_ascii=False))
'''

    # Sauvegarder le script
    script_path = os.path.join(temp_dir, 'ocr_script.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(ocr_script)

    try:
        # Exécuter le script dans Docker
        cmd = ['docker', 'exec', CONTAINER_NAME, 'python', '/workspace/temp_docker/ocr_script.py']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            # Parser le résultat JSON
            try:
                data = json.loads(result.stdout.strip())
                if data.get('success'):
                    print(f"=== RÉSULTATS DOCKER PADDLEOCR ===")
                    texts = []
                    for i, item in enumerate(data['data']):
                        print(f"{i + 1}. '{item['text']}' (confiance: {item['confidence']:.3f})")
                        if item['confidence'] > 0.3:
                            texts.append(item['text'])

                    final_text = ' '.join(texts)
                    print(f"✅ Texte final ({data['total_chars']} caractères): {final_text}")
                    return final_text
                else:
                    print(f"❌ Erreur OCR: {data.get('error')}")
                    return ""
            except json.JSONDecodeError:
                print(f"❌ Erreur parsing JSON: {result.stdout}")
                return ""
        else:
            print(f"❌ Erreur exécution Docker: {result.stderr}")
            return ""

    except subprocess.TimeoutExpired:
        print("⏱️  Timeout - OCR trop long")
        return ""
    except Exception as e:
        print(f"❌ Erreur Docker OCR: {e}")
        return ""
    finally:
        # Nettoyer les fichiers temporaires
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(script_path):
            os.remove(script_path)


def preprocess_image(image_path):
    """Preprocessing basique - Docker PaddleOCR gère bien les images brutes"""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur : Impossible de lire l'image {image_path}")
        return None

    print(f"Image originale : {image.shape[1]}x{image.shape[0]}")

    # Preprocessing minimal car PaddleOCR est robuste
    if image.shape[1] < 800:
        print("Image petite, agrandissement x2")
        image = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Sauvegarde
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        processed_path = tmp_file.name
    cv2.imwrite(processed_path, image)

    return processed_path


def extract_text_from_image(image_path):
    """Point d'entrée principal - utilise Docker PaddleOCR"""
    if image_path is None:
        return ""

    # Vérifier Docker
    if not check_docker():
        return "Docker non disponible"

    # Configurer le container si nécessaire
    if not setup_docker_container():
        return "Erreur configuration Docker"

    # Extraire le texte
    return docker_ocr_extract(image_path)


def extract_text_from_pdf(pdf_path):
    """Extraction PDF via Docker"""
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        if not images:
            return ""

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_path = tmp_file.name

        images[0].save(temp_path, 'JPEG', quality=95)
        text = extract_text_from_image(temp_path)
        os.unlink(temp_path)

        return text
    except Exception as e:
        print(f"Erreur PDF: {e}")
        return ""


def cleanup_docker():
    """Nettoyer le container Docker (optionnel)"""
    try:
        subprocess.run(['docker', 'stop', CONTAINER_NAME], check=True)
        subprocess.run(['docker', 'rm', CONTAINER_NAME], check=True)
        print("🧹 Container Docker nettoyé")
    except:
        pass


if __name__ == "__main__":
    # Test de l'installation
    if check_docker():
        if setup_docker_container():
            print("🎉 Docker PaddleOCR prêt à utiliser!")
        else:
            print("❌ Échec configuration Docker")
    else:
        print("❌ Docker non disponible")
