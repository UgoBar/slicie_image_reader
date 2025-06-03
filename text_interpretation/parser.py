# text_interpretation/parser.py

import re
from datetime import datetime

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s,.-_€]', '', text)
    return text


def find_amount(text):
    """Version améliorée avec logique de fallback intelligente"""
    clean_text_lower = text.lower()
    candidates = []

    # Patterns avec priorités
    priority_patterns = [
        # Priorité maximale : mots-clés explicites
        (r'(?:total\s*a\s*payer|net\s*a\s*payer|montant\s*total)[\s:]*(\d{1,5}(?:[.,]\d{2})?)', 100, 'total_explicit'),
        (r'(?:total|ttc)[\s:]*(\d{1,5}(?:[.,]\d{2})?)', 90, 'total'),
        (r'(?:somme|montant)[\s:]*(\d{1,5}(?:[.,]\d{2})?)', 85, 'amount_keyword'),

        # Priorité haute : format avec devise
        (r'(\d{1,5}(?:[.,]\d{2}?))\s*(?:eur|euros|€)', 80, 'with_currency'),

        # Priorité moyenne : montants décimaux
        (r'(\d{1,5}[.,]\d{2})', 60, 'decimal'),

        # Priorité basse : nombres entiers (fallback)
        (r'(?<!\d)(\d{1,3})(?!\d)', 30, 'integer')
    ]

    for pattern, priority, pattern_type in priority_patterns:
        matches = re.findall(pattern, clean_text_lower, re.IGNORECASE)
        for match in matches:
            try:
                amount = float(match.replace(',', '.'))
                if 0.1 <= amount <= 9999:  # Filtrage des montants réalistes
                    candidates.append({
                        'amount': amount,
                        'priority': priority,
                        'type': pattern_type,
                        'original': match
                    })
            except ValueError:
                continue

    if not candidates:
        return None

    # Logique de sélection intelligente
    candidates.sort(key=lambda x: x['priority'], reverse=True)

    # Si on a des candidats haute priorité, on les privilégie
    high_priority = [c for c in candidates if c['priority'] >= 80]
    if high_priority:
        # Parmi les haute priorité, on prend le plus élevé (souvent le total)
        return max(high_priority, key=lambda x: x['amount'])['amount']

    # Sinon, logique contextuelle
    medium_priority = [c for c in candidates if c['priority'] >= 60]
    if medium_priority:
        # Pour les décimaux, on prend le plus élevé (probablement le total)
        return max(medium_priority, key=lambda x: x['amount'])['amount']

    # Fallback : le montant le plus élevé parmi les restants
    return max(candidates, key=lambda x: x['amount'])['amount']


def find_date(text):
    date_patterns = [
        r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b',
        r'\b(\d{4}[./-]\d{1,2}[./-]\d{1,2})\b',
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for date_str in matches:
                date_str_normalized = date_str.replace('.', '/').replace('-', '/')
                try:
                    if len(date_str_normalized.split('/')[-1]) == 2:
                        parsed_date = datetime.strptime(date_str_normalized, '%d/%m/%y')
                    else:
                        parsed_date = datetime.strptime(date_str_normalized, '%d/%m/%Y')
                    return parsed_date.strftime('%d/%m/%Y')
                except ValueError:
                    continue
    return None


def find_hour(text):
    """Recherche l'heure dans le texte (HH:mm, HHhMM, HH:mm:ss)."""

    # Patterns pour l'heure
    hour_patterns = [
        r'\b(\d{1,2}:\d{2}:\d{2})\b',  # HH:mm:ss (ajouté en premier pour la priorité)
        r'\b(\d{1,2}[h:]\d{2})\b',     # HH:mm ou HHhMM
        r'\b(\d{1,2}[h])\b',           # HHh
    ]

    for pattern in hour_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for hour_str in matches:
                try:
                    hour_str_clean = hour_str.replace('h', ':')
                    # Vérifier le nombre de segments pour déterminer le format
                    parts = hour_str_clean.split(':')
                    if len(parts) == 3: # HH:mm:ss
                        parsed_hour = datetime.strptime(hour_str_clean, '%H:%M:%S')
                    elif len(parts) == 2: # HH:mm
                        parsed_hour = datetime.strptime(hour_str_clean, '%H:%M')
                    else: # HHh (simple heure)
                         parsed_hour = datetime.strptime(parts[0], '%H')
                    return parsed_hour.strftime('%H:%M') # On garde le format HH:MM pour la sortie
                except ValueError:
                    continue
    return None