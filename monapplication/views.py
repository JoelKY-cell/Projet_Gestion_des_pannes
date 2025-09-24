from django.shortcuts import render, get_object_or_404, redirect
from .models import Panne
from .forms import PanneForm
from django.contrib.auth import login, authenticate
from .forms import LoginForm
from django.http import JsonResponse  
from django.views.decorators.csrf import csrf_exempt  
from django.contrib.auth.models import User  
from .forms import CustomUserCreationForm
from django.conf import settings
from django.db.models import Q
from .forms import AgenceForm, AgentForm
from django.http import JsonResponse
import requests 
import matplotlib.pyplot as plt
from django.contrib.auth import update_session_auth_hash
import io
from django.shortcuts import render, redirect
from .forms import PanneForm
from .models import AgentCommercial, Panne
from django.contrib import messages
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
import base64
from collections import Counter
import pandas as pd
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render
from django.db.models import Count
from .forms import AnalysePanneForm
from .models import Panne
from .forms import DateFilterForm
from django.db.models import Q
from .models import Panne, ActivityLog
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.core.paginator import Paginator
import random
from django.core.mail import send_mail
from .forms import EmailForm
from django.contrib.auth.forms import SetPasswordForm




from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Agence, Agent
from .forms import AgenceForm, AgentForm
from collections import Counter

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


# Les agences


from .models import Agence, ResponsableAgence, VisiteMaintenance
from .forms import AgenceForm, VisiteMaintenanceForm


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.db.models import Q, Count
from django.core.paginator import Paginator
from collections import Counter

from .models import Agence, Agent, AgentCommercial, Panne, ActivityLog, PanneAgence, Notification
from .forms import AgenceForm, AgentForm, AgentCommercialForm, PanneForm, CustomUserCreationForm, LoginForm, AnalysePanneForm, PanneAgenceForm

from django.http import HttpResponse, HttpResponseForbidden



from django.contrib.admin.views.decorators import staff_member_required

# Vérifie si l'utilisateur est admin
def is_admin(user):
    return user.is_superuser

from django.contrib.auth.decorators import login_required, user_passes_test












def get_agent_commercial(request):
    matricule = request.GET.get('matricule', None)
    if matricule:
        try:
            agent = AgentCommercial.objects.get(matricule=matricule)
            return JsonResponse({
                'success': True,
                'nom': agent.nom,
                'prenom': agent.prenom,
                'matricule': agent.matricule,
                'telephone': agent.telephone
            })
        except AgentCommercial.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})












