from django.forms import ModelForm, TextInput, URLInput, Select, DateInput, Textarea
from teams.models import Team

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'logo', 'region', 'founded', 'description']
        widgets = {
            'name': TextInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Team Name (e.g., "LA Lakers")'
            }),
            'logo': URLInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://example.com/logo.png'
            }),
            'region': Select(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'founded': DateInput(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date' # Use HTML5 date picker
            }),
            'description': Textarea(attrs={
                'class': 'w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'A brief description of the team...'
            }),
        }
