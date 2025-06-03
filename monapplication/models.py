from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone





class VisiteMaintenance(models.Model):
    agence = models.ForeignKey('Agence', on_delete=models.CASCADE)
    date_visite = models.DateField()
    objet = models.CharField(max_length=255)
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Visite du {self.date_visite} à {self.agence.nom}"
    
    



    
#Pour les responsables d'agence
class ResponsableAgence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=10, unique=True)
    telephone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (Responsable)"


class Agence(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    localisation = models.CharField(max_length=255, blank=True, null=True)

    responsable = models.ForeignKey(
        ResponsableAgence,  # changé ici
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsable de l'agence"
    )

    def __str__(self):
        return self.nom
    
    



#Pour les maintenanciers 
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=10, unique=True)
    telephone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



class AgentCommercial(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=10, unique=True)
    telephone = models.CharField(max_length=15)
    gerant_de_club = models.BooleanField(default=False)
    gerant = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'gerant_de_club': True},
        related_name='agents_sous_gerance',
        verbose_name="Gérant"
    )

    def __str__(self):
        role = "Gérant de club" if self.gerant_de_club else "Agent commercial"
        return f"{self.nom} {self.prenom} - {role}"
    
    

class Panne(models.Model):
    TYPE_EQUIPEMENT_CHOICES = [
        ('TERMINAL', 'Terminal'),
        ('IMPRIMANTE', 'Imprimante'),
        ('CHARGEUR', 'Chargeur'),
        ('ECD', 'ECD'),
    ]

    ETAT_CHOICES = [
        ('en_attente', 'En attente'),
        ('resolue', 'Résolue'),
    ]

    agent_commercial = models.ForeignKey('AgentCommercial', on_delete=models.CASCADE)
    type_equipement = models.CharField(max_length=50, choices=TYPE_EQUIPEMENT_CHOICES)
    description = models.TextField()
    date_signalisation = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='en_attente')

    # Le maintenancier (utilisateur connecté qui a signalé)
    maintenancier = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,  # ← rend le champ nullable temporairement
        blank=True,  # ← permet de ne pas l'afficher dans les formulaires si tu utilises ModelForm
    )

    def __str__(self):
        
        return f"Panne {self.id} - {self.agent_commercial.nom} - {self.type_equipement} - {self.get_etat_display()}"
    
    

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255)  # Par exemple, "Panne"
    object_id = models.PositiveIntegerField()  # ID de l'objet affecté
    details = models.TextField(blank=True, null=True)  # Détails supplémentaires (par exemple, champs modifiés)
    field_modified = models.CharField(max_length=255, null=True, blank=True)  # Champ pour stocker quel champ a été modifié
    timestamp = models.DateTimeField(auto_now_add=True)  # Date et heure de l'activité
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Pour stocker l'adresse IP de l'utilisateur

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"
    
    
    


class PanneAgence(models.Model):
    ETAT_CHOICES = [
        ('en_attente', 'En attente'),
        ('resolue', 'Résolue'),
    ]

    responsable = models.ForeignKey('ResponsableAgence', on_delete=models.CASCADE)
    agence = models.ForeignKey('Agence', on_delete=models.CASCADE)
    titre = models.CharField(max_length=255, default='Panne')
    description = models.TextField()
    date_signalement = models.DateTimeField(default=timezone.now)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='en_attente')
    maintenanciers = models.ManyToManyField('Agent', blank=True)

    def __str__(self):
        return self.titre


class Notification(models.Model):
    
    type_notification = models.CharField(max_length=100, default='panne')
    panne_agence = models.ForeignKey('PanneAgence', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.titre



# Create your models here.
