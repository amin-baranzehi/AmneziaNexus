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

    def test_dashboard_has_view_and_edit_modals_and_buttons(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('vpn_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Check buttons with icons
        self.assertIn('view-config-btn', content)
        self.assertIn('edit-config-btn', content)
        
        # Check modals
        self.assertIn('view-config-modal', content)
        self.assertIn('edit-config-modal', content)
        self.assertIn('copy-config-btn', content)
        self.assertIn('config-raw-' + str(self.config.id), content)

    def test_config_edit_view_get(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('vpn_panel:config_edit', args=[self.config.id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Edit Server Profile', content)
        self.assertIn('Frankfurt Pro', content)

    def test_config_edit_view_post_updates_model(self):
        self.client.login(username='testuser', password='password123')
        new_content = '[Interface]\nPrivateKey = updated_key\n[Peer]\nEndpoint = 203.0.113.5:51820\nPublicKey = pub5\n'
        response = self.client.post(reverse('vpn_panel:config_edit', args=[self.config.id]), {
            'name': 'Amsterdam Updated',
            'config_content': new_content
        })
        self.assertEqual(response.status_code, 302)
        self.config.refresh_from_db()
        self.assertEqual(self.config.name, 'Amsterdam Updated')
        self.assertEqual(self.config.endpoint_ip, '203.0.113.5')


