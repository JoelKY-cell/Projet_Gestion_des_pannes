from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ResponsableAgence, Agence, PanneAgence, Agent
from django.core import mail

class EmailNotificationTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        # Create responsable agence user and related models
        self.responsable_user = User.objects.create_user(username='resp', email='resp@example.com', password='resppass')
        self.responsable = ResponsableAgence.objects.create(user=self.responsable_user, matricule='R001', telephone='123456789')
        self.agence = Agence.objects.create(nom='AgenceTest', adresse='123 rue', responsable=self.responsable)
        # Create maintenancier user and related model
        self.maintenancier_user = User.objects.create_user(username='maint', email='maint@example.com', password='maintpass')
        self.maintenancier = Agent.objects.create(user=self.maintenancier_user, matricule='M001', telephone='987654321')

        self.client = Client()

    def test_email_sent_on_panne_signalement(self):
        # Login as responsable agence
        self.client.login(username='resp', password='resppass')
        url = reverse('signaler_panne_agence')
        data = {
            'titre': 'Panne Test',
            'description': 'Description de la panne test',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('liste_panne_agence'))
        # Check that an email was sent to the admin
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouvelle panne signalée', mail.outbox[0].subject)
        self.assertIn('AgenceTest', mail.outbox[0].body)
        self.assertIn(self.admin_user.email, mail.outbox[0].to)

    def test_email_sent_on_maintenancier_assignment(self):
        # Create a panne agence
        panne = PanneAgence.objects.create(
            responsable=self.responsable,
            agence=self.agence,
            titre='Panne Assign Test',
            description='Description assign test',
        )
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        url = reverse('affecter_maintenanciers', args=[panne.id])
        data = {
            'agents': [self.maintenancier.id],
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        # Check that an email was sent to the maintenancier
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouvelle panne assignée', mail.outbox[0].subject)
        self.assertIn('Panne Assign Test', mail.outbox[0].body)
        self.assertIn(self.maintenancier_user.email, mail.outbox[0].to)
