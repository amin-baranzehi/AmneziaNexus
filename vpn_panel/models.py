from django.db import models

class AmneziaConfig(models.Model):
    name = models.CharField(max_length=100, default='Default Profile')
    config_content = models.TextField(help_text="Paste your AmneziaWG (.conf) configuration here")
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
