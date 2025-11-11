from django.db import models

# -------------------------------------------------------------------------
# PROVEEDORES
# -------------------------------------------------------------------------

class ProveedorInternet(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Proveedor de Internet"
        verbose_name_plural = "Proveedores de Internet"

    def __str__(self):
        return self.nombre


class ProveedorPisoTecnologico(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Proveedor de Piso Tecnológico"
        verbose_name_plural = "Proveedores de Piso Tecnológico"

    def __str__(self):
        return self.nombre


# -------------------------------------------------------------------------
# CATÁLOGOS GENERALES
# -------------------------------------------------------------------------

class Region(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Distrito(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Ambito(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Dependencia(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Turno(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class MetodoSolicitud(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class EstadoConectividad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class TipoEstablecimiento(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nombre


class TipoPisoTecnologico(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre


class PlanPiso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre


# -------------------------------------------------------------------------
# MODELOS PRINCIPALES DEL SISTEMA
# -------------------------------------------------------------------------

class Predio(models.Model):
    numero_predio = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.numero_predio)


class Escuela(models.Model):
    cue = models.CharField(max_length=50, unique=True)
    clave_provincial = models.CharField(max_length=60, blank=True, null=True)

    nombre = models.CharField(max_length=400)
    direccion = models.CharField(max_length=200)
    matricula = models.IntegerField(default=0)

    tiene_internet = models.BooleanField(default=False)
    tiene_piso_tecnologico = models.BooleanField(default=False)

    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    predio = models.ForeignKey(Predio, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    distrito = models.ForeignKey(Distrito, on_delete=models.SET_NULL, null=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)

    ambito = models.ForeignKey(Ambito, on_delete=models.SET_NULL, null=True)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.SET_NULL, null=True)
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    tipo_establecimiento = models.ForeignKey(TipoEstablecimiento, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre


# -------------------------------------------------------------------------
# SERVICIOS Y PISO TECNOLÓGICO
# -------------------------------------------------------------------------

class ServicioConectividad(models.Model):
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)
    estado_conectividad = models.ForeignKey(EstadoConectividad, on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey(ProveedorInternet, on_delete=models.SET_NULL, null=True)

    velocidad_mbps = models.IntegerField(default=0)
    fecha_instalacion = models.DateField(blank=True, null=True)
    fecha_mejora = models.DateField(blank=True, null=True)

    metodo_solicitud = models.ForeignKey(MetodoSolicitud, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Servicio de {self.escuela.nombre}"


class PisoTecnologico(models.Model):
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)
    plan_piso = models.ForeignKey(PlanPiso, on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey(ProveedorPisoTecnologico, on_delete=models.SET_NULL, null=True)

    tipo_piso_instalado = models.ForeignKey(TipoPisoTecnologico, on_delete=models.SET_NULL, null=True)
    fecha_terminado = models.DateField(blank=True, null=True)

    tipo_mejora = models.CharField(max_length=100, blank=True, null=True)
    fecha_mejora = models.DateField(blank=True, null=True)

    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Piso Tecnológico en {self.escuela.nombre}"
