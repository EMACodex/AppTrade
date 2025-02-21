from django import forms
from .models import *
from django.contrib.auth.models import User

class CriptoForm(forms.ModelForm):
    class Meta:
        model = Cripto
        fields = ["ticker"]
        
        
class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['currency', 'country', 'receive_alerts', 'alert_price', 'alert_cripto']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener usuario
        super().__init__(*args, **kwargs)

        if user:
            # Asignar los datos del usuario al formulario
            self.fields['first_name'].initial = user.first_name
            self.fields['email'].initial = user.email


        
        
class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Oculta la contraseña
        if commit:
            user.save()
        return user