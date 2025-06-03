# text_interpretation/text_structure.py

import re
from typing import List, Dict, Tuple


def reconstruct_ticket_structure(raw_text: str) -> Dict:
    """
    Reconstitue la structure logique d'un ticket à partir du texte brut OCR
    """
    # Nettoyage initial
    text = raw_text.strip()

    # Tentative de reconstruction des lignes basée sur des indices
    lines = smart_line_splitting(text)

    # Analyse de la structure
    structure = {
        'header': [],  # Lignes 1-3 : nom du commerce, adresse
        'body': [],  # Lignes du milieu : articles, détails
        'footer': [],  # Lignes de fin : totaux, informations légales
        'metadata': []  # Date, heure, numéro de ticket
    }

    # Classification des lignes
    classify_lines(lines, structure)

    return structure


def smart_line_splitting(text: str) -> List[str]:
    """
    Divise intelligemment le texte en lignes logiques
    """
    # Première approche : découper sur les \n existants
    lines = text.split('\n')

    # Si pas assez de lignes, essayer d'autres méthodes
    if len(lines) < 5:
        lines = advanced_line_reconstruction(text)

    # Nettoyer et filtrer les lignes vides
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 1:  # Éviter les lignes avec juste un caractère
            cleaned_lines.append(line)

    return cleaned_lines


def advanced_line_reconstruction(text: str) -> List[str]:
    """
    Reconstruction avancée des lignes quand l'OCR n'a pas détecté les retours à la ligne
    """
    lines = []

    # Méthode 1 : Découper sur les patterns de fin de ligne typiques
    patterns = [
        r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',  # Dates
        r'(\d{1,2}[h:]\d{2})',  # Heures
        r'(\d+[.,]\d{2}\s*€?)',  # Montants
        r'(TOTAL|Total|SOUS-TOTAL|TVA)',  # Mots-clés de structure
        r'([A-Z]{3,}\s+[A-Z]{3,})',  # Mots en majuscules (enseignes)
    ]

    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            potential_line = text[start:end].strip()
            if potential_line and len(potential_line) > 2:
                lines.append(potential_line)

    # Méthode 2 : Découper sur les espaces multiples (colonnes)
    if not lines:
        lines = re.split(r'\s{3,}', text)

    # Méthode 3 : Découper sur les changements de casse ou de type de contenu
    if not lines:
        lines = smart_content_splitting(text)

    return lines if lines else [text]  # Fallback


def smart_content_splitting(text: str) -> List[str]:
    """
    Découpage basé sur les changements de contenu (adresse -> articles -> totaux)
    """
    lines = []
    current_line = ""

    words = text.split()

    for i, word in enumerate(words):
        current_line += word + " "

        # Indicateurs de fin de ligne/section
        if (
                # Fin d'adresse (code postal + ville)
                re.match(r'\d{5}', word) and i < len(words) - 1 and words[i + 1].istitle() or
                # Après un prix
                re.match(r'\d+[.,]\d{2}€?$', word) or
                # Après une date/heure
                re.match(r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}$', word) or
                re.match(r'\d{1,2}[h:]\d{2}$', word) or
                # Mots-clés de structure
                word.upper() in ['TOTAL', 'SUBTOTAL', 'TVA', 'MERCI', 'TICKET', 'CAISSE']
        ):
            lines.append(current_line.strip())
            current_line = ""

    if current_line.strip():
        lines.append(current_line.strip())

    return lines


def classify_lines(lines: List[str], structure: Dict):
    """
    Classifie chaque ligne selon sa position logique dans le ticket
    """
    total_lines = len(lines)

    for i, line in enumerate(lines):
        line_info = {
            'text': line,
            'position': i + 1,
            'relative_position': (i + 1) / total_lines,  # Position relative (0-1)
            'type': analyze_line_type(line)
        }

        # Classification basée sur la position et le contenu
        if i < 3:  # Premières lignes = header probable
            structure['header'].append(line_info)
        elif line_info['type'] in ['total', 'payment', 'legal']:
            structure['footer'].append(line_info)
        elif line_info['type'] in ['date', 'time', 'ticket_number']:
            structure['metadata'].append(line_info)
        else:
            structure['body'].append(line_info)


