#import_escuelas.py

import csv
from django.core.management.base import BaseCommand
from gestor.models import (
    Escuela, Predio, Region, Distrito, Ciudad, Ambito, Dependencia, Turno, Categoria, TipoEstablecimiento,
    ServicioConectividad, Proveedor, EstadoConectividad, MetodoSolicitud,
    PisoTecnologico, PlanPiso, TipoPisoTecnologico
)
from django.db import transaction
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Importa datos de escuelas y sus servicios desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='La ruta del archivo CSV a importar')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.stdout.write(self.style.SUCCESS('Iniciando importación masiva...'))

                with transaction.atomic():
                    for row in reader:
                        # 1. Obtener o crear los objetos de las tablas de catálogo
                        try:
                            numero_predio = int(row.get('predio', '0'))
                        except (ValueError, TypeError):
                            numero_predio = 0
                        predio_obj, _ = Predio.objects.get_or_create(numero_predio=numero_predio)
                        region_obj, _ = Region.objects.get_or_create(nombre=row['region'])
                        distrito_obj, _ = Distrito.objects.get_or_create(nombre=row['distrito'])
                        ciudad_obj, _ = Ciudad.objects.get_or_create(nombre=row['ciudad'])
                        ambito_obj, _ = Ambito.objects.get_or_create(nombre=row['ambito'])
                        dependencia_obj, _ = Dependencia.objects.get_or_create(nombre=row['dependencia'])
                        turno_obj, _ = Turno.objects.get_or_create(nombre=row['turno'])
                        categoria_obj, _ = Categoria.objects.get_or_create(nombre=row['categoria'])
                        tipo_establecimiento_obj, _ = TipoEstablecimiento.objects.get_or_create(nombre=row['tipo_establecimiento'])

                        # 2. Crear o actualizar el objeto Escuela
                        try:
                            matricula_val = int(row.get('matricula', 0))
                        except (ValueError, TypeError):
                            self.stdout.write(self.style.WARNING(f"Valor de 'matricula' inválido para la escuela {row.get('nombre')}. Usando 0."))
                            matricula_val = 0

                        try:
                            latitud_val = float(row.get('latitud')) if row.get('latitud') else None
                        except (ValueError, TypeError):
                            self.stdout.write(self.style.WARNING(f"Valor de 'latitud' inválido para la escuela {row.get('nombre')}. Usando None."))
                            latitud_val = None

                        try:
                            longitud_val = float(row.get('longitud')) if row.get('longitud') else None
                        except (ValueError, TypeError):
                            self.stdout.write(self.style.WARNING(f"Valor de 'longitud' inválido para la escuela {row.get('nombre')}. Usando None."))
                            longitud_val = None
                        
                        escuela, created = Escuela.objects.update_or_create(
                            cue=row['cue'],
                            defaults={
                                'clave_provincial': row.get('clave_provincial'),
                                'nombre': row.get('nombre'),
                                'direccion': row.get('direccion'),
                                'coordenadas': row.get('coordenadas'),
                                'matricula': matricula_val,
                                'tiene_internet': row.get('tiene_internet', '').lower() == 'si',
                                'tiene_piso_tecnologico': row.get('tiene_piso_tecnologico', '').lower() == 'si',
                                'latitud': latitud_val,
                                'longitud': longitud_val,
                                'predio': predio_obj,
                                'region': region_obj,
                                'distrito': distrito_obj,
                                'ciudad': ciudad_obj,
                                'ambito': ambito_obj,
                                'dependencia': dependencia_obj,
                                'turno': turno_obj,
                                'categoria': categoria_obj,
                                'tipo_establecimiento': tipo_establecimiento_obj
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Escuela {row['nombre']} ({row['cue']}) importada."))
                        else:
                            self.stdout.write(self.style.WARNING(f"Escuela {row['nombre']} ({row['cue']}) actualizada."))

                        # 3. Importar los datos de Servicio de Conectividad (si existen en la fila)
                        if row.get('estado_conectividad') and row.get('proveedor_conectividad'):
                            estado_conectividad_obj, _ = EstadoConectividad.objects.get_or_create(nombre=row['estado_conectividad'])
                            proveedor_conectividad_obj, _ = Proveedor.objects.get_or_create(nombre=row['proveedor_conectividad'])
                            metodo_solicitud_obj = None
                            if row.get('metodo_solicitud'):
                                metodo_solicitud_obj, _ = MetodoSolicitud.objects.get_or_create(nombre=row['metodo_solicitud'])
                            
                            try:
                                velocidad_val = int(row.get('velocidad_mbps', 0))
                            except (ValueError, TypeError):
                                self.stdout.write(self.style.WARNING(f"Valor de 'velocidad_mbps' inválido para la escuela {row.get('nombre')}. Usando 0."))
                                velocidad_val = 0

                            ServicioConectividad.objects.update_or_create(
                                escuela=escuela,
                                defaults={
                                    'estado_conectividad': estado_conectividad_obj,
                                    'proveedor': proveedor_conectividad_obj,
                                    'velocidad_mbps': velocidad_val,
                                    'fecha_instalacion': parse_date(row.get('fecha_instalacion_conectividad')),
                                    'fecha_mejora': parse_date(row.get('fecha_mejora_conectividad')),
                                    'metodo_solicitud': metodo_solicitud_obj,
                                    'observaciones': row.get('observaciones_conectividad')
                                }
                            )
                            self.stdout.write(self.style.NOTICE(f"    - Servicio de conectividad de {escuela.nombre} procesado."))

                        # 4. Importar los datos de Piso Tecnológico (si existen en la fila)
                        if row.get('plan_piso') and row.get('proveedor_piso'):
                            plan_piso_obj, _ = PlanPiso.objects.get_or_create(nombre=row['plan_piso'])
                            proveedor_piso_obj, _ = Proveedor.objects.get_or_create(nombre=row['proveedor_piso'])
                            tipo_piso_obj = None
                            if row.get('tipo_piso_instalado'):
                                tipo_piso_obj, _ = TipoPisoTecnologico.objects.get_or_create(nombre=row['tipo_piso_instalado'])

                            PisoTecnologico.objects.update_or_create(
                                escuela=escuela,
                                defaults={
                                    'plan_piso': plan_piso_obj,
                                    'proveedor': proveedor_piso_obj,
                                    'fecha_terminado': parse_date(row.get('fecha_terminado_piso')),
                                    'tipo_piso_instalado': tipo_piso_obj,
                                    'tipo_mejora': row.get('tipo_mejora'),
                                    'fecha_mejora': parse_date(row.get('fecha_mejora_piso')),
                                    'observaciones': row.get('observaciones_piso')
                                }
                            )
                            self.stdout.write(self.style.NOTICE(f"    - Piso tecnológico de {escuela.nombre} procesado."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'El archivo no se encontró en la ruta especificada: {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nOcurrió un error: {e}'))
            self.stdout.write(self.style.WARNING('La transacción fue revertida. Ningún dato fue guardado.'))