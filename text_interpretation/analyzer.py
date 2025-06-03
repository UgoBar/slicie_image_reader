import re
import json
from constants import CATEGORIES, KNOWN_COMMERCES
from parser import clean_text, find_amount, find_date, find_hour


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


def extract_location_name_improved(text, detected_category="Autre"):
    """Extraction améliorée du nom du commerce"""
    lines = text.strip().split('\n')
    location_candidates = []

    # 1. Recherche dans les enseignes connues (priorité absolue)
    clean_text_lower = clean_text(text)

    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in clean_text_lower:
            return known_name.title(), category

    # 2. Extraction du nom en début de ticket (lignes 1-3)
    for i, line in enumerate(lines[:3]):
        line = line.strip()
        if not line:
            continue

        # Nettoyer la ligne
        clean_line = re.sub(r'[^\w\s-]', '', line)
        words = clean_line.split()

        # Filtrer les mots parasites
        filtered_words = []
        skip_words = {'ticket', 'caisse', 'facture', 'recu', 'tva', 'tel', 'fax',
                      'adresse', 'siret', 'rcs', 'sarl', 'sas', 'eurl', 'www', 'email'}

        for word in words:
            if (len(word) >= 3 and
                    word.lower() not in skip_words and
                    not word.isdigit() and
                    not re.match(r'^\d+[a-z]*$', word.lower())):
                filtered_words.append(word)

        if filtered_words:
            # Prendre les 1-2 premiers mots significatifs
            candidate_name = ' '.join(filtered_words[:2])
            location_candidates.append({
                'name': candidate_name,
                'line_position': i,
                'confidence': calculate_name_confidence(candidate_name, detected_category)
            })

    # 3. Recherche de noms avec majuscules dans tout le texte
    capitalized_words = re.findall(r'\b[A-Z][A-Za-z]{2,}\b', text)
    for word in capitalized_words[:5]:  # Limiter aux 5 premiers
        if (word.lower() not in ['tva', 'total', 'merci', 'ticket', 'caisse'] and
                len(word) >= 3):
            location_candidates.append({
                'name': word,
                'line_position': 10,  # Moins prioritaire
                'confidence': calculate_name_confidence(word, detected_category)
            })

    # 4. Sélection du meilleur candidat
    if location_candidates:
        # Trier par confiance puis par position
        location_candidates.sort(key=lambda x: (x['confidence'], -x['line_position']), reverse=True)
        return location_candidates[0]['name'], detected_category

    return "Inconnu", detected_category


def calculate_keyword_weight(keyword, text):
    """Calcule le poids d'un mot-clé selon son contexte"""
    base_weight = 1

    # Bonus si le mot-clé apparaît plusieurs fois
    count = text.count(keyword)
    weight = base_weight * count

    # Bonus selon la longueur du mot-clé (plus spécifique = plus de poids)
    if len(keyword) > 8:
        weight *= 1.5

    return weight


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


def find_category_and_location(text, amount=None):
    """Version améliorée de la détection catégorie + lieu"""
    detected_category = "Autre"
    cleaned_text = clean_text(text)

    # 1. Vérifier les enseignes connues (priorité absolue)
    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in cleaned_text:
            location_name = known_name.title()
            return category, location_name

    # 2. Scoring par mots-clés avec pondération
    category_scores = {}
    for cat, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword in cleaned_text:
                # Pondération selon la position et le contexte
                score += calculate_keyword_weight(keyword, cleaned_text)
        if score > 0:
            category_scores[cat] = score

    # Sélection de la meilleure catégorie
    if category_scores:
        detected_category = max(category_scores, key=category_scores.get)

    # 3. Extraction du nom du lieu
    location_name, final_category = extract_location_name_improved(text, detected_category)

    # 4. Heuristiques de fallback basées sur le montant
    if detected_category == "Autre" and amount is not None:
        detected_category = categorize_by_amount_heuristic(amount, cleaned_text)

    return detected_category, location_name


def interpret_text(extracted_text):
    """Version améliorée de l'interprétation"""
    cleaned_text = clean_text(extracted_text)

    result = {
        "amount": None, "currency": "eur", "location_name": "Inconnu",
        "category": "Autre", "date": None, "hour": None, "country": "france"
    }

    # Extraction améliorée
    result["amount"] = find_amount(extracted_text)
    result["category"], result["location_name"] = find_category_and_location(
        extracted_text, result["amount"]
    )

    # Les fonctions date/heure restent identiques
    result["date"] = find_date(extracted_text)
    result["hour"] = find_hour(extracted_text)

    return json.dumps(result, indent=4)