# gestor/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # --- NAVEGACIÓN PRINCIPAL ---
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('escuelas/lista/', views.lista_escuelas, name='lista_escuelas'),

    # --- BÚSQUEDA Y DETALLE DE ESCUELAS ---
    path('busqueda/', views.busqueda, name='busqueda'),
    path('resultados_busqueda/', views.resultados_busqueda, name='resultados_busqueda'),
    path('escuela/<str:cue>/', views.detalle_escuela, name='detalle_escuela'),

    # --- AJAX / ENDPOINTS DINÁMICOS ---
    path('ajax/cargar-distritos/', views.ajax_cargar_distritos, name='ajax_cargar_distritos'),

    # --- REPORTES ---
    path('reportes/', views.reportes_generales, name='reportes_generales'),
    path('reportes/internet/', views.reporte_internet, name='reporte_internet'),
    path('reportes/piso/', views.reporte_piso, name='reporte_piso'),

    # --- MAPAS ---
    path('mapa/', views.mapa_escuelas_colores, name='mapa_escuelas_colores'),
    path('mapa-escuelas-con-internet/', views.mapa_escuelas_con_internet, name='mapa_escuelas_con_internet'),

    # --- HERRAMIENTAS DE DATOS ---
    path('datos/', views.carga_descarga_view, name='carga_descarga_url'),
    path('datos/importar/', views.importar_datos, name='importar_datos'),
    path('datos/exportar/', views.exportar_datos, name='exportar_datos'),
    path('datos/plantilla/', views.descargar_plantilla, name='descargar_plantilla'),

    # --- EXPORTACIONES ---
    path('escuela/<str:cue>/generar_excel/', views.generar_excel_escuela, name='generar_excel_escuela'),
    path('exportar_resultados/', views.exportar_resultados_excel, name='exportar_resultados'),
    path('reportes/exportar/', views.exportar_reporte_excel, name='exportar_reporte_excel'),
    
    # --- Api Escuelas para mapa 
    path('api/escuela/<str:cue>/', views.api_escuela, name='api_escuela'),
    path("api/escuelas/bounds/", views.api_escuelas_bounds, name="api_escuelas_bounds"),
    



]