@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_pannes = Panne.objects.count()
    total_maintenanciers = Agent.objects.count()
    total_commercials = AgentCommercial.objects.count()
    total_pannes_en_attente = Panne.objects.filter(etat='en_attente').count()
    total_pannes_resolues = Panne.objects.filter(etat='resolue').count()
    total_agences = Agence.objects.count()
    total_responsables = ResponsableAgence.objects.count()

    panne_data = Panne.objects.values('type_equipement')\
        .annotate(count=Count('type_equipement'))\
        .order_by('type_equipement')

    labels = [entry['type_equipement'] for entry in panne_data]
    data = [entry['count'] for entry in panne_data]

    # Prepare data for pannes by agent (for circular chart)
    agent_counts = (
        Panne.objects.values('agent_commercial__nom', 'agent_commercial__prenom')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    agent_labels = [
        f"{agent['agent_commercial__nom'] or ''} {agent['agent_commercial__prenom'] or ''}".strip()
        for agent in agent_counts
    ]
    agent_data = [agent['total'] for agent in agent_counts]

    context = {
        'total_pannes': total_pannes,
        'total_maintenanciers': total_maintenanciers,
        'total_commercials': total_commercials,
        'total_pannes_en_attente': total_pannes_en_attente,
        'total_pannes_resolues': total_pannes_resolues,
        'total_agences': total_agences,
        'total_responsables': total_responsables,
        'labels': labels,
        'data': data,
        'agent_labels': agent_labels,
        'agent_data': agent_data,
    }

    return render(request, 'admin_dashboard.html', context)








@login_required
@user_passes_test(is_admin)
def ajouter_maintenancier(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            # Création du User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            # Création de l’agent lié à ce user
            agent = form.save(commit=False)
            agent.user = user
            agent.save()

            messages.success(request, "Maintenancier ajouté avec succès.")
            return redirect('liste_maintenanciers')  # ou autre vue cible
    else:
        form = AgentForm()

    return render(request, 'ajouter_maintenancier.html', {'form': form})




@login_required
@user_passes_test(is_admin)
def liste_maintenanciers(request):
    agents = Agent.objects.select_related('user')  # Optimisation avec `select_related`
    
    return render(request, 'liste_maintenanciers.html', {'agents': agents})






# 🔹 Gestion des agents commerciaux
@login_required
def ajouter_commercial(request):
    if request.method == 'POST':
        form = AgentCommercialForm(request.POST)
        
        # Cas AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        # Cas normal (non-AJAX)
        if form.is_valid():
            form.save()
            return redirect('liste_commerciaux')
    
    else:
        form = AgentCommercialForm()

    return render(request, 'ajouter_commercial.html', {'form': form})


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import AgentCommercial  # Modèle à adapter selon ton projet

def liste_commerciaux(request):
    query = request.GET.get('q', '')
    agents_list = AgentCommercial.objects.all()

    if query:
      agents_list = agents_list.filter(
        Q(nom__icontains=query) |
        Q(prenom__icontains=query) |
        Q(matricule__icontains=query) |
        Q(telephone__icontains=query)
    ) 

    paginator = Paginator(agents_list, 18)  # 18 agents par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'agents': page_obj.object_list,
        'request': request  # requis pour {{ request.GET.q }} dans le template
    }
    return render(request, 'agent_liste.html', context)






@login_required
def modifier_commercial(request, pk):
    agent = get_object_or_404(AgentCommercial, pk=pk)
    if request.method == 'POST':
        form = AgentCommercialForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            return redirect('agent_liste')
    else:
        form = AgentCommercialForm(instance=agent)
    return render(request, 'modifier_commercial.html', {'form': form, 'agent': agent})



@login_required
def supprimer_commercial(request, pk):
    agent = get_object_or_404(AgentCommercial, pk=pk)
    if request.method == 'POST':
        agent.delete()
        return redirect('agent_liste')
    return render(request, 'supprimer_commercial.html', {'agent': agent})







#Les pannes


@login_required
def signaler_panne(request):
    if request.method == 'POST':
        form = PanneForm(request.POST)
        if form.is_valid():
            panne = form.save(commit=False)
            panne.maintenancier = request.user  # <-- Ajoute l'utilisateur connecté
            panne.save()
            messages.success(request, "Panne signalée avec succès.")
            return redirect('signaler_panne')
    else:
        form = PanneForm()
    return render(request, 'signaler_panne.html', {'form': form})







@login_required
def toggle_etat_panne(request, panne_id):
    panne = get_object_or_404(Panne, id=panne_id)

    if panne.etat == 'en_attente':
        panne.etat = 'resolue'
    else:
        panne.etat = 'en_attente'

    panne.save()  # Très important !
    messages.success(request, f"L'état de la panne a été changé à : {panne.etat}.")
    
      # Retour à la page précédente
    return redirect(request.META.get('HTTP_REFERER'))








def analyse(request):
    form = AnalysePanneForm(request.GET or None)
    pannes = Panne.objects.all()

    if form.is_valid():
        mois = form.cleaned_data.get('mois')
        annee = form.cleaned_data.get('annee')
        if mois:
            pannes = pannes.filter(date_signalisation__month=mois)
        if annee:
            pannes = pannes.filter(date_signalisation__year=annee)

    if request.GET.get('general'):
        pannes = Panne.objects.all()

    agent_counts = (
        pannes
        .values('agent_commercial__nom', 'agent_commercial__prenom')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    labels = [
        f"{agent['agent_commercial__nom'] or ''} {agent['agent_commercial__prenom'] or ''}".strip()
        for agent in agent_counts
    ]
    data = [agent['total'] for agent in agent_counts]

    return render(request, 'agents.html', {
        'form': form,
        'labels': labels,
        'data': data,
    })





def admin_enregistrement(request):
    if request.method == 'POST':
        form = PanneForm(request.POST)

        # Si la requête est AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                panne_instance = form.save(commit=False)

                # Récupérer le matricule envoyé via le champ texte
                matricule = form.cleaned_data.get('agent_commercial_id')

                try:
                    # On retrouve l'agent avec ce matricule
                    agent_commercial = AgentCommercial.objects.get(matricule=matricule)
                    panne_instance.agent_commercial = agent_commercial

                    # Sauvegarde
                    panne_instance.save()

                    # Log de l'activité
                    ActivityLog.objects.create(
                        user=request.user,
                        action='CREATE',
                        model_name='Panne',
                        object_id=panne_instance.id,
                        details=f"Création d'une panne: {panne_instance.description}",
                    )

                    return JsonResponse({'success': True})
                except AgentCommercial.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Agent commercial non trouvé.'})

            # Le formulaire est invalide
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = PanneForm()

    return render(request, 'admin_enregistrement.html', {'form': form})







def liste_agences(request):
    agences = Agence.objects.select_related('responsable').order_by('nom')
    return render(request, 'liste_agences.html', {'agences': agences})

@login_required
def ajouter_agence(request):
    if request.method == 'POST':
        form = AgenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_agences')
    else:
        form = AgenceForm()
    return render(request, 'ajouter_agence.html', {'form': form})

@login_required
def modifier_agence(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    if request.method == 'POST':
        form = AgenceForm(request.POST, instance=agence)
        if form.is_valid():
            form.save()
            return redirect('liste_agences')
    else:
        form = AgenceForm(instance=agence)
    return render(request, 'modifier_agence.html', {'form': form, 'agence': agence})

@login_required
def supprimer_agence(request, pk):
    agence = get_object_or_404(Agence, pk=pk)
    agence.delete()
    return redirect('liste_agences')
                                                                                                                                                                                                                                             





# Les Responsables d'agence 
@login_required
def liste_responsables_agence(request):
    responsables = ResponsableAgence.objects.select_related('user').order_by('user__last_name')
    return render(request, 'liste_responsables.html', {'responsables': responsables})


from .forms import ResponsableAgenceCreationForm

@login_required
def ajouter_responsable_agence(request):
    if request.method == 'POST':
        form = ResponsableAgenceCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ResponsableAgenceCreationForm()
    return render(request, 'ajouter_responsable.html', {'form': form})

@login_required
def modifier_responsable_agence(request, pk):
    responsable = get_object_or_404(ResponsableAgence, pk=pk)
    if request.method == 'POST':
        form = ResponsableAgenceCreationForm(request.POST, instance=responsable)
        if form.is_valid():
            form.save()
            return redirect('liste_responsables')
    else:
        form = ResponsableAgenceCreationForm(instance=responsable)
    return render(request, 'modifier_responsable_agence.html', {'form': form, 'responsable': responsable})

@login_required
def supprimer_responsable_agence(request, pk):
    responsable = get_object_or_404(ResponsableAgence, pk=pk)
    responsable.delete()
    return redirect('liste_responsables')



def is_responsable(user):
    return hasattr(user, 'responsableagence')

@user_passes_test(is_responsable)
def responsable_dashboard(request):
    responsable = request.user.responsableagence

    context = {
        'responsable': responsable,
        # Tu peux ajouter ici des stats ou infos spécifiques si nécessaire
    }

    return render(request, 'responsable_dashboard.html', context)



def login_success(request):
    user = request.user
    if hasattr(user, 'responsableagence'):
        return redirect('responsable_dashboard')
    elif user.is_superuser:
        return redirect('admin_dashboard')
    else:
        return redirect('home')





#Liste des pannes user

def liste_enregistrement(request):
    query = request.GET.get('q')  # Obtient le paramètre de recherche 'q' de l'URL
    if query:
        enregistrements = Panne.objects.filter(
            Q(agent_nom__icontains=query) |
            Q(agent_prenom__icontains=query) |
            Q(agent_numero__icontains=query) |
            Q(equipement_type__icontains=query) |
            Q(description__icontains=query) |
            Q(date_signalisation__icontains=query) |
            Q(agent_id__icontains=query)
        ).order_by('-date_signalisation')  # Trier par date décroissante
    else:
        enregistrements = Panne.objects.all().order_by('-date_signalisation')

    # Pagination
    paginator = Paginator(enregistrements, 8)  # Afficher 8 éléments par page
    page_number = request.GET.get('page')  # Obtenir le numéro de la page actuelle
    page_obj = paginator.get_page(page_number)  # Récupérer les objets de la page actuelle

    return render(request, 'liste_enregistrement.html', {
        'page_obj': page_obj,
        'query': query,  # Inclure la requête pour conserver la recherche dans l'interface
    })










def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            form.add_error(None, 'Invalid')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def index(request): 
    return render(request,'index.html')

def home(request):
    return render(request,'home.html')

# Vérifier si l'utilisateur est un superutilisateur ou a des privilèges d'administration
def is_admin(user):
    return user.is_superuser





def modifier_enregistrement(request, pk):
    enregistrement = get_object_or_404(Panne, pk=pk)  # Récupérer l'enregistrement par ID

    if request.method == 'POST':
        form = PanneForm(request.POST, instance=enregistrement)  # Lier le formulaire à l'enregistrement  
        if form.is_valid():
            # Sauvegardez les anciennes données pour le log
            ancienne_description = enregistrement.description
            ancien_equipement_type = enregistrement.equipement_type

            # Enregistrez les modifications
            form.save()  # Enregistrer les modifications  

            # Ajouter un log d'activité pour la modification
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Panne',
                object_id=enregistrement.id,  # Utilisation de l'ID de l'instance
                details=f"Modification d'une panne: Ancienne description '{ancienne_description}', Nouveau description '{enregistrement.description}', Ancien type équipement '{ancien_equipement_type}', Nouveau type équipement '{enregistrement.equipement_type}'",
            )

            return redirect('liste_enregistrement')  # Rediriger vers la liste des enregistrements  
    else:
        form = PanneForm(instance=enregistrement)  # Créer le formulaire avec les données de l'enregistrement

    return render(request, 'modifier_enregistrement.html', {'form': form})




@login_required
def supprimer_enregistrement(request, pk):
    enregistrement = get_object_or_404(Panne, pk=pk)

    if request.method == 'POST':
        try:
            # Sauvegarder les informations avant la suppression pour les logs
            description = enregistrement.description
            equipement_type = enregistrement.equipement_type

            # Suppression de l'enregistrement
            enregistrement.delete()

            # Enregistrement de l'action dans ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='DELETE',
                model_name='Panne',
                object_id=pk,
                details=f"Suppression de la panne: Description '{description}', Type d'équipement '{equipement_type}'"
            )

            return redirect('liste_enregistrement')  # Rediriger vers la liste des enregistrements 

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Une erreur est survenue : {str(e)}"})

    return JsonResponse({'success': False, 'message': 'Requête invalide.'})

 






def analyse_pannes(request):
    form = DateFilterForm(request.GET or None)

    if request.GET.get('general'):
        # Si le bouton "Voir toutes les pannes" est cliqué
        panne_data = Panne.objects.values('type_equipement')\
            .annotate(count=Count('type_equipement'))\
            .order_by('type_equipement')
    elif form.is_valid():
        mois = form.cleaned_data.get('mois')
        annee = form.cleaned_data.get('annee')

        filters = Q()
        if mois:
            filters &= Q(date_signalisation__month=mois)
        if annee:
            filters &= Q(date_signalisation__year=annee)

        panne_data = Panne.objects.filter(filters)\
            .values('type_equipement')\
            .annotate(count=Count('type_equipement'))\
            .order_by('type_equipement')
    else:
        # Aucun filtre appliqué
        panne_data = Panne.objects.values('type_equipement')\
            .annotate(count=Count('type_equipement'))\
            .order_by('type_equipement')

    labels = [entry['type_equipement'] for entry in panne_data]
    data = [entry['count'] for entry in panne_data]

    return render(request, 'analyse_pannes.html', {
        'labels': labels,
        'data': data,
        'form': form
    })




@login_required
def activity_log(request):
    # Récupérer l'historique des activités de l'utilisateur connecté
    logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'activity_log.html', {'logs': logs})

