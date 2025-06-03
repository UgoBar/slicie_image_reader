# text_interpretation/analyzer.py

import re
import json
from datetime import datetime  # Assure-toi que datetime est importé si tu l'utilises ailleurs
from fuzzywuzzy import fuzz  # <-- Nouvelle importation

from .constants import CATEGORIES, KNOWN_COMMERCES
from .parser import clean_text, find_amount, find_date, find_hour
from .text_structure import extract_location_name_structured, reconstruct_ticket_structure


# --- Fonctions existantes ---
def calculate_name_confidence(name, category):
    """Calcule un score de confiance pour un nom de commerce"""
    confidence = 50  # Score de base

    # Bonus pour longueur appropriée
    if 3 <= len(name) <= 20:
        confidence += 10
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
    if re.match(r'^\d+$', name) or len(name) < 3:
        confidence -= 30
    return confidence


def extract_contextual_info_from_structure(structure):
    # ... (ton code existant) ...
    context_info = {
        'has_multiple_items': len([line for line in structure['body'] if line['type'] == 'item']) > 1,
        'has_alcohol_keywords': False,
        'has_food_keywords': False,
        'payment_method': None,
        'location_indicators': []
    }
    all_text = ' '.join([line['text'] for section in structure.values() for line in section])
    all_text_lower = all_text.lower()
    food_keywords = ['pain', 'sandwich', 'menu', 'plat', 'boisson', 'eau', 'cafe', 'the']
    context_info['has_food_keywords'] = any(keyword in all_text_lower for keyword in food_keywords)
    alcohol_keywords = ['biere', 'vin', 'alcool', 'whisky', 'vodka', 'cocktail']
    context_info['has_alcohol_keywords'] = any(keyword in all_text_lower for keyword in alcohol_keywords)
    payment_keywords = {'carte': 'card', 'espece': 'cash', 'cheque': 'check', 'cb': 'card'}
    for keyword, method in payment_keywords.items():
        if keyword in all_text_lower:
            context_info['payment_method'] = method
            break
    return context_info


def check_fuzzy_match(ocr_text_word, reference_keyword, threshold=80):
    """
    Vérifie si un mot extrait de l'OCR est suffisamment similaire à un mot clé de référence
    en utilisant la correspondance floue (fuzz.ratio).
    """
    # Utilise fuzz.ratio qui donne un score de 0 à 100
    # On peut aussi utiliser fuzz.partial_ratio si le mot clé est une sous-chaîne possible.
    # Pour 'épicerie' vs 'épiceri', ratio est bon. Pour 'supermarché' vs 'supermar', partial_ratio serait mieux.
    # Pour commencer, ratio est souvent suffisant pour des fautes légères.
    return fuzz.ratio(ocr_text_word, reference_keyword) >= threshold


