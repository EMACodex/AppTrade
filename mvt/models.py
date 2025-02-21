from django.db import models
from django.contrib.auth.models import User

class Cripto(models.Model):
    ticker = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.ticker

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    CURRENCY_CHOICES = [
        ('USD', 'USD - Dólar estadounidense'),
        ('EUR', 'EUR - Euro'),
        ('BTC', 'BTC - Bitcoin'),
        ('JPY', 'JPY - Yen japonés'),
        ('GBP', 'GBP - Libra esterlina'),
        ('AUD', 'AUD - Dólar australiano'),
        ('CAD', 'CAD - Dólar canadiense'),
        ('CHF', 'CHF - Franco suizo'),
        ('CNH', 'CNH - Yuan chino'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')

    COUNTRY_CHOICES = [
        ('ES', 'España'), ('FR', 'Francia'), ('DE', 'Alemania'),
        ('IT', 'Italia'), ('NL', 'Países Bajos'), ('BE', 'Bélgica'),
        ('PT', 'Portugal'), ('SE', 'Suecia'), ('AT', 'Austria'),
        ('FI', 'Finlandia'), ('DK', 'Dinamarca'), ('PL', 'Polonia'),
        ('IE', 'Irlanda'), ('GR', 'Grecia'), ('CZ', 'República Checa'),
        ('HU', 'Hungría'), ('SK', 'Eslovaquia'), ('RO', 'Rumanía'),
    ]
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)

    receive_alerts = models.BooleanField(default=False)
    alert_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    alert_cripto = models.ForeignKey(Cripto, null=True, blank=True, on_delete=models.SET_NULL, related_name="user_alerts")

    def __str__(self):
        return self.user.username
