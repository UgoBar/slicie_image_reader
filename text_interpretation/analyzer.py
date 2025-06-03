
import re
import json
from constants import CATEGORIES, KNOWN_COMMERCES
from parser import clean_text, find_amount, find_date, find_hour


def find_category_and_location(text, amount=None):
    detected_category = "Autre"
    location_name = "Inconnu"
    cleaned_text = clean_text(text)

    for known_name, category in KNOWN_COMMERCES.items():
        if known_name in cleaned_text:
            detected_category = category
            location_name = known_name.title()
            return detected_category, location_name

    category_scores = {}
    for cat, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in cleaned_text:
                category_scores[cat] = category_scores.get(cat, 0) + 1

    if category_scores:
        detected_category = max(category_scores, key=category_scores.get)

    if detected_category in ["Autre", "Shopping"] and amount is not None:
        if amount <= 20 and any(k in cleaned_text for k in ["cafe", "boisson", "pain", "boulangerie", "grigne"]):
            detected_category = "Restaurant"
        elif amount <= 50 and any(k in cleaned_text for k in ["pizza", "burger", "sushi"]):
            detected_category = "Restaurant"
        elif amount > 50 and any(k in cleaned_text for k in ["courses", "aliment", "supermarche"]):
            detected_category = "Courses"

    lines = text.split('\n')
    for line in lines[:5]:
        words = line.split()
        for word in words:
            if len(word) > 2 and word[0].isupper() and word.isalpha():
                if word.lower() not in ["tva", "ticket", "bienvenue", "merci", "adresse", "tel"]:
                    if location_name == "Inconnu":
                        location_name = word
                    break
        if location_name != "Inconnu" and location_name != "Autre":
            break

    return detected_category, location_name


def interpret_text(extracted_text):
    """Interprète le texte extrait pour en déduire les informations de dépense."""
    cleaned_text = clean_text(extracted_text)

    result = {
        "amount": None, "currency": "eur", "location_name": "Inconnu",
        "category": "Autre", "date": None, "hour": None, "country": "france"
    }

    result["amount"] = find_amount(cleaned_text)
    result["date"] = find_date(cleaned_text)
    result["hour"] = find_hour(cleaned_text)
    result["category"], result["location_name"] = find_category_and_location(cleaned_text, result["amount"])

    if result["location_name"] == "Inconnu":
        words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', extracted_text)
        for word in words:
            if word.lower() not in [k.lower() for cat_list in CATEGORIES.values() for k in cat_list]:
                if word.lower() not in ["tva", "ticket", "bienvenue", "merci", "adresse", "tel", "facture", "total"]:
                    result["location_name"] = word
                    break

    if result["category"] == "Autre" and result["amount"] is not None:
        if result["amount"] < 10:
            result["category"] = "Bar"
        elif result["amount"] < 30:
            result["category"] = "Restaurant"
        elif result["amount"] > 50:
            result["category"] = "Courses"

    return json.dumps(result, indent=4)