@login_required
def supprimer_historique(request, log_id):
    log = get_object_or_404(ActivityLog, id=log_id)
    
    # Suppression du log
    log.delete()
    
    # Rediriger vers la page des logs avec un message de succès
    return redirect('activity_log')  # Adaptez l'URL de redirection à votre structure


def supprimer_tout_historique(request):
    if request.method == 'GET':  # Vous pouvez utiliser GET ou POST selon le cas
        # Supprimer tous les logs de l'utilisateur connecté
        logs = ActivityLog.objects.filter(user=request.user)
        logs.delete()
        
        # Rediriger l'utilisateur vers la page d'historique avec un message de succès
        return redirect('activity_log')  # Modifiez 'activity_log' avec l'URL correcte de votre historique
    
    
@login_required
def mon_compte(request):
    # Récupérer l'utilisateur actuellement connecté
    user = request.user
    # Passer le mot de passe en clair temporairement (pour l'affichage uniquement)
    context = {
        'user': user,
        'password_clear': user.password  # Affiche le mot de passe crypté en clair pour l'interface
    }
    return render(request, 'mon_compte.html', context)


@login_required
def modifier_nom_utilisateur(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        ancien_username = request.user.username  # Sauvegarde du nom d'utilisateur avant la modification
        request.user.username = username
        request.user.save()
        
        # Enregistrer l'activité dans le log
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='User',
            object_id=request.user.id,
            details=f"Changement de nom d'utilisateur: Ancien nom '{ancien_username}', Nouveau nom '{request.user.username}'",
        )
        
        messages.success(request, "Nom d'utilisateur modifié avec succès!")
        return redirect('mon_compte')
    return render(request, 'modifier_nom_utilisateur.html')


