from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class CriarConta(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False, 
        help_text="Opcional", 
        widget=forms.TextInput(attrs={'placeholder': 'Primeiro Nome'})
    )
    last_name = forms.CharField(
        max_length=30, required=False, 
        help_text="Opcional", 
        widget=forms.TextInput(attrs={'placeholder': 'Último Nome'})
    )
    email = forms.EmailField(required=True, help_text="Obrigatório. Preencha com um e-mail válido.",
    widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CriarConta, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Nome de utilizador'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Palavra-Passe'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme a Palavra-Passe'})

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto_perfil', 'data_nascimento', 'genero']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