def enhanced_categorization(text, amount=None, structure=None):
    """
    Catégorisation améliorée utilisant la structure, le contexte et la correspondance floue.
    """
    cleaned_text = clean_text(text)
    detected_category = "Autre"

    # 1. Vérifier les enseignes connues (priorité absolue) avec correspondance floue
    # Ici, nous pourrions aussi faire du fuzzy matching, mais pour des noms exacts,
    # un simple 'in' est souvent suffisant ou alors il faut une logique plus avancée
    # pour les noms complexes qui ne sont pas de simples mots-clés.
    # Pour l'instant, on garde la correspondance exacte pour les enseignes connues car elles doivent être très fiables.
    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in cleaned_text:
            return category  # On retourne la catégorie immédiatement si match exact

    # 2. Analyse contextuelle si structure disponible
    context = {}  # Initialise context pour éviter erreur si structure est None
    if structure:
        context = extract_contextual_info_from_structure(structure)
        # Logique contextuelle avancée
        if context['has_alcohol_keywords']:
            return "Bar"  # Retourne la catégorie immédiatement si forte correspondance
        elif context['has_food_keywords']:
            if amount:  # Vérifier si amount est None ou 0
                if amount > 30 and context['has_multiple_items']:
                    return "Courses"  # Plus de 30€ et plusieurs articles de nourriture => Courses
                elif amount <= 30 and context['has_multiple_items']:
                    return "Restaurant"  # Moins de 30€ et plusieurs articles de nourriture => Restaurant
                else:
                    return "Restaurant"  # Un seul article ou petite somme, mais nourriture
            else:  # Pas de montant, mais des indices de nourriture
                return "Restaurant"

    # 3. Scoring par mots-clés avec pondération et correspondance floue
    category_scores = {}
    # On itère sur chaque mot du texte nettoyé pour le comparer aux mots-clés
    words_in_text = cleaned_text.split()  # Sépare le texte en mots

    for cat, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            for ocr_word in words_in_text:
                if check_fuzzy_match(ocr_word, keyword, threshold=85):  # Utilise le fuzzy matching
                    base_weight = 1
                    # Pondération selon la position dans la structure (si disponible)
                    if structure:
                        header_text = ' '.join([line['text'] for line in structure.get('header', [])]).lower()
                        body_text = ' '.join([line['text'] for line in structure.get('body', [])]).lower()

                        # Bonus si le mot-clé est trouvé dans le header (souvent le nom du commerce ou type)
                        if fuzz.partial_ratio(keyword, header_text) >= 85:  # Utilise partial_ratio pour le header
                            base_weight += 2  # Plus de poids pour le header
                        # Bonus pour des mots clés trouvés dans les lignes d'items
                        if structure and any(fuzz.partial_ratio(keyword, line['text'].lower()) >= 85 for line in
                                             structure.get('body', []) if line['type'] == 'item'):
                            base_weight += 1

                    score += base_weight
                    # Pour éviter de compter le même mot OCR plusieurs fois pour le même mot clé,
                    # on peut le marquer ou le retirer de `words_in_text` (mais attention à ne pas modifier la liste en boucle)
                    # ou simplement `break` ici pour passer au prochain `keyword` si un match est trouvé
                    break  # Passe au prochain keyword après un match pour ce ocr_word
        if score > 0:
            category_scores[cat] = score

    # Choisir la meilleure catégorie si score significatif
    if category_scores:
        max_score = max(category_scores.values())
        if max_score > 0:  # N'importe quel score positif
            detected_category = max(category_scores, key=category_scores.get)

    # 4. Heuristiques de fallback basées sur le montant (si la catégorie est toujours "Autre")
    if detected_category == "Autre" and amount is not None:
        detected_category = categorize_by_amount_heuristic(amount, cleaned_text)

    return detected_category


def categorize_by_amount_heuristic(amount, text):
    """Heuristiques de catégorisation basées sur le montant et des indices textuels"""
    # Indices contextuels dans le texte (mis à jour)
    food_indicators = any(check_fuzzy_match(word, "pain") or
                          check_fuzzy_match(word, "boisson") or
                          check_fuzzy_match(word, "cafe") or
                          check_fuzzy_match(word, "sandwich") or
                          check_fuzzy_match(word, "menu") or
                          check_fuzzy_match(word, "plat")
                          for word in text.split())  # Vérifie avec chaque mot du texte

    transport_indicators = any(check_fuzzy_match(word, "essence") or
                               check_fuzzy_match(word, "carburant") or
                               check_fuzzy_match(word, "station") or
                               check_fuzzy_match(word, "parking")
                               for word in text.split())

    if amount <= 5:
        return "Bar" if any(
            check_fuzzy_match(word, "boisson") or check_fuzzy_match(word, "cafe") for word in text.split()) else "Autre"
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
    structure = reconstruct_ticket_structure(text)  # Assure-toi que cette fonction existe et est importée
    detected_category = enhanced_categorization(text, amount, structure)
    location_name, final_category = extract_location_name_structured(text, detected_category)
    return final_category, location_name


def interpret_text(extracted_text):
    """Version améliorée de l'interprétation avec analyse structurelle"""
    cleaned_text = clean_text(extracted_text)
    result = {
        "amount": None, "currency": "eur", "location_name": "Inconnu",
        "category": "Autre", "date": None, "hour": None, "country": "france"
    }

    result["amount"] = find_amount(extracted_text)
    result["category"], result["location_name"] = find_category_and_location_enhanced(
        extracted_text, result["amount"]
    )
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
                print(f" - {line_info['text']} (type: {line_info['type']})")
    category, location = find_category_and_location_enhanced(extracted_text)
    print(f"\nRÉSULTAT: {location} - {category}")