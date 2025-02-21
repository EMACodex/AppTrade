from django.core.mail import send_mail
from django.conf import settings

def enviar_alerta_email(usuario_email, cripto, precio_actual, precio_objetivo):
    subject = f"¡Alerta! {cripto} ha alcanzado los ${precio_objetivo}"
    message = f"Hola,\n\nLa criptomoneda {cripto} ha alcanzado un precio de ${precio_actual}, superando el límite que configuraste de ${precio_objetivo}.\n\n¡Revisa el mercado y toma acción!\n\nSaludos, \nEquipo de TradingApp"
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [usuario_email])
