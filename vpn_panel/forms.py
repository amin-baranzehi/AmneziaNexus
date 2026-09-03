from django import forms
from .models import AmneziaConfig

class AmneziaConfigForm(forms.ModelForm):
    """Form to create or update an AmneziaWG configuration profile."""
    
    class Meta:
        model = AmneziaConfig
        fields = ['name', 'config_content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:border-indigo-500',
                'placeholder': 'e.g. Frankfurt Server'
            }),
            'config_content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white font-mono text-sm focus:outline-none focus:border-indigo-500',
                'rows': 10,
                'placeholder': '[Interface]\nPrivateKey = ...'
            }),
        }
