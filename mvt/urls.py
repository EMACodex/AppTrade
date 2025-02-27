from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import *


urlpatterns = [
    path('principal', views.principal, name="principal"),# Ruta que muestra la página principal donde se pueden buscar criptomonedas.
    path('obtenerPrecio/<str:ticker>/', views.obtenerPrecio, name='obtenerPrecio'),  # Ruta de un endpoint que obtiene el precio de una criptomoneda en función del ticker proporcionado.
    path('verificaralerta/', verificaralerta, name='verificaralerta'), #Esta url es necesaria para que se envien los correos
    path('perfil', views.perfil, name="perfil"), # Ruta que muestra y permite editar el perfil del usuario.
    path('añadirCripto', views.añadirCripto, name="añadirCripto"), # Ruta que permite añadir nuevas criptomonedas a la base de datos.
    path('eliminar/<int:cripto_id>/', views.eliminar, name='eliminar'), # Ruta que permite eliminar una criptomoneda específica de la base de datos, identificada por su ID.
    path('', views.verLogin, name='login'), # Ruta que carga la página de inicio de sesión. Si no hay una sesión activa, redirige a esta página.
    path('registro/', views.registro, name='registro'), # Ruta que carga la página de registro para crear una nueva cuenta de usuario.
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), # Ruta que cierra la sesión del usuario y lo redirige a la página de inicio de sesión.
    ]