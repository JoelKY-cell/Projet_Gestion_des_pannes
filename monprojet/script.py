import requests
import json

# Charge le corps de la requête depuis le fichier JSON
with open('request.json', 'r') as f:
    request_body = json.load(f)

# Charge la clé API depuis les settings ou un fichier sécurisé
API_KEY = "TA_CLE_API"

# Envoie la requête HTTP POST
url = f"https://recaptchaenterprise.googleapis.com/v1/projects/my-project-89527-1729851111884/assessments?key=6LcXz2sqAAAAAH4JLruQRDFmm1TyRWGcU9_RSgB3"
response = requests.post(url, json=request_body)

# Vérifie la réponse
if response.status_code == 200:
    print("Requête envoyée avec succès")
    print("Réponse:", response.json())
else:
    print("Erreur lors de l'envoi de la requête")
    print("Statut:", response.status_code)
    print("Réponse:", response.text)