@login_required
def modifier_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        ancien_email = request.user.email  # Sauvegarde de l'email avant la modification
        request.user.email = email
        request.user.save()

        # Enregistrer l'activité dans le log
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='User',
            object_id=request.user.id,
            details=f"Changement d'email: Ancien email '{ancien_email}', Nouveau email '{request.user.email}'",
        )

        messages.success(request, "Email modifié avec succès!")
        return redirect('mon_compte')
    return render(request, 'modifier_email.html')


@login_required
def modifier_prenom(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        ancien_prenom = request.user.first_name  # Sauvegarde du prénom avant la modification
        request.user.first_name = first_name
        request.user.save()

        # Enregistrer l'activité dans le log
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='User',
            object_id=request.user.id,
            details=f"Changement de prénom: Ancien prénom '{ancien_prenom}', Nouveau prénom '{request.user.first_name}'",
        )

        messages.success(request, "Prénom modifié avec succès!")
        return redirect('mon_compte')
    return render(request, 'modifier_prenom.html')

@login_required
def modifier_nom(request):
    if request.method == 'POST':
        last_name = request.POST.get('last_name')
        ancien_nom = request.user.last_name  # Sauvegarde du nom de famille avant la modification
        request.user.last_name = last_name
        request.user.save()

        # Enregistrer l'activité dans le log
        ActivityLog.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='User',
            object_id=request.user.id,
            details=f"Changement de nom de famille: Ancien nom '{ancien_nom}', Nouveau nom '{request.user.last_name}'",
        )

        messages.success(request, "Nom de famille modifié avec succès!")
        return redirect('mon_compte')
    return render(request, 'modifier_nom.html')

