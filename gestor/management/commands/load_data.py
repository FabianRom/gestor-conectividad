#gestor/commands/load_data.py
import csv
import os
import decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.conf import settings
from gestor.models import (
    Region, Distrito, Ciudad, Ambito, Dependencia, Turno, Categoria, Proveedor, MetodoSolicitud,
    EstadoConectividad, TipoEstablecimiento, Escuela, Predio, ServicioConectividad,
    TipoPisoTecnologico, PlanPiso, PisoTecnologico
)

# Constantes para los nombres de las columnas en el CSV
COLUMN_MAP = {
    'cue': 'cue',
    'clave_provincial': 'clave_provincial',
    'nombre_escuela': 'nombre',
    'direccion': 'direccion',
    'matricula': 'matricula',
    'latitud': 'latitud',
    'longitud': 'longitud',
    'predio': 'predio',
    'region': 'region',
    'distrito': 'distrito',
    'ciudad': 'ciudad',
    'ambito': 'ambito',
    'dependencia': 'dependencia',
    'turno': 'turno',
    'categoria': 'categoria',
    'tipo_establecimiento': 'tipo_establecimiento',
    'tiene_internet': 'tiene_internet',
    'tiene_piso_tecnologico': 'tiene_piso_tecnologico',
    'estado_conectividad': 'estado_conectividad',
    'proveedor_conectividad': 'proveedor_conectividad',
    'velocidad_mbps': 'velocidad_mbps',
    'fecha_instalacion_conectividad': 'fecha_instalacion_conectividad',
    'fecha_mejora_conectividad': 'fecha_mejora_conectividad',
    'metodo_solicitud': 'metodo_solicitud',
    'observaciones_conectividad': 'observaciones_conectividad',
    'plan_piso': 'plan_piso',
    'proveedor_piso': 'proveedor_piso',
    'fecha_terminado_piso': 'fecha_terminado_piso',
    'tipo_piso_instalado': 'tipo_piso_instalado',
    'tipo_mejora': 'tipo_mejora',
    'fecha_mejora_piso': 'fecha_mejora_piso',
    'observaciones_piso': 'observaciones_piso',
}

# Clases de catálogo para una creación más eficiente
catalogo_clases = {
    'region': Region, 'distrito': Distrito, 'ciudad': Ciudad, 'ambito': Ambito,
    'dependencia': Dependencia, 'turno': Turno, 'categoria': Categoria,
    'tipo_establecimiento': TipoEstablecimiento, 'estado_conectividad': EstadoConectividad,
    'proveedor': Proveedor, 'metodo_solicitud': MetodoSolicitud,
    'tipo_piso_instalado': TipoPisoTecnologico, 'plan_piso': PlanPiso
}

def parse_date(date_string):
    """Intenta parsear una cadena de texto a un objeto de fecha, manejando varios formatos."""
    if not date_string:
        return None
    date_string = date_string.strip()
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    return None

