from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import get_agent_commercial

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signaler/', views.signaler_panne, name='signaler_panne'),
    path('liste_enregistrement/', views.liste_enregistrement, name='liste_enregistrement'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('modifier/<int:pk>/', views.modifier_enregistrement, name='modifier_enregistrement'),
    path('supprimer/<int:pk>/', views.supprimer_enregistrement, name='supprimer_enregistrement'), 
    path('analyse_pannes/', views.analyse_pannes, name='analyse_pannes'),
    path('agents/', views.analyse, name='agents'),
    path('activity_log/', views.activity_log, name='activity_log'),
    path('supprimer_historique/<int:log_id>/', views.supprimer_historique, name='supprimer_historique'),
    path('supprimer_tout_historique/', views.supprimer_tout_historique, name='supprimer_tout_historique'),
    path('mon_compte/', views.mon_compte, name='mon_compte'),
    path('modifier_nom_utilisateur/', views.modifier_nom_utilisateur, name='modifier_nom_utilisateur'),
    path('modifier_email/', views.modifier_email, name='modifier_email'),
    path('modifier_prenom/', views.modifier_prenom, name='modifier_prenom'),
    path('modifier_nom/', views.modifier_nom, name='modifier_nom'),
    path('supprimer_compte/', views.supprimer_compte, name='supprimer_compte'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('modifier_utilisateur/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('modifier_mot_de_passe/', views.modifier_mot_de_passe, name='modifier_mot_de_passe'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.create_user, name='create_user'),
    path('admin/users/modify/<int:user_id>/', views.modify_user, name='modify_user'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/pannes/', views.panne_list, name='panne_list'),
    path('admin/pannes/create/', views.create_panne, name='create_panne'),
    path('admin/pannes/delete/<int:panne_id>/', views.delete_panne, name='delete_panne'),
    path('admin/admin_activity_log/', views.admin_activity_log, name='admin_activity_log'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login_success/', views.login_success, name='login_success'),
    path('panne/<int:panne_id>/changer-etat/', views.toggle_etat_panne, name='changer_etat_panne'),
    
    # Routes pour les agences
    path('agences/', views.liste_agences, name='liste_agences'),
    
    path('pannes_agence/', views.liste_pannes_agences, name='liste_pannes_agences'),
    path('panne_agence/', views.liste_panne_agence, name='liste_panne_agence'),
    
    
    path('agences/modifier/<int:pk>/', views.modifier_agence, name='modifier_agence'),
    path('agences/supprimer/<int:pk>/', views.supprimer_agence, name='supprimer_agence'),
    path('signaler_panne_agence/', views.signaler_panne_agence, name='signaler_panne_agence'),
    path('notifications/', views.afficher_notifications, name='notifications'),
    path('pannes_agence/<int:panne_id>/affecter/', views.affecter_maintenanciers, name='affecter_maintenanciers'),
    path('panne/<int:panne_id>/resolue/', views.marquer_panne_resolue, name='marquer_panne_resolue'),
    path('pannes/<int:id>/', views.detail_panne, name='detail_panne'),
    path('agences/ajouter/', views.ajouter_agence, name='ajouter_agence'),

    # Routes pour les responsables d'agence
    path('responsables/', views.liste_responsables_agence, name='liste_responsables'),
    path('responsables/ajouter/', views.ajouter_responsable_agence, name='ajouter_responsable'),
    path('responsables/modifier/<int:pk>/', views.modifier_responsable_agence, name='modifier_responsable_agence'),
    path('responsables/supprimer/<int:pk>/', views.supprimer_responsable_agence, name='supprimer_responsable_agence'),
    path('dashboard/responsable/', views.responsable_dashboard, name='responsable_dashboard'),

    # Routes pour les agents commerciaux
    path('agents/ajouter/', views.ajouter_commercial, name='ajouter_commercial'),
    path('agents/modifier/<int:pk>/', views.modifier_commercial, name='modifier_commercial'),
    path('agents/supprimer/<int:pk>/', views.supprimer_commercial, name='supprimer_commercial'),
    path('agent_liste/', views.liste_commerciaux, name='agent_liste'),
    path('get_agent_commercial/', get_agent_commercial, name='get_agent_commercial'),

   
     path('admin_enregistrement/', views.admin_enregistrement, name='admin_enregistrement'),
     path('ajouter_maintenancier/', views.ajouter_maintenancier, name='ajouter_maintenancier'),
      path('maintenanciers/', views.liste_maintenanciers, name='liste_maintenanciers'),
      
    #vistes de maintenance
    path('visites/', views.liste_visites_admin, name='liste_visites_admin'),
    path('visites/planifier/', views.planifier_visite, name='planifier_visite'),
    path('visites/modifier/<int:visite_id>/', views.modifier_visite, name='modifier_visite'),
    path('visites/supprimer/<int:visite_id>/', views.supprimer_visite, name='supprimer_visite'),

    # Responsable d'agence
    path('agence/visites/', views.liste_visites_agence, name='liste_visites_agence'),

    # Maintenancier
    path('maintenancier/visites/', views.liste_visites_maintenancier, name='liste_visites_maintenancier'),
    path('mes_pannes/', views.mes_pannes_assignees, name='mes_pannes_assignees'),
]

