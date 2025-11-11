"""
URL configuration for ges_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# C:\Gestor de Conectividad y Equipamiento Escolar\ges_proyecto\urls.py

from django.contrib import admin
from django.urls import path, include # Asegúrate de que 'include' esté importado aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestor.urls')), # Esta línea es CRUCIAL para que el proyecto encuentre las URLs de tu app 'gestor'
    # Esto define automáticamente 'login', 'logout', etc.
    # ---------------------------------------------------------------
    #path('accounts/', include('django.contrib.auth.urls')),
    
]