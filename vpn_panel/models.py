from django.db import models
from django.db import transaction
import re

class AmneziaConfig(models.Model):
    """Model representing an AmneziaWG/WireGuard configuration profile."""
    name = models.CharField(max_length=100, default='New Profile')
    endpoint_ip = models.CharField(max_length=100, blank=True, help_text="Extracted automatically from config")
    config_content = models.TextField(help_text="Paste your AmneziaWG (.conf) configuration here")
    is_active = models.BooleanField(default=False)
    last_latency = models.CharField(max_length=20, default="N/A", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Extract Endpoint IP and ensure only one active config exists."""
        # Automatically extract Endpoint IP from config content
        if self.config_content:
            match = re.search(r'Endpoint\s*=\s*([^:]+)', self.config_content, re.IGNORECASE)
            if match:
                self.endpoint_ip = match.group(1).strip()

        # Ensure only one config is active at a time
        if self.is_active:
            with transaction.atomic():
                AmneziaConfig.objects.filter(is_active=True).update(is_active=False)
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
