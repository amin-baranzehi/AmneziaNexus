from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import AmneziaConfig

class ResponsiveTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.config = AmneziaConfig.objects.create(
            name='Frankfurt Pro',
            config_content='[Interface]\nPrivateKey = abc\n[Peer]\nEndpoint = 198.51.100.1:51820\nPublicKey = def\n'
        )

    def test_login_page_renders_responsive_elements(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('viewport', content)
        self.assertIn('max-w-sm sm:max-w-md', content)
        self.assertIn('text-base sm:text-sm', content)

    def test_dashboard_renders_mobile_and_desktop_views(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('vpn_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Verify responsive cards (mobile) and table (desktop)
        self.assertIn('block md:hidden', content)
        self.assertIn('hidden md:block', content)
        self.assertIn('server-card', content)
        self.assertIn('custom-scrollbar', content)
        self.assertIn('latency-' + str(self.config.id), content)
        self.assertIn('Frankfurt Pro', content)
        self.assertIn('modal-container', content)

    def test_logs_page_renders_responsive_elements(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('vpn_panel:logs'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('vpn-logs-container', content)
        self.assertIn('sys-logs-container', content)
        self.assertIn('Dashboard', content)

    def test_dashboard_empty_state_responsive(self):
        self.client.login(username='testuser', password='password123')
        AmneziaConfig.objects.all().delete()
        response = self.client.get(reverse('vpn_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('No servers added yet', content)

    def test_dashboard_active_server_status_badge(self):
        self.client.login(username='testuser', password='password123')
        self.config.is_active = True
        self.config.save()
        response = self.client.get(reverse('vpn_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Disconnect', content)

