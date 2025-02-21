from django.shortcuts import render, redirect
import requests
from .models import Cripto, UserProfile
from django.contrib import messages
from .forms import CriptoForm, PerfilForm, RegistroForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from.utils import *
from django.http import JsonResponse

def home(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').strip()
        if not ticker:
            messages.error(request, "Introduce un símbolo de criptomoneda válido.")
            return redirect('home')

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

        return render(request, 'home.html', {'trades': trades, 'ticker': ticker})
    
    return render(request, 'home.html', {'ticker': "Introduce el símbolo de una criptomoneda para comenzar..."})




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
        api_url = f"https://api.pionex.com/api/v1/market/trades?symbol={str(ticker_item.ticker)}_USDT&limit=1"
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


def delete(request, cripto_id):
    try:
        item = Cripto.objects.get(id=cripto_id)
        item.delete()
        messages.success(request, "La cripto ha sido eliminada!")
    except Cripto.DoesNotExist:
        messages.error(request, "No se encontró la cripto a eliminar.")
    return redirect('añadirCripto')



@login_required
def perfil(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=user_profile, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.email = form.cleaned_data['email']
            user.save()  # Guardar cambios en User
            user_profile.save()  # Guardar perfil

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')

    else:
        form = PerfilForm(instance=user_profile, user=user)

    return render(request, 'perfil.html', {'form': form})





def precio_cripto(symbol):
    api_url = f"https://api.pionex.com/api/v1/market/trades?symbol={symbol}_USDT&limit=1"
    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()
        if "data" in data and "trades" in data["data"]:
            trades = data["data"]["trades"]
            if trades:
                return float(trades[0]["price"])  
        return None  
    except requests.RequestException:
        return None  


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Inicio de sesión exitoso.")
                return redirect('home')
        messages.error(request, "Usuario o contraseña incorrectos.")
    
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Asegurar que no se cree un perfil duplicado
            UserProfile.objects.get_or_create(user=user)  

            login(request, user)
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('home')
        else:
            messages.error(request, "Hubo un error en el registro. Por favor, revisa los datos.")
    else:
        form = RegistroForm()

    return render(request, 'register.html', {'form': form})

def revisar_alertas():
    usuarios_con_alertas = UserProfile.objects.filter(receive_alerts=True, alert_price__isnull=False, alert_cripto__isnull=False)

    for usuario in usuarios_con_alertas:
        cripto = usuario.alert_cripto.ticker
        precio_objetivo = usuario.alert_price
        precio_actual = precio_cripto(cripto)  # Obtiene el precio actual con tu función existente

        if precio_actual and precio_actual >= precio_objetivo:
            enviar_alerta_email(usuario.user.email, cripto, precio_actual, precio_objetivo)


def enviar_alerta_email(usuario_email, cripto_ticker, precio_actual):
    # Asunto y mensaje del correo
    subject = f"Alerta: {cripto_ticker} ha superado el precio de alerta"
    message = f"El precio de {cripto_ticker} ha alcanzado {precio_actual} USDT, que es superior al precio de alerta que configuraste."
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Asegúrate de que esta esté configurada correctamente en settings.py
        [usuario_email],
        fail_silently=False,
    )
    
    
def get_price(request, ticker):
    price = precio_cripto(ticker)  # Usamos tu función existente para obtener el precio
    if price is not None:
        return JsonResponse({'price': price})
    return JsonResponse({'error': 'No se pudo obtener el precio'}, status=500)