def analyze_line_type(line: str) -> str:
    """
    Analyse le type de contenu d'une ligne
    """
    line_lower = line.lower()

    # Patterns de classification
    if re.search(r'total|somme|montant.*total', line_lower):
        return 'total'
    elif re.search(r'tva|tax', line_lower):
        return 'tax'
    elif re.search(r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}', line):
        return 'date'
    elif re.search(r'\d{1,2}[h:]\d{2}', line):
        return 'time'
    elif re.search(r'ticket|facture|recu.*n[°o]?\s*\d+', line_lower):
        return 'ticket_number'
    elif re.search(r'siret|rcs|tva.*n[°o]', line_lower):
        return 'legal'
    elif re.search(r'carte|espece|cb|cheque', line_lower):
        return 'payment'
    elif re.search(r'\d+[.,]\d{2}', line):
        return 'price'
    elif re.search(r'^[A-Z\s]{5,}$', line):  # Ligne en majuscules
        return 'merchant_name'
    elif re.search(r'\d+.*rue|avenue|boulevard|place', line_lower):
        return 'address'
    else:
        return 'item'


def get_prioritized_merchant_names(structure: Dict) -> List[Tuple[str, float]]:
    """
    Extrait et priorise les noms de commerces potentiels
    """
    candidates = []

    # Priorité 1 : Header avec type merchant_name
    for line_info in structure['header']:
        if line_info['type'] == 'merchant_name':
            candidates.append((line_info['text'], 100))

    # Priorité 2 : Première ligne du header (même si pas identifiée comme merchant_name)
    if structure['header']:
        first_line = structure['header'][0]['text']
        # Nettoyer et évaluer
        clean_name = clean_merchant_name(first_line)
        if clean_name and len(clean_name) > 2:
            candidates.append((clean_name, 80))

    # Priorité 3 : Lignes avec majuscules dans les premières lignes
    for line_info in structure['header'][:3]:
        words = line_info['text'].split()
        capitalized_words = [w for w in words if w.isupper() and len(w) > 2]
        if capitalized_words:
            merchant_candidate = ' '.join(capitalized_words[:2])
            candidates.append((merchant_candidate, 60))

    # Déduplication et tri
    unique_candidates = {}
    for name, score in candidates:
        if name not in unique_candidates or unique_candidates[name] < score:
            unique_candidates[name] = score

    return sorted(unique_candidates.items(), key=lambda x: x[1], reverse=True)


def clean_merchant_name(raw_name: str) -> str:
    """
    Nettoie un nom de commerce brut
    """
    # Supprimer les mots parasites
    noise_words = {
        'ticket', 'facture', 'recu', 'caisse', 'n°', 'numero',
        'tel', 'telephone', 'fax', 'email', 'www', 'http',
        'siret', 'rcs', 'sarl', 'sas', 'eurl', 'tva'
    }

    words = raw_name.split()
    clean_words = []

    for word in words:
        word_clean = re.sub(r'[^\w]', '', word.lower())
        if (word_clean not in noise_words and
                len(word_clean) > 2 and
                not word_clean.isdigit()):
            clean_words.append(word)

    return ' '.join(clean_words[:3])  # Max 3 mots


# Fonction d'intégration à ton analyzer.py existant
def extract_location_name_structured(text: str, detected_category: str = "Autre") -> Tuple[str, str]:
    """
    Version améliorée utilisant l'analyse structurelle
    """
    from text_interpretation.constants import KNOWN_COMMERCES

    # 1. Vérification des enseignes connues (priorité absolue)
    clean_text_lower = text.lower()
    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in clean_text_lower:
            return known_name.title(), category

    # 2. Analyse structurelle
    structure = reconstruct_ticket_structure(text)
    merchant_candidates = get_prioritized_merchant_names(structure)

    if merchant_candidates:
        best_name, confidence = merchant_candidates[0]
        if confidence > 50:
            return best_name.title(), detected_category

    # 3. Fallback vers l'ancienne méthode si échec
    return "Inconnu", detected_category