class Command(BaseCommand):
    help = 'Carga datos de escuelas desde un archivo CSV.'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'datos_planos_ final.csv')
        self.stdout.write(self.style.SUCCESS(f'Iniciando la carga de datos desde: {csv_file_path}'))

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado en: {csv_file_path}'))
            return

        total_registros = 0
        registros_procesados = 0
        registros_fallidos = 0
        errores = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    total_registros += 1
                    try:
                        with transaction.atomic():
                            # Limpieza y mapeo de datos
                            datos_mapeados = {
                                'cue': row.get(COLUMN_MAP['cue'], '') or None,
                                'clave_provincial': row.get(COLUMN_MAP['clave_provincial'], '') or None,
                                'nombre': row.get(COLUMN_MAP['nombre_escuela'], '') or None,
                                'direccion': row.get(COLUMN_MAP['direccion'], '') or None,
                                'matricula': row.get(COLUMN_MAP['matricula'], '') or '0',
                                'tiene_internet': row.get('tiene_internet', '').lower() == 'si',
                                'tiene_piso_tecnologico': row.get('tiene_piso_tecnologico', '').lower() == 'si',
                            }
                            
                            # Procesamiento de latitud y longitud
                            latitud_str = row.get(COLUMN_MAP['latitud'], '').strip()
                            longitud_str = row.get(COLUMN_MAP['longitud'], '').strip()

                            latitud = None
                            if latitud_str:
                                try:
                                    latitud = decimal.Decimal(latitud_str)
                                    # Validar que la latitud esté en un rango válido
                                    if not -90 <= latitud <= 90:
                                        raise ValueError("Valor de latitud fuera de rango geográfico válido (-90 a 90).")
                                except (decimal.InvalidOperation, ValueError, TypeError) as e:
                                    self.stdout.write(self.style.WARNING(f"Saltando fila {total_registros} - Latitud inválida: '{latitud_str}'. Motivo: {e}"))
                                    registros_fallidos += 1
                                    continue # Saltar a la siguiente fila

                            longitud = None
                            if longitud_str:
                                try:
                                    longitud = decimal.Decimal(longitud_str)
                                    # Validar que la longitud esté en un rango válido
                                    if not -180 <= longitud <= 180:
                                        raise ValueError("Valor de longitud fuera de rango geográfico válido (-180 a 180).")
                                except (decimal.InvalidOperation, ValueError, TypeError) as e:
                                    self.stdout.write(self.style.WARNING(f"Saltando fila {total_registros} - Longitud inválida: '{longitud_str}'. Motivo: {e}"))
                                    registros_fallidos += 1
                                    continue # Saltar a la siguiente fila


                            # --- Creación de modelos de catálogo (Foreing Keys) ---
                            predio_obj, _ = Predio.objects.get_or_create(numero_predio=row.get(COLUMN_MAP['predio']))

                            # Procesamiento de campos de catálogos
                            for campo, modelo in catalogo_clases.items():
                                valor = row.get(campo, '').strip()
                                if valor:
                                    try:
                                        obj, created = modelo.objects.get_or_create(nombre=valor)
                                        datos_mapeados[campo] = obj
                                    except IntegrityError:
                                        # Esto maneja el caso de nombres duplicados, aunque unique=True ya lo previene.
                                        datos_mapeados[campo] = modelo.objects.get(nombre=valor)
                                else:
                                    datos_mapeados[campo] = None


                            # --- Creación o actualización de Escuela ---
                            escuela, created = Escuela.objects.get_or_create(
                                cue=datos_mapeados['cue'],
                                defaults={
                                    'clave_provincial': datos_mapeados['clave_provincial'],
                                    'nombre': datos_mapeados['nombre'],
                                    'direccion': datos_mapeados['direccion'],
                                    'matricula': int(datos_mapeados['matricula'] or 0),
                                    'tiene_internet': datos_mapeados['tiene_internet'],
                                    'tiene_piso_tecnologico': datos_mapeados['tiene_piso_tecnologico'],
                                    'latitud': latitud,
                                    'longitud': longitud,
                                    'predio': predio_obj,
                                    'region': datos_mapeados.get('region'),
                                    'distrito': datos_mapeados.get('distrito'),
                                    'ciudad': datos_mapeados.get('ciudad'),
                                    'ambito': datos_mapeados.get('ambito'),
                                    'dependencia': datos_mapeados.get('dependencia'),
                                    'turno': datos_mapeados.get('turno'),
                                    'categoria': datos_mapeados.get('categoria'),
                                    'tipo_establecimiento': datos_mapeados.get('tipo_establecimiento'),
                                }
                            )

                            if not created:
                                # Actualizar la escuela si ya existe
                                escuela.clave_provincial = datos_mapeados['clave_provincial']
                                escuela.nombre = datos_mapeados['nombre']
                                escuela.direccion = datos_mapeados['direccion']
                                escuela.matricula = int(datos_mapeados['matricula'] or 0)
                                escuela.tiene_internet = datos_mapeados['tiene_internet']
                                escuela.tiene_piso_tecnologico = datos_mapeados['tiene_piso_tecnologico']
                                escuela.latitud = latitud
                                escuela.longitud = longitud
                                escuela.predio = predio_obj
                                escuela.region = datos_mapeados.get('region')
                                escuela.distrito = datos_mapeados.get('distrito')
                                escuela.ciudad = datos_mapeados.get('ciudad')
                                escuela.ambito = datos_mapeados.get('ambito')
                                escuela.dependencia = datos_mapeados.get('dependencia')
                                escuela.turno = datos_mapeados.get('turno')
                                escuela.categoria = datos_mapeados.get('categoria')
                                escuela.tipo_establecimiento = datos_mapeados.get('tipo_establecimiento')
                                escuela.save()

                            # --- Creación o actualización de Servicios de Conectividad ---
                            if datos_mapeados['tiene_internet']:
                                # Elimina registros existentes para evitar errores de duplicidad
                                ServicioConectividad.objects.filter(escuela=escuela).delete()
                                
                                # Crea el nuevo registro
                                ServicioConectividad.objects.create(
                                    escuela=escuela,
                                    estado_conectividad=datos_mapeados.get('estado_conectividad'),
                                    proveedor=datos_mapeados.get('proveedor'),
                                    velocidad_mbps=row.get('velocidad_mbps', '0') or 0,
                                    fecha_instalacion=parse_date(row.get(COLUMN_MAP['fecha_instalacion_conectividad'])),
                                    fecha_mejora=parse_date(row.get(COLUMN_MAP['fecha_mejora_conectividad'])),
                                    metodo_solicitud=datos_mapeados.get('metodo_solicitud'),
                                    observaciones=row.get('observaciones_conectividad') or None,
                                )

                            # --- Creación o actualización de Pisos Tecnológicos ---
                            if datos_mapeados['tiene_piso_tecnologico']:
                                # Elimina registros existentes para evitar errores de duplicidad
                                PisoTecnologico.objects.filter(escuela=escuela).delete()

                                # Crea el nuevo registro
                                PisoTecnologico.objects.create(
                                    escuela=escuela,
                                    plan_piso=datos_mapeados.get('plan_piso'),
                                    proveedor=datos_mapeados.get('proveedor'),
                                    fecha_terminado=parse_date(row.get(COLUMN_MAP['fecha_terminado_piso'])),
                                    tipo_piso_instalado=datos_mapeados.get('tipo_piso_instalado'),
                                    tipo_mejora=row.get('tipo_mejora') or None,
                                    fecha_mejora=parse_date(row.get(COLUMN_MAP['fecha_mejora_piso'])),
                                    observaciones=row.get('observaciones_piso') or None,
                                )

                            registros_procesados += 1
                            if registros_procesados % 1000 == 0:
                                self.stdout.write(f'Llevamos {registros_procesados} registros procesados...')

                    except Exception as e:
                        errores.append({'fila': total_registros, 'error': str(e)})
                        self.stdout.write(self.style.ERROR(f'Ocurrió un error inesperado durante la carga en la fila {total_registros}: {str(e)}'))
                        registros_fallidos += 1
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al leer el archivo CSV: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS('--- Resumen de la carga ---'))
        self.stdout.write(self.style.SUCCESS(f'Registros totales en el archivo: {total_registros}'))
        self.stdout.write(self.style.SUCCESS(f'Registros procesados con éxito: {registros_procesados}'))
        self.stdout.write(self.style.WARNING(f'Registros fallidos: {registros_fallidos}'))

        if errores:
            self.stdout.write(self.style.WARNING('\nDetalles de los errores:'))
            for error in errores:
                self.stdout.write(f'Fila {error["fila"]}: {error["error"]}')
        self.stdout.write(self.style.SUCCESS('Carga de datos finalizada.'))
