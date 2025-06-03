import os
import sys

# Chemin vers le répertoire de votre projet Django
path = '/home/Joel1Ky/monprojet'
if path not in sys.path:
    sys.path.append(path)

# Définir la variable d'environnement pour les paramètres Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'monprojet.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