@login_required
def supprimer_compte(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('index')  # Rediriger vers la page d'accueil après suppression du compte
    return render(request, 'supprimer_compte.html')



def modifier_utilisateur(request):
    if request.method == 'POST':
        champ = request.POST.get('champ')
        valeur = request.POST.get('valeur')
        
        # Vérifier si le champ est l'un des champs modifiables
        if champ in ['username', 'email', 'first_name', 'last_name']:
            ancien_valeur = getattr(request.user, champ)  # Obtenir l'ancienne valeur
            
            # Modifier l'attribut de l'utilisateur
            setattr(request.user, champ, valeur)
            request.user.save()

            # Enregistrer l'action dans l'historique
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=request.user.id,
                details=f"Modification de {champ}: Ancienne valeur '{ancien_valeur}', Nouvelle valeur '{valeur}'",
            )
            
            return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'error'})


@login_required
def modifier_mot_de_passe(request):
    if request.method == 'POST':
        nouveau_mot_de_passe = request.POST.get('nouveau_mot_de_passe')
        
        if nouveau_mot_de_passe:
            user = request.user
            ancien_mot_de_passe = user.password  # Sauvegarde du mot de passe avant la modification
            user.set_password(nouveau_mot_de_passe)
            user.save()
            update_session_auth_hash(request, user)  # Garder l'utilisateur connecté après le changement

            # Enregistrer l'activité dans le log
            ActivityLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=request.user.id,
                details=f"Changement de mot de passe: Ancien mot de passe '{ancien_mot_de_passe}', Nouveau mot de passe [masqué]",
            )
            
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


