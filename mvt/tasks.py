from django.core.mail import send_mail
from .models import UserProfile
import requests

def alerta_precio(user_profile_id):
    try:
        user_profile = UserProfile.objects.get(id=user_profile_id)

        if user_profile.receive_alerts and user_profile.alert_cripto and user_profile.alert_price:
            cripto = user_profile.alert_cripto
            api_url = f"https://api.pionex.com/api/v1/market/trades?symbol={cripto.ticker}_USDT&limit=1"

            response = requests.get(api_url)
            data = response.json()

            if "data" in data and "trades" in data["data"] and len(data["data"]["trades"]) > 0:
                trade = data["data"]["trades"][0]
                current_price = float(trade["price"])

                if current_price > float(user_profile.alert_price):
                    send_mail(
                        'Alerta de precio',
                        f"El precio de {cripto.ticker} ha superado el límite de {user_profile.alert_price}. El precio actual es {current_price}.",
                        'admin@TradingApp.com',
                        [user_profile.user.email],  # Corregido aquí
                        fail_silently=False,
                    )
    except Exception as e:
        print(f"Error al verificar la alerta de precio: {e}")
