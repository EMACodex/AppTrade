from django import forms
from .models import *
from django.contrib.auth.models import User

"""
Formulario para agregar una nueva criptomoneda al sistema.
Permite al usuario ingresar únicamente el ticker de la criptomoneda.
"""
class CriptoForm(forms.ModelForm):
    class Meta:
        model = Cripto
        fields = ["ticker"]
        
"""
Formulario para la edición del perfil del usuario.
Permite modificar información personal como nombre y correo electrónico.
También permite configurar alertas de precios para criptomonedas específicas.  
"""      
class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    alert_cripto = forms.ModelChoiceField(
    queryset=Cripto.objects.all().order_by('ticker'),  
    required=False,
    widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Campo para definir el precio de alerta que activará una notificación.
    alert_price = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    # Campo para activar o desactivar las alertas de precio.
    receive_alerts = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
   
    class Meta:
        model = UserProfile
        fields = ['alert_cripto', 'alert_price', 'receive_alerts']

    # Método para inicializar el formulario con valores predeterminados basados en el usuario autenticado.
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener usuario
        super().__init__(*args, **kwargs)

        if user:
            # Asignar los datos del usuario al formulario
            self.fields['first_name'].initial = user.first_name
            self.fields['email'].initial = user.email


''' 
Formulario de registro de nuevos usuarios.
Permite a los usuarios crear una cuenta ingresando un nombre de usuario, correo electrónico, nombre y contraseña.
''' 
class RegistroForm(forms.ModelForm):
    # Campo para el nombre de usuario, obligatorio.
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Campo para el correo electrónico, obligatorio.
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # Campo para el nombre del usuario, obligatorio.
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Campo para la contraseña, obligatorio.
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password"]

    # Método para validar los datos ingresados en el formulario.
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        first_name = cleaned_data.get("first_name")
        password = cleaned_data.get("password")
        
        # Si alguno de los campos está vacío, lanza un error de validación.
        if not username or not email or not first_name or not password:
            raise forms.ValidationError("Todos los campos son obligatorios. Por favor, complétalos.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)  # Guarda el usuario sin enviarlo a la base de datos aún.
        user.set_password(self.cleaned_data["password"])  # Guarda la contraseña encriptada.
        if commit:
            user.save()  # Guarda el usuario en la base de datos si commit es True.
        return user  # Retorna el usuario creado.
    
    