# Traitement de la modification du mot de passe
@login_required
def modifier_mot_de_passe_action(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Garder la session active
            return redirect('mon_compte')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'modifier_mot_de_passe.html', {'form': form})



def request_reset_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            
            if user:
                # Générer un code aléatoire
                reset_code = random.randint(100000, 999999)

                # Sauvegarder le code pour la vérification
                # Assurez-vous d'avoir un modèle pour sauvegarder ces données (ou utilisez la session)
                request.session['reset_code'] = reset_code
                request.session['user_email'] = email

                # Envoyer le code par email
                send_mail(
                    'Votre code de réinitialisation de mot de passe',
                    f'Votre code de réinitialisation est : {reset_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Un code de réinitialisation a été envoyé à votre adresse e-mail.")
                return redirect('verify_reset_code')
            else:
                messages.error(request, "Aucun utilisateur trouvé avec cet e-mail.")
        else:
            messages.error(request, "Veuillez entrer un e-mail valide.")
    else:
        form = EmailForm()

    return render(request, 'request_reset_email.html', {'form': form})


def verify_reset_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        session_code = request.session.get('reset_code')

        if code and str(code) == str(session_code):
            # Code correct, permettre à l'utilisateur de réinitialiser le mot de passe
            return redirect('reset_password')
        else:
            messages.error(request, "Le code que vous avez entré est incorrect.")

    return render(request, 'verify_reset_code.html')



def reset_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès !")
            return redirect('login')  # Rediriger vers la page de connexion
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'reset_password.html', {'form': form})





@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def panne_list(request):
    pannes = Panne.objects.all()
    return render(request, 'panne_list.html', {'pannes': pannes})

@login_required
@user_passes_test(is_admin)
def activity_log(request):
    logs = ActivityLog.objects.all()
    return render(request, 'activity_log.html', {'logs': logs})

