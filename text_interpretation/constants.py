# text_interpretation/constants.py

# --- Configuration des catégories et mots clés ---
CATEGORIES = {
    "Restaurant": ["restaurant", "brasserie", "cafe", "pizzeria", "sandwich", "burger", "fast food", "repas", "midi", "soir", "cantine"],
    "Loisir": ["cinema", "theatre", "concert", "parc", "musee", "exposition", "loisir", "activite", "billet"],
    "Sport": ["sport", "fitness", "gym", "piscine", "club", "abonnement sport"],
    "Courses": ["supermarche", "hypermarche", "courses", "alimentation", "provisions", "boulangerie", "epicerie", "primeur", "marche", "carrefour", "leclerc", "auchan", "lidl", "intermarche", "monoprix"], # Ajout d'enseignes connues
    "Culture": ["librairie", "livre", "fnac", "culture", "galerie"],
    "Shopping": ["vetement", "boutique", "magasin", "chaussure", "electronique", "jouet", "cadeau", "mode", "beaute"],
    "Voyage": ["train", "avion", "hotel", "hebergement", "billet voyage", "transport"],
    "Trajet": ["essence", "carburant", "peage", "parking", "bus", "metro", "tram", "taxi", "uber", "transport en commun", "rer"],
    "Bar": ["bar", "pub", "boisson", "cocktail", "biere"],
    "Santé": ["pharmacie", "medicament", "medecin", "dentiste", "hopital", "mutuelle"],
    "Education": ["ecole", "universite", "formation", "cours", "livre scolaire"],
    "Prêts": ["pret", "credit", "emprunt"],
    "Fiscal": ["impot", "taxe", "tva"],
    "Abonnements": ["abonnement", "netflix", "spotify", "telephonie", "internet box", "streaming"],
    "Charges": ["eau", "electricite", "gaz", "loyer", "facture energie", "internet"],
    "Assurances": ["assurance", "mutuelle", "habitation", "auto"],
    "Logement": ["loyer", "charges logement", "immobilier", "reparation logement"]
}

# Base de données de grandes enseignes (à étendre)
# Priorité haute : si le nom est trouvé, la catégorie est forte
KNOWN_COMMERCES = {
    "carrefour": "Courses",
    "leclerc": "Courses",
    "auchan": "Courses",
    "lidl": "Courses",
    "intermarche": "Courses",
    "monoprix": "Courses",
    "fnac": "Culture",
    "mcdonald's": "Restaurant",
    "burger king": "Restaurant",
    "kfc": "Restaurant",
    "starbucks": "Bar", # ou Bar/Cafe selon l'usage
    "sncf": "Voyage",
    "ratp": "Trajet",
    "totalenergies": "Trajet", # Essence
    "bp": "Trajet", # Essence
    "sephora": "Shopping",
    "decathlon": "Sport",
    "zara": "Shopping",
    "h&m": "Shopping",
    "amazon": "Shopping",
    "netflix": "Abonnements",
    "spotify": "Abonnements",
    "orange": "Abonnements", # Téléphonie
    "free": "Abonnements", # Internet
    "edf": "Charges",
    "gaz de france": "Charges",
    "assurance maladie": "Santé",
    "mutuelle": "Santé",
    "credit agricole": "Prêts",
    "bnp paribas": "Prêts",
    "santander": "Prêts",
    "assurance vie": "Assurances",
    "assurance auto": "Assurances",
    "assurance habitation": "Assurances"
}