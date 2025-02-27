from django.db import models
from django.contrib.auth.models import User

# Modelo que representa una criptomoneda en la base de datos.
class Cripto(models.Model):
    # Campo para almacenar el ticker de la criptomoneda (ej: BTC, ETH).
    # Se define como único para evitar duplicados.
    ticker = models.CharField(max_length=10, unique=True)

    # Método que devuelve el ticker como representación en cadena del objeto.
    def __str__(self):
        return self.ticker


# Modelo que representa el perfil de usuario y sus preferencias de alertas de criptomonedas.
class UserProfile(models.Model):   
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Si el usuario se elimina, su perfil también se eliminará (on_delete=models.CASCADE).
    alert_cripto = models.ForeignKey(Cripto, on_delete=models.SET_NULL, null=True, blank=True)  # Cripto a monitorear
    alert_price = models.FloatField(null=True, blank=True)  # Precio de alerta
    receive_alerts = models.BooleanField(default=False)  # Activar o desactivar alertas
    
    
    def __str__(self):
        return self.user.username
