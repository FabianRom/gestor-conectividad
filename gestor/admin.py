from django.contrib import admin

from .models import (
    Escuela,
    Region,
    Distrito,
    Ciudad,
    Ambito,
    Dependencia,
    Turno,
    Categoria,
    TipoEstablecimiento,
    ProveedorInternet,
    ProveedorPisoTecnologico,
    EstadoConectividad,
    Predio,
    ServicioConectividad,
    PisoTecnologico,
    TipoPisoTecnologico,
    PlanPiso,
    MetodoSolicitud,
)

# ---------------------------------------------------------------------
# INLINES (formularios anidados)
# ---------------------------------------------------------------------

class ServicioConectividadInline(admin.TabularInline):
    """Formulario inline para ServicioConectividad dentro de Escuela."""
    model = ServicioConectividad
    extra = 1
    raw_id_fields = ('proveedor',)


class PisoTecnologicoInline(admin.TabularInline):
    """Formulario inline para PisoTecnologico dentro de Escuela."""
    model = PisoTecnologico
    extra = 1
    raw_id_fields = ('proveedor',)


# ---------------------------------------------------------------------
# ADMIN PRINCIPALES
# ---------------------------------------------------------------------

class EscuelaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'cue',
        'tiene_internet',
        'tiene_piso_tecnologico',
        'region',
        'distrito',
    )
    search_fields = ('cue', 'nombre')
    list_filter = (
        'region',
        'distrito',
        'categoria',
        'tiene_internet',
        'tiene_piso_tecnologico',
    )
    inlines = [ServicioConectividadInline, PisoTecnologicoInline]

    raw_id_fields = (
        'predio',
        'region',
        'distrito',
        'ciudad',
        'ambito',
        'dependencia',
        'turno',
        'categoria',
        'tipo_establecimiento',
    )


class PredioAdmin(admin.ModelAdmin):
    list_display = ('numero_predio',)


class ServicioConectividadAdmin(admin.ModelAdmin):
    list_display = ('escuela', 'proveedor', 'estado_conectividad', 'velocidad_mbps')
    list_filter = ('proveedor', 'estado_conectividad')
    search_fields = ('escuela__nombre', 'escuela__cue')


class PisoTecnologicoAdmin(admin.ModelAdmin):
    list_display = ('escuela', 'proveedor', 'tipo_piso_instalado', 'fecha_terminado')
    list_filter = ('proveedor', 'tipo_piso_instalado')
    search_fields = ('escuela__nombre', 'escuela__cue')


class PlanPisoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(MetodoSolicitud)
class MetodoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


# ---------------------------------------------------------------------
# REGISTRO DE MODELOS
# ---------------------------------------------------------------------

# Principales
admin.site.register(Escuela, EscuelaAdmin)
admin.site.register(Predio, PredioAdmin)

# Catálogos
admin.site.register(Region)
admin.site.register(Distrito)
admin.site.register(Ciudad)
admin.site.register(Ambito)
admin.site.register(Dependencia)
admin.site.register(Turno)
admin.site.register(Categoria)
admin.site.register(TipoEstablecimiento)

# Proveedores
admin.site.register(ProveedorInternet)
admin.site.register(ProveedorPisoTecnologico)

# Conectividad
admin.site.register(EstadoConectividad)
admin.site.register(ServicioConectividad, ServicioConectividadAdmin)
admin.site.register(PisoTecnologico, PisoTecnologicoAdmin)

# Otros
admin.site.register(TipoPisoTecnologico)
admin.site.register(PlanPiso, PlanPisoAdmin)
