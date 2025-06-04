# text_interpretation/constants.py

# --- Configuration des catégories et mots clés ---
CATEGORIES = {
    "Restaurant": [
        "restaurant", "repas", "midi", "soir", "dîner", "déjeuner", "petit-déjeuner",
        "brasserie", "pizzeria", "sushi", "asiatique", "fast food", "snack",
        "traiteur", "livraison repas", "uber eats", "deliveroo", "just eat",
        "cantine", "self-service", "grill", "crêperie", "glacier", "salon de thé",
        "buffet", "catering", "service traiteur", "food truck", "foodtruck"
    ],
    "Loisir": [
        "loisir", "divertissement", "cinéma", "concert", "spectacle", "théâtre",
        "parc d'attractions", "musée", "exposition", "activité", "jeux", "jeux vidéo",
        "billetterie", "entrée", "bowling", "laser game", "karting", "paintball",
        "escape game", "casino", "piscine (loisir)", "zoo", "aquarium", "club",
        "soirée", "évènement", "festival", "clubbing", "karaoké", "bar à jeux",
        "parc aquatique", "aire de jeux", "billard", "baby-foot"
    ],
    "Sport": [
        "sport", "salle de sport", "fitness", "gym", "abonnement sport", "coach sportif",
        "équipement sportif", "vêtements sport", "chaussures sport", "nutrition sportive",
        "compétition", "course", "match", "billet match", "stade", "piscine (sport)",
        "club de sport", "licence sportive", "art martial", "danse", "yoga", "pilates",
        "escalade", "randonnée", "vélo (sportif)", "natation", "tennis", "football",
        "basketball", "athlétisme", "musculation", "cardio", "remise en forme"
    ],
    "Courses": [
        "supermarché", "supérette", "épicerie", "courses", "produits alimentaires",
        "primeur", "boulangerie", "pâtisserie", "boucherie", "poissonnerie",
        "fromagerie", "marché", "alimentation générale", "produits frais", "fruits",
        "légumes", "viande", "poisson", "pain", "viennoiseries", "fromage", "yaourt",
        "lait", "oeufs", "céréales", "pâtes", "riz", "huile", "condiments", "épices",
        "produits surgelés", "confiserie", "biscuits", "gâteaux", "sodas", "jus de fruits",
        "eau minérale", "alcool", "vin", "bière", "spiritueux", "apéro",
        "hygiène", "produits ménagers", "produits d'entretien", "produits de beauté",
        "lessive", "liquide vaisselle", "papier toilette", "savon", "shampoing",
        "dentifrice", "mouchoirs", "produits pour bébé", "produits pour animaux",
        "droguerie", "parapharmacie", "cosmétiques"
    ],
    "Culture": [
        "culture", "musée", "exposition", "galerie d'art", "bibliothèque", "médiathèque",
        "livre", "librairie", "journal", "magazine", "presse", "cd", "dvd", "vinyle",
        "abonnement culturel", "atelier artistique", "cours d'art", "visite guidée",
        "monument", "site historique", "conférence", "vernissage", "vernissages",
        "concert classique", "opéra", "ballet", "philharmonie", "patrimoine"
    ],
    "Shopping": [
        "shopping", "vêtements", "chaussures", "accessoires", "bijoux", "sac",
        "mode", "prêt-à-porter", "boutique", "magasin", "centre commercial",
        "décoration", "meuble", "ameublement", "électroménager", "électronique",
        "téléphone", "ordinateur", "tablette", "télévision", "appareil photo",
        "jeux vidéo", "jouet", "cadeau", "parfum", "cosmétiques (achat)",
        "quincaillerie", "bricolage", "jardinage", "animalerie", "fleuriste",
        "librairie (achat)", "produits électroniques", "matériel informatique",
        "bijouterie", "horlogerie", "maroquinerie", "lingerie", "optique", "lunettes",
        "articles de sport (achat)", "articles de voyage", "valise", "sac à dos",
        "supermarché (non alimentaire)", "grandes surfaces (non alimentaire)", "marketplace"
    ],
    "Voyage": [
        "voyage", "billet avion", "train", "sncf", "tgv", "ouigo", "ter", "vol",
        "hôtel", "hébergement", "airbnb", "gîte", "camping", "auberge", "motel",
        "location voiture", "séjour", "vacances", "croisière", "ferry", "autocar",
        "forfait voyage", "agence de voyage", "tourisme", "excursion", "visite",
        "tour", "circuit", "passeport", "visa", "chambre d'hôtes", "bed and breakfast",
        "taxi (voyage)", "transfert aéroport", "transports (voyage)"
    ],
    "Trajet": [
        "essence", "carburant", "diesel", "gazole", "station service", "péage", "autoroute",
        "taxi", "vtc", "uber", "bolt", "free now", "le cab", "chauffeur privé",
        "bus", "tram", "métro", "ticket bus", "abonnement transport", "rer",
        "parking", "garage", "laverie auto", "covoiturage", "blablacar",
        "trottinette", "vélo (location)", "vélib", "transports en commun",
        "transport public", "déplacement", "frais kilométriques", "péages",
        "pont", "tunnel", "gare", "gare routière", "gare sncf", "autoroute", "route"
    ],
    "Bar": [
        "bar", "café", "boissons", "pub", "club", "discothèque", "cocktail", "bière",
        "vin", "alcool", "apéro", "happy hour", "terrasse", "brasserie (boissons)",
        "night club", "boîte de nuit", "salon de thé (boissons)"
    ],
    "Santé": [
        "santé", "médecin", "consultation", "hôpital", "clinique", "pharmacie",
        "médicaments", "ordonnance", "dentiste", "ophtalmologiste", "spécialiste",
        "kinésithérapeute", "ostéopathe", "infirmière", "laboratoire", "analyse",
        "radiologie", "scanner", "irm", "soins", "hospitalisation", "lunettes (santé)",
        "lentilles", "audition", "prothèse", "appareil auditif", "fauteuil roulant",
        "matériel médical", "prévention", "vaccin", "bilan de santé", "mutuelle (remboursement)",
        "franchise médicale", "ticket modérateur", "ambulance", "secours", "urgence",
        "médecine douce", "sophrologie", "acupuncture", "naturopathie", "podologue",
        "psychologue", "thérapie", "bien-être (médical)"
    ],
    "Education": [
        "éducation", "école", "université", "collège", "lycée", "crèche", "garderie",
        "frais de scolarité", "inscription école", "cours", "leçon", "formation",
        "atelier", "manuel scolaire", "fournitures scolaires", "livre (éducation)",
        "stage", "soutien scolaire", "tutorat", "diplôme", "certification", "examen",
        "concours", "bibliothèque (frais)", "logiciel éducatif", "abonnement éducatif",
        "études", "scolarité", "rentrée scolaire", "formation professionnelle",
        "formation continue", "cours en ligne", "webinaire (éducation)"
    ],
    "Prêts": [
        "prêt", "crédit", "emprunt", "remboursement prêt", "intérêts", "crédit immobilier",
        "crédit auto", "prêt personnel", "prêt étudiant", "microcrédit",
        "découvert bancaire", "agios", "facilité de caisse", "rachat de crédit",
        "regroupement de crédits", "amortissement", "crédit à la consommation",
        "crédit renouvelable", "crédit bail", "leasing", "loyer financier"
    ],
    "Fiscal": [
        "impôt", "impôts", "taxes", "taxe sur la valeur ajoutée", "tva", "impôt sur le revenu",
        "taxe foncière", "taxe d'habitation", "prélèvement à la source", "cfe", "cvae",
        "amende", "pénalité", "redressement fiscal", "déclaration fiscale",
        "conseil fiscal", "expert comptable (fiscal)", "droits d'enregistrement",
        "frais de douane", "droits de douane", "timbre fiscal", "fiscalité",
        "contribution", "cotisation sociale (indépendant)", "urssaf (indépendant)",
        "impôts locaux", "impôts nationaux", "taxes diverses", "taxes gouvernementales"
    ],
    "Abonnements": [
        "abonnement", "internet", "fibre", "adsl", "téléphone", "mobile", "forfait mobile",
        "streaming", "netflix", "spotify", "deezer", "prime video", "disney+",
        "logiciel", "logiciel en ligne", "saas", "cloud", "antivirus", "jeu vidéo (abonnement)",
        "salle de sport (abonnement)", "transport (abonnement)", "magazine (abonnement)",
        "journal (abonnement)", "application", "service", "mensuel", "annuel",
        "service de streaming", "box internet", "forfait mobile", "canal+", "beIN SPORTS",
        "sfr", "orange", "bouygues", "free", "télévision payante", "plateforme"
    ],
    "Charges": [
        "eau", "électricité", "gaz", "chauffage", "climatisation", "internet", "facture eau",
        "facture électricité", "facture gaz", "facture internet", "abonnement eau",
        "abonnement électricité", "abonnement gaz", "charges locatives", "charges de copropriété",
        "entretien immeuble", "nettoyage (immeuble)", "syndic", "ordures ménagères",
        "assainissement", "chauffagiste", "plombier", "réparation (maison)",
        "concierge", "gardien", "ascenseur", "sécurité (immeuble)", "alarme (maison)",
        "extincteur (maison)", "maintenance (maison)", "gaz naturel", "fioul", "bois de chauffage"
    ],
    "Assurances": [
        "assurance", "assurance habitation", "assurance auto", "assurance moto",
        "assurance santé", "mutuelle", "complémentaire santé", "prévoyance",
        "assurance vie", "assurance emprunteur", "assurance responsabilité civile",
        "rc pro", "assurance professionnelle", "assurance multirisque", "courtier assurance",
        "prime d'assurance", "contrat d'assurance", "garantie", "frais d'assurance",
        "protection juridique", "assurance voyage", "assurance annulation", "assurance maladie",
        "assurance chômage (privé)"
    ],
    "Logement": [
        "loyer", "loyers", "loyer mensuel", "loyer appartement", "loyer maison",
        "bail", "location appartement", "location maison", "agence immobilière",
        "frais d'agence", "dépôt de garantie", "caution", "aménagement", "rénovation",
        "travaux", "matériel de construction", "bricolage (gros œuvre)", "meubles",
        "immobilier", "achat immobilier", "vente immobilière", "crédit immobilier",
        "taxe foncière (propriétaire)", "impôts fonciers", "taxe d'habitation (propriétaire)",
        "résidence principale", "résidence secondaire", "propriété", "investissement locatif",
        "copropriété (frais non charges)", "syndic de copropriété (frais non charges)"
    ]
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