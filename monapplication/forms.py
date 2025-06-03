from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime
from .models import ResponsableAgence
from .models import Agence, Agent, AgentCommercial, Panne, PanneAgence, Notification, VisiteMaintenance



# --- Formulaire pour les visites de maintenance 

class VisiteMaintenanceForm(forms.ModelForm):
    class Meta:
        model = VisiteMaintenance
        fields = ['agence', 'date_visite', 'objet']
        widgets = {
            'agence': forms.Select(attrs={'class': 'form-control'}),
            'date_visite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
        }



# --- Formulaire pour les agents de maintenance (Agent)
class AgentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Agent
        fields = ['matricule', 'telephone']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class AgentCommercialForm(forms.ModelForm):
    class Meta:
        model = AgentCommercial
        fields = ['nom', 'prenom', 'matricule', 'telephone', 'gerant_de_club', 'gerant']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'gerant_de_club': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_gerant_de_club'}),
            'gerant': forms.Select(attrs={'class': 'form-select', 'id': 'id_gerant'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        gerant_de_club = cleaned_data.get('gerant_de_club')
        gerant = cleaned_data.get('gerant')

        if not gerant_de_club and not gerant:
            raise ValidationError("Vous devez soit cocher 'Gérant de club', soit choisir un gérant.")

        if gerant_de_club and gerant:
            # Optionnel : empêcher d'avoir un gérant si on est gérant soi-même
            raise ValidationError("Un agent gérant de club ne peut pas avoir un gérant.")

        return cleaned_data
    
    
    

# --- Formulaire pour les agences

class AgenceForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['nom', 'adresse', 'localisation', 'responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(AgenceForm, self).__init__(*args, **kwargs)
        # On filtre pour n’afficher que les Responsables d’Agence disponibles
        self.fields['responsable'].queryset = ResponsableAgence.objects.all()
        
        

class PanneAgenceForm(forms.ModelForm):
    class Meta:
        model = PanneAgence
        fields = ['titre', 'description']  # On enlève 'agence'
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        

        
#Formulaire pour les responsables d'agence
# Formulaire pour les responsables d'agence
class ResponsableAgenceCreationForm(forms.ModelForm):
    # Champs du modèle User
    last_name = forms.CharField(label="Nom", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Prénom", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label="Nom d'utilisateur", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ResponsableAgence
        fields = ['matricule', 'telephone']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Création de l'utilisateur
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        # Création du ResponsableAgence
        responsable = super().save(commit=False)
        responsable.user = user
        if commit:
            responsable.save()
        return responsable




# --- Formulaire pour signaler une panne
TYPE_CHOICES = [
    ('TERMINAL', 'Terminal'),
    ('IMPRIMANTE', 'Imprimante'),
    ('CHARGEUR', 'Chargeur'),
    ('ECD', 'ECD'),
]

class PanneForm(forms.ModelForm):
    agent_commercial_id = forms.CharField(
        label="Matricule de l'Agent Commercial",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le matricule du commercial"}),
        required=True
    )

    type_equipement = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type d'Équipement",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Panne
        fields = ['agent_commercial_id', 'type_equipement', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Décrivez la panne'}),
        }

    def clean_agent_commercial_id(self):
        matricule = self.cleaned_data['agent_commercial_id']
        try:
            agent_commercial = AgentCommercial.objects.get(matricule=matricule)
        except AgentCommercial.DoesNotExist:
            raise forms.ValidationError("Aucun Agent Commercial trouvé avec ce matricule.")
        self.cleaned_data['agent_commercial'] = agent_commercial
        return matricule

    def save(self, commit=True):
        panne = super().save(commit=False)
        panne.agent_commercial = self.cleaned_data['agent_commercial']
        panne.type_equipement = self.cleaned_data['type_equipement']
        panne.etat = 'en_attente'  # Définir automatiquement l'état à "En attente"
        if commit:
            panne.save()
        return panne


# --- Formulaire de connexion
class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Nom d'utilisateur ou Email", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username_or_email'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'})
    )

# --- Formulaire d'inscription personnalisé
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    )

# --- Formulaire pour filtrer par date
class DateFilterForm(forms.Form):
    current_year = datetime.now().year
    years = [str(year) for year in range(2000, current_year + 1)]
    mois_choices = [
        ('', 'Sélectionnez un mois'),
        ('1', 'Janvier'),
        ('2', 'Février'),
        ('3', 'Mars'),
        ('4', 'Avril'),
        ('5', 'Mai'),
        ('6', 'Juin'),
        ('7', 'Juillet'),
        ('8', 'Août'),
        ('9', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ]
    annee = forms.ChoiceField(
        choices=[('', 'Sélectionnez une année')] + [(year, year) for year in years],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mois = forms.ChoiceField(
        choices=mois_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# --- Formulaire d'analyse des pannes
class AnalysePanneForm(DateFilterForm):
    pass  # Identique à DateFilterForm

# --- Formulaire simple pour collecter un email
class EmailForm(forms.Form):
    email = forms.EmailField(
        label='Entrez votre e-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


