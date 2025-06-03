
import re
from datetime import datetime


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s,.-_€]', '', text)
    return text


def find_amount(text):
    patterns = [
        r'(?:total|net a payer|somme|ttc|total net|montant|montant)[\s:]*(\d{1,5}(?:[.,]\d{2})?)',
        r'(\d{1,5}(?:[.,]\d{2}?))\s*(?:eur|euros|€)',
        r'(\d{1,5}[.,]\d{2})',
        r'(\d{1,5}\.\d{2})',
        r'(\d{1,5},\d{2})',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            amounts = []
            for m in matches:
                try:
                    clean_m = m.replace(',', '.')
                    amounts.append(float(clean_m))
                except ValueError:
                    pass
            if amounts:
                if any(k in text for k in ["total", "net a payer", "ttc"]):
                    return max(amounts)
                else:
                    return max(amounts)
    return None


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
    hour_patterns = [
        r'\b(\d{1,2}[h:]\d{2})\b',
        r'\b(\d{1,2}[h])\b',
        r'\b(\d{1,2}:\d{2}:\d{2})\b'
    ]

    for pattern in hour_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for hour_str in matches:
                try:
                    hour_str_clean = hour_str.replace('h', ':')
                    if len(hour_str_clean.split(':')) == 2:
                        parsed_hour = datetime.strptime(hour_str_clean, '%H:%M')
                    elif len(hour_str_clean.split(':')) == 3:
                        parsed_hour = datetime.strptime(hour_str_clean, '%H:%M:%S')
                    else:
                        parsed_hour = datetime.strptime(hour_str_clean.split(':')[0], '%H')
                    return parsed_hour.strftime('%H:%M')
                except ValueError:
                    continue
    return None