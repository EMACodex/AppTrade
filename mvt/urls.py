from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('home', views.home, name="home"),
    path('get_price/<str:ticker>/', views.get_price, name='get_price'),  # endpoint para obtener el precio
    path('perfil', views.perfil, name="perfil"),
    path('añadirCripto', views.añadirCripto, name="añadirCripto"),
    path('delete/<int:cripto_id>/', views.delete, name='delete'),
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    ]