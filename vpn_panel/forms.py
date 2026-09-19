from django import forms
from .models import AmneziaConfig

class AmneziaConfigForm(forms.ModelForm):
    """Form to create or update an AmneziaWG configuration profile."""
    
    class Meta:
        model = AmneziaConfig
        fields = ['name', 'config_content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 bg-gray-800/90 border border-gray-700 rounded-lg text-white text-base sm:text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150',
                'placeholder': 'e.g. Frankfurt Server'
            }),
            'config_content': forms.Textarea(attrs={
                'class': 'w-full px-3.5 py-2.5 bg-gray-800/90 border border-gray-700 rounded-lg text-white font-mono text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150 custom-scrollbar resize-y',
                'rows': 7,
                'placeholder': '[Interface]\nPrivateKey = ...'
            }),
        }
