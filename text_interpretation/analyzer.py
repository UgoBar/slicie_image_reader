# text_interpretation/analyzer.py (version améliorée)
import re
import json
from .constants import CATEGORIES, KNOWN_COMMERCES
from .parser import clean_text, find_amount, find_date, find_hour
from .text_structure import extract_location_name_structured, reconstruct_ticket_structure

def calculate_name_confidence(name, category):
    """Calcule un score de confiance pour un nom de commerce"""
    confidence = 50  # Score de base

    # Bonus pour longueur appropriée
    if 3 <= len(name) <= 20:
        confidence += 10

    # Bonus si le nom contient des mots liés à la catégorie
    name_lower = name.lower()
    category_keywords = {
        'Restaurant': ['restaurant', 'cafe', 'brasserie', 'pizza', 'burger'],
        'Courses': ['market', 'super', 'hyper', 'bio', 'fresh'],
        'Sport': ['sport', 'gym', 'fitness'],
        'Bar': ['bar', 'pub', 'lounge']
    }

    if category in category_keywords:
        for keyword in category_keywords[category]:
            if keyword in name_lower:
                confidence += 20
                break

    # Malus pour certains patterns suspects
    if re.match(r'^\d+$', name) or len(name) < 3:
        confidence -= 30

    return confidence


def extract_contextual_info_from_structure(structure):
    """
    Extrait des informations contextuelles de la structure du ticket
    """
    context_info = {
        'has_multiple_items': len([line for line in structure['body'] if line['type'] == 'item']) > 1,
        'has_alcohol_keywords': False,
        'has_food_keywords': False,
        'payment_method': None,
        'location_indicators': []
    }

    # Analyser tout le contenu pour des indices contextuels
    all_text = ' '.join([line['text'] for section in structure.values() for line in section])
    all_text_lower = all_text.lower()

    # Détection d'indices alimentaires
    food_keywords = ['pain', 'sandwich', 'menu', 'plat', 'boisson', 'eau', 'cafe', 'the']
    context_info['has_food_keywords'] = any(keyword in all_text_lower for keyword in food_keywords)

    # Détection d'alcool
    alcohol_keywords = ['biere', 'vin', 'alcool', 'whisky', 'vodka', 'cocktail']
    context_info['has_alcohol_keywords'] = any(keyword in all_text_lower for keyword in alcohol_keywords)

    # Méthode de paiement
    payment_keywords = {'carte': 'card', 'espece': 'cash', 'cheque': 'check', 'cb': 'card'}
    for keyword, method in payment_keywords.items():
        if keyword in all_text_lower:
            context_info['payment_method'] = method
            break

    return context_info


def enhanced_categorization(text, amount=None, structure=None):
    """
    Catégorisation améliorée utilisant la structure et le contexte
    """
    cleaned_text = clean_text(text)
    detected_category = "Autre"

    # 1. Vérifier les enseignes connues (priorité absolue)
    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in cleaned_text:
            return category

    # 2. Analyse contextuelle si structure disponible
    if structure:
        context = extract_contextual_info_from_structure(structure)

        # Logique contextuelle avancée
        if context['has_alcohol_keywords']:
            detected_category = "Bar"
        elif context['has_food_keywords']:
            if amount and amount > 30:
                detected_category = "Courses"
            elif context['has_multiple_items']:
                detected_category = "Restaurant"
            else:
                detected_category = "Restaurant"

    # 3. Scoring par mots-clés avec pondération (méthode existante)
    category_scores = {}
    for cat, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword in cleaned_text:
                # Pondération selon la position dans la structure
                base_weight = 1
                if structure:
                    # Bonus si le mot-clé apparaît dans le header (nom du commerce)
                    header_text = ' '.join([line['text'] for line in structure['header']]).lower()
                    if keyword in header_text:
                        base_weight = 3

                score += base_weight

        if score > 0:
            category_scores[cat] = score

    # Prendre la meilleure catégorie si score significatif
    if category_scores and max(category_scores.values()) > 1:
        detected_category = max(category_scores, key=category_scores.get)

    # 4. Heuristiques de fallback basées sur le montant
    if detected_category == "Autre" and amount is not None:
        detected_category = categorize_by_amount_heuristic(amount, cleaned_text)

    return detected_category


def categorize_by_amount_heuristic(amount, text):
    """Heuristiques de catégorisation basées sur le montant"""
    # Indices contextuels dans le texte
    food_indicators = any(word in text for word in
                          ["pain", "boisson", "cafe", "sandwich", "menu", "plat"])
    transport_indicators = any(word in text for word in
                               ["essence", "carburant", "station", "parking"])

    if amount <= 5:
        return "Bar" if any(word in text for word in ["boisson", "cafe"]) else "Autre"
    elif amount <= 15:
        return "Restaurant" if food_indicators else "Bar"
    elif amount <= 50:
        return "Restaurant" if food_indicators else "Shopping"
    elif amount <= 100:
        if transport_indicators:
            return "Trajet"
        elif food_indicators:
            return "Courses"
        else:
            return "Shopping"
    else:
        return "Courses" if food_indicators else "Shopping"


def find_category_and_location_enhanced(text, amount=None):
    """
    Version améliorée utilisant l'analyse structurelle
    """
    # Reconstituer la structure du ticket
    structure = reconstruct_ticket_structure(text)

    # Catégorisation améliorée
    detected_category = enhanced_categorization(text, amount, structure)

    # Extraction du nom du lieu avec l'analyse structurelle
    location_name, final_category = extract_location_name_structured(text, detected_category)

    return final_category, location_name


def interpret_text(extracted_text):
    """Version améliorée de l'interprétation avec analyse structurelle"""
    cleaned_text = clean_text(extracted_text)

    result = {
        "amount": None, "currency": "eur", "location_name": "Inconnu",
        "category": "Autre", "date": None, "hour": None, "country": "france"
    }

    # Extraction du montant
    result["amount"] = find_amount(extracted_text)

    # Catégorisation et extraction du lieu améliorées
    result["category"], result["location_name"] = find_category_and_location_enhanced(
        extracted_text, result["amount"]
    )

    # Extraction date/heure (inchangées)
    result["date"] = find_date(extracted_text)
    result["hour"] = find_hour(extracted_text)

    return json.dumps(result, indent=4)


def debug_structure_analysis(extracted_text):
    """
    Fonction de debug pour visualiser l'analyse structurelle
    """
    structure = reconstruct_ticket_structure(extracted_text)

    print("=== ANALYSE STRUCTURELLE ===")
    for section_name, lines in structure.items():
        if lines:
            print(f"\n{section_name.upper()}:")
            for line_info in lines:
                print(f"  - {line_info['text']} (type: {line_info['type']})")

    # Test de l'extraction du nom
    category, location = find_category_and_location_enhanced(extracted_text)
    print(f"\nRÉSULTAT: {location} - {category}")
