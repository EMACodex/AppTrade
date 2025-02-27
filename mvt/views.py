from django.shortcuts import render, redirect
import requests
from .models import *
from django.contrib import messages
from .forms import CriptoForm, PerfilForm, RegistroForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings


"""
Función main
Muestra la página principal donde el usuario puede buscar información sobre una criptomoneda.
Si el usuario ingresa un símbolo de criptomoneda, consulta la API de Pionex para obtener el precio y los datos de trading.
"""
def principal(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').strip()
        if not ticker:
            messages.error(request, "Introduce un símbolo de criptomoneda válido.")
            return redirect('principal')

        api_url = "https://api.pionex.com/api/v1/market/trades?symbol=" + ticker + "_USDT&limit=1"
        
        try:
            api_request = requests.get(api_url, timeout=5)
            api_data = api_request.json()
            
            if "data" in api_data and "trades" in api_data["data"] and api_data["data"]["trades"]:
                trades = api_data["data"]["trades"]
                for trade in trades:
                    trade["symbol"] = trade["symbol"].replace("_USDT", "")
            else:
                trades = "Error: No se encontraron datos para esta criptomoneda."

        except requests.RequestException:
            trades = "Error: No se pudo conectar con la API."

        return render(request, 'principal.html', {'trades': trades, 'ticker': ticker})
    
    return render(request, 'principal.html', {'ticker': "Introduce el símbolo de una criptomoneda para comenzar..."})


"""
Función para añadir una criptomoneda a la base de datos
Permite al usuario añadir una criptomoneda a la base de datos.
También obtiene y muestra los precios de todas las criptomonedas almacenadas en la base de datos.
"""

def añadirCripto(request):
    if request.method == 'POST':
        form = CriptoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La cripto ha sido añadida!")
            return redirect('añadirCripto')        
    
    ticker_list = Cripto.objects.all().order_by('ticker')
    output = []
    
    for ticker_item in ticker_list:
        api_url = "https://api.pionex.com/api/v1/market/trades?symbol=" + str(ticker_item.ticker) + "_USDT&limit=1"
        try:
            api_request = requests.get(api_url, timeout=5)
            api_data = api_request.json()
            if "data" in api_data and "trades" in api_data["data"] and api_data["data"]["trades"]:
                trades = api_data["data"]["trades"]
                for trade in trades:
                    trade["symbol"] = trade["symbol"].replace("_USDT", "")
                    trade["id"] = ticker_item.id  
            else:
                trades = "Error: No se encontraron datos."
        except requests.RequestException:
            trades = "Error: No se pudo conectar con la API."

        output.append(trades)

    return render(request, 'añadirCripto.html', {'ticker': ticker_list, 'output': output})

"""
Función para eliminar una criptomoneda de la base de datos
Permite eliminar una criptomoneda de la base de datos.
Antes de eliminarla, se asegura de eliminar referencias en perfiles de usuario que la tengan configurada en alertas.
"""
def eliminar(request, cripto_id):
    try:
        item = Cripto.objects.get(id=cripto_id)
        
        UserProfile.objects.filter(alert_cripto=item).update(alert_cripto=None)  

        item.delete()  
        messages.success(request, "La cripto ha sido eliminada!")
    except Cripto.DoesNotExist:
        messages.error(request, "No se encontró la cripto a eliminar.")
    except IntegrityError:
        messages.error(request, "No se puede eliminar la cripto porque está en uso.")
    
    return redirect('añadirCripto')


"""
Función del perfil del usuario (requiere autenticación)
Permite al usuario ver y actualizar su perfil.
Se puede modificar el nombre y el correo electrónico.
"""
@login_required
def perfil(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=user_profile, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.email = form.cleaned_data['email']
            user.save()  
            user_profile.save()  

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')

    else:
        form = PerfilForm(instance=user_profile, user=user)

    return render(request, 'perfil.html', {'form': form})



"""
Función para iniciar sesión
Permite al usuario iniciar sesión en la aplicación.
Si las credenciales son correctas, redirige a la página principal.
"""
def verLogin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Inicio de sesión exitoso.")
                return redirect('principal')
        messages.error(request, "Usuario o contraseña incorrectos.")
    
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

"""
Función para registrar un nuevo usuario
Permite registrar un nuevo usuario en la aplicación.
Tras registrarse, el usuario inicia sesión automáticamente.
"""
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('principal')
        else:
            messages.error(request, "Todos los campos son obligatorios. Por favor, complétalos.")

    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})

    
"""
Función para obtener el precio de una criptomoneda desde la API de Pionex
Consulta la API de Pionex y devuelve el precio actual de una criptomoneda.
"""
def obtenerPrecioCripto(ticker):
    api_url = "https://api.pionex.com/api/v1/market/trades?symbol=" + ticker + "_USDT&limit=1"
    
    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()

        if "data" in data and "trades" in data["data"] and data["data"]["trades"]:
            return round(float(data["data"]["trades"][0]["price"]), 2)  # Redondeo a 2 decimales

    except requests.RequestException:
        return None  

    return None  

"""
Endpoint para obtener información del precio para la gráfica
Endpoint Django que devuelve el precio de una criptomoneda en formato JSON.
También obtiene detalles de la última transacción registrada en la API de Pionex.
"""
def obtenerPrecio(request, ticker):
    price = obtenerPrecioCripto(ticker)
    
    api_url = "https://api.pionex.com/api/v1/market/trades?symbol=" + ticker + "_USDT&limit=1"
    trade_data = {}

    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()

        if data.get("data", {}).get("trades"):
            trade = data["data"]["trades"][0]  
            trade_data = {
                'tradeId': trade["tradeId"],
                'price': round(float(trade["price"]), 2),
                'size': trade["size"]
            }

    except requests.RequestException:
        return JsonResponse({'error': 'No se pudo obtener la información de la API'}, status=500)

    response_data = {'price': price} if price is not None else {'error': 'No se pudo obtener el precio'}
    response_data.update(trade_data)

    return JsonResponse(response_data if trade_data else {**response_data, 'error': 'Datos no encontrados'}, status=200 if trade_data or price is not None else 404)

"""
Función para comprobar alertas de precios y enviar notificaciones por correo
Revisa si alguna criptomoneda ha alcanzado el precio configurado por el usuario y envía una alerta por correo.
"""
def comprobarAlertas():
    users = UserProfile.objects.filter(receive_alerts=True, alert_cripto__isnull=False, alert_price__isnull=False)

    for user in users:
        ticker = user.alert_cripto.ticker
        price = obtenerPrecioCripto(ticker)

        if price and price > user.alert_price:
            send_mail(
                "Alerta de Criptomoneda",
                "La criptomoneda " + ticker + " ha superado el precio de " + str(user.alert_price) + " USD. Precio actual: " + str(price) + " USD.",
                settings.DEFAULT_FROM_EMAIL,
                [user.user.email],
                fail_silently=False,
            )

"""
Endpoint para verificar alertas manualmente
Llama a comprobarAlertas() y devuelve un JSON confirmando la verificación.

un endpoint es una URL específica dentro de una API que permite a los clientes interactuar con el servidor y acceder a ciertos datos.
"""

@login_required
def verificaralerta(request):
    comprobarAlertas()
    return JsonResponse({'status': 'checked'})
