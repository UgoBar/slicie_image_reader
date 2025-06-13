
Je développe un micro service en python. Le but est de recevoir une image, de voir si c'est un fichier d'image ou de pdf. Ensuite essayer d'en extraire le texte pour l'interpréter et en conclure les informations d'une dépense.

Expected output :
{
    amount: // amount: float
    currency: // string 'eur'
    location_name: // location: string
    category: // among a list of predefined categories
    date: // date: DD/MM/YYYY
    hour: // hour: HH:ss
    country: // string 'france'
}
Pour l'instant je vais cantonner mon application à la France donc pas besoin de traiter les dates avec différents formats.
La liste des catégories :
## Catégories de dépenses usuelles / variables
- Restaurant
- Loisir
- Sport
- Courses
- Culture
- Shopping
- Voyage
- Trajet
- Bar
- Santé
- Education

## Catégories de dépenses récurrentes / fixes
- Prêts
- Fiscal
- Abonnements
- Charges (eau, electricité, internet)
- Assurances
- Logement

J'ai déjà commencé à faire pas mal de code, voilà un lien GitHub Gist pour y accéder : https://gist.github.com/UgoBar/9a57c471c6122f9b243fb0a6ccb4652b