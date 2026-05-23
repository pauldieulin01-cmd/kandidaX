from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Etudiant
 
 
class CustomUserCreationForm(UserCreationForm):
    username    = forms.CharField(max_length=150, label="Nom d'utilisateur",
                    widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-input'}))
    email       = forms.EmailField(label='Email',
                    widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-input'}))
    password1   = forms.CharField(label='Mot de passe', strip=False,
                    widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-input'}))
    password2   = forms.CharField(label='Confirmer', strip=False,
                    widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe', 'class': 'form-input'}))
    nom_complet = forms.CharField(max_length=100, label='Nom complet',
                    widget=forms.TextInput(attrs={'placeholder': 'Jean Dupont', 'class': 'form-input'}))
    serie       = forms.ChoiceField(choices=Etudiant.NIVEAU_CHOICES, label='Série',
                    widget=forms.Select(attrs={'class': 'form-input'}))
    option      = forms.ChoiceField(choices=Etudiant.OPTION_CHOICES, label='Option',
                    widget=forms.Select(attrs={'class': 'form-input'}))
    entite      = forms.ChoiceField(choices=Etudiant.ENTITE_CHOICES, label='Entité',
                    widget=forms.Select(attrs={'class': 'form-input'}))
 
    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ('username', 'email', 'nom_complet', 'serie', 'option', 'entite', 'password1', 'password2')
 
 
class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur",
                widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-input'}))
    password = forms.CharField(label='Mot de passe',
                widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-input'}))
 