@login_required
@user_passes_test(is_admin)
def create_panne(request):
    if request.method == 'POST':
        form = PanneForm(request.POST)
        if form.is_valid():
            panne = form.save()
            return redirect('panne_list')
    else:
        form = PanneForm()
    return render(request, 'create_panne.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def modify_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'modify_user.html', {'form': form})

@login_required

@login_required
def delete_panne(request, panne_id):
    panne = get_object_or_404(Panne, id=panne_id)
    panne.delete()
    
    if is_admin(request.user):
        messages.success(request, "Panne supprimée avec succès.")
        return redirect('panne_list')  # Vue réservée aux admins
    else:
        messages.info(request, "La panne a été supprimée.")
        return redirect('liste_enregistrement')  # Vue pour les utilisateurs normaux



@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('user_list')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_activity_log(request):
    # Récupérer l'historique des activités de l'utilisateur connecté
    logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'admin_activity_log.html', {'logs': logs})











from django.core.mail import send_mail
from django.contrib.auth.models import User

@login_required
def signaler_panne_agence(request):
    responsable = get_object_or_404(ResponsableAgence, user=request.user)

    try:
        agence = Agence.objects.get(responsable=responsable)
    except Agence.DoesNotExist:
        messages.error(request, "Aucune agence n'est associée à votre profil.")
        return redirect('responsable_dashboard')

    if request.method == 'POST':
        form = PanneAgenceForm(request.POST)
        if form.is_valid():
            panne = form.save(commit=False)
            panne.responsable = responsable
            panne.agence = agence
            panne.save()

            # Envoi d'email à l'administrateur unique
            admin_email = "joelkyras3@gmail.com"
            subject = f"Nouvelle panne signalée par {responsable.user.get_full_name()}"
            message = f"Une nouvelle panne a été signalée pour l'agence {agence.nom}.\n\nTitre: {panne.titre}\nDescription: {panne.description}\nDate: {panne.date_signalement.strftime('%d/%m/%Y %H:%M')}\n\nVeuillez consulter le tableau de bord pour plus de détails."
            from_email = settings.DEFAULT_FROM_EMAIL  # Utilise DEFAULT_FROM_EMAIL dans settings.py

            try:
                send_mail(subject, message, from_email, [admin_email], fail_silently=False)
            except Exception as e:
                # Log ou gestion d'erreur si nécessaire
                pass

            messages.success(request, "La panne a été signalée avec succès.")
            return redirect('liste_panne_agence')
    else:
        form = PanneAgenceForm()

    return render(request, 'signaler_panne_agence.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def afficher_notifications(request):
    notifications = Notification.objects.order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import PanneAgence, Agent

@login_required
@user_passes_test(is_admin)
def affecter_maintenanciers(request, panne_id):
    panne = get_object_or_404(PanneAgence, id=panne_id)
    agents = Agent.objects.all()

    if request.method == 'POST':
        agents_ids = request.POST.getlist('agents')
        panne.maintenanciers.set(agents_ids)
        panne.save()

        # Envoi d'email aux maintenanciers assignés
        subject = f"Nouvelle panne assignée : {panne.titre}"
        message = (
            f"Vous avez été assigné à une nouvelle panne.\n\n"
            f"Titre: {panne.titre}\n"
            f"Description: {panne.description}\n"
            f"Agence: {panne.agence.nom}\n"
            f"Date de signalement: {panne.date_signalement.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Veuillez consulter votre tableau de bord pour plus de détails."
        )
        from_email = settings.DEFAULT_FROM_EMAIL

        assigned_agents = Agent.objects.filter(id__in=agents_ids)
        for agent in assigned_agents:
            try:
                send_mail(subject, message, from_email, [agent.user.email], fail_silently=False)
            except Exception as e:
                # Log ou gestion d'erreur si nécessaire
                pass

        messages.success(request, "Maintenancier(s) affecté(s) avec succès.")
        return render(request, 'affecter_maintenanciers.html', {'panne': panne, 'agents': agents})

    # POUR LE CAS GET → afficher le formulaire
    return render(request, 'affecter_maintenanciers.html', {'panne': panne, 'agents': agents})






@login_required
def mes_pannes_assignees(request):
    user = request.user

    if hasattr(user, 'agent'):
        agent = user.agent
        pannes = PanneAgence.objects.filter(maintenanciers=agent).order_by('-date_signalement')
    else:
        pannes = []

    return render(request, 'mes_pannes_assignees.html', {'pannes': pannes})






@login_required
def marquer_panne_resolue(request, panne_id):
    panne = get_object_or_404(PanneAgence, id=panne_id)

    if not hasattr(request.user, 'agent') or request.user.agent not in panne.maintenanciers.all():
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette panne.")
        return redirect('mes_pannes_assignees')

    panne.etat = 'resolue'
    panne.save()
    messages.success(request, "Panne marquée comme résolue.")
    return redirect('mes_pannes_assignees')

from django.utils import timezone


def detail_panne(request, id):
    panne = get_object_or_404(Panne, id=id)
    return render(request, 'detail_panne.html', {'panne': panne})



@login_required
def liste_panne_agence(request):
    responsable = get_object_or_404(ResponsableAgence, user=request.user)

    try:
        agence = Agence.objects.get(responsable=responsable)
    except Agence.DoesNotExist:
        messages.error(request, "Aucune agence n'est associée à votre profil.")
        return render(request, 'liste_panne_agence.html', {
            'pannes': [],
            'agence': None,
        })

    # ✅ Utiliser PanneAgence ici
    pannes = PanneAgence.objects.filter(agence=agence).order_by('-date_signalement')

    return render(request, 'liste_panne_agence.html', {
        'pannes': pannes,
        'agence': agence,
    })

def liste_notifications_agence(request):
    pannes_resolues = PanneAgence.objects.filter(est_resolue=True, vue_par_admin=False)
    return render(request, 'notifications.html', {'pannes_resolues': pannes_resolues})




@login_required
@user_passes_test(is_admin)
def liste_pannes_agences(request):
    pannes = PanneAgence.objects.order_by('-date_signalement')
    return render(request, 'liste_pannes_agences.html', {'pannes': pannes})



















@login_required
@user_passes_test(is_admin)
def liste_visites_admin(request):
    visites = VisiteMaintenance.objects.all().order_by('date_visite')
    return render(request, 'liste_visites_admin.html', {'visites': visites})


@login_required
@user_passes_test(is_admin)
def planifier_visite(request):
    if request.method == 'POST':
        form = VisiteMaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Visite de maintenance planifiée avec succès.")
            return redirect('liste_visites_admin')
    else:
        form = VisiteMaintenanceForm()
    return render(request, 'planifier_visite.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def modifier_visite(request, visite_id):
    visite = get_object_or_404(VisiteMaintenance, id=visite_id)
    if request.method == 'POST':
        form = VisiteMaintenanceForm(request.POST, instance=visite)
        if form.is_valid():
            form.save()
            messages.success(request, "Visite modifiée avec succès.")
            return redirect('liste_visites_admin')
    else:
        form = VisiteMaintenanceForm(instance=visite)
    return render(request, 'modifier_visite.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def supprimer_visite(request, visite_id):
    visite = get_object_or_404(VisiteMaintenance, id=visite_id)
    if request.method == 'POST':
        visite.delete()
        messages.success(request, "Visite supprimée.")
        return redirect('liste_visites_admin')
    return render(request, 'supprimer_visite.html', {'visite': visite})


# -----------------------------
# 2. Vue pour le RESPONSABLE d'agence
# -----------------------------

@login_required
def liste_visites_agence(request):
    responsable = request.user.responsableagence
    agence = get_object_or_404(Agence, responsable=responsable)
    visites = VisiteMaintenance.objects.filter(agence=agence).order_by('date_visite')
    return render(request, 'liste_visites_agence.html', {'visites': visites, 'agence': agence})


# -----------------------------
# 3. Vue pour les MAINTENANCIERS
# -----------------------------

@login_required
def liste_visites_maintenancier(request):
    visites = VisiteMaintenance.objects.all().order_by('date_visite')
    return render(request, 'liste_visites_maintenancier.html', {'visites': visites})



# Create your views here.




