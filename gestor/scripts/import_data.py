import csv
import os
from datetime import datetime
from decimal import Decimal

# Importa todos tus modelos necesarios
from gestor.models import (
    Escuela,
    Region,
    Distrito,
    Ciudad,
    Ambito,
    Dependencia,
    Turno,
    Categoria,
    TipoEstablecimiento,
    Predio,
    Proveedor,
    EstadoConectividad,
    ServicioConectividad,
    PisoTecnologico,
    TipoPisoTecnologico,
    PlanPiso,
    MetodoSolicitud
)

# --- CONFIGURACIÓN ---
CSV_FILE_PATH = 'datos_planos_ final.csv'

# Mapeo de columnas del CSV a los campos de tus modelos.
# He añadido los nuevos campos que definiste en models.py.
COLUMN_MAPPING = {
    'cue': 'cue',
    'clave_provincial': 'clave_provincial',
    'nombre': 'nombre',
    'direccion': 'direccion',
    'coordenadas': 'coordenadas',
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
    'proveedor_conectividad': 'proveedor',
    'velocidad_mbps': 'velocidad_mbps',
    'fecha_instalacion': 'fecha_instalacion', 
    'fecha_mejora_conectividad': 'fecha_mejora', 
    'metodo_solicitud': 'metodo_solicitud',
    'observaciones_conectividad': 'observaciones',
    'plan_piso': 'plan_piso',
    'proveedor_piso': 'proveedor',
    'fecha_terminado_piso': 'fecha_terminado', 
    'tipo_piso_instalado': 'tipo_piso_instalado',
    'tipo_mejora_piso': 'tipo_mejora',
    'fecha_mejora_piso': 'fecha_mejora',
    'observaciones_piso': 'observaciones',
}

print("Iniciando la carga de datos...")

def load_data():
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            next(reader)  # Saltar la primera fila de encabezados "amigables"
            next(reader)  # Saltar la segunda fila de encabezados con los nombres reales

            total_rows = 0
            skipped_rows = 0
            for row in reader:
                total_rows += 1
                
                # Campos obligatorios para crear una escuela
                cue = row.get(COLUMN_MAPPING['cue'])
                nombre = row.get(COLUMN_MAPPING['nombre'])
                direccion = row.get(COLUMN_MAPPING['direccion'])
                matricula_str = row.get(COLUMN_MAPPING['matricula'])
                
                # Manejo de la matrícula
                try:
                    matricula = int(matricula_str) if matricula_str else 0
                except (ValueError, TypeError):
                    matricula = 0
                
                if not all([cue, nombre, direccion]):
                    print(f"Saltando fila {total_rows} - Faltan datos obligatorios para la escuela.")
                    skipped_rows += 1
                    continue
                
                # --- 1. Obtener o Crear modelos de catálogo (claves foráneas) ---
                region, _ = Region.objects.get_or_create(nombre=row.get('region', 'Sin datos'))
                distrito, _ = Distrito.objects.get_or_create(nombre=row.get('distrito', 'Sin datos'))
                ciudad, _ = Ciudad.objects.get_or_create(nombre=row.get('ciudad', 'Sin datos'))
                ambito, _ = Ambito.objects.get_or_create(nombre=row.get('ambito', 'Sin datos'))
                dependencia, _ = Dependencia.objects.get_or_create(nombre=row.get('dependencia', 'Sin datos'))
                turno, _ = Turno.objects.get_or_create(nombre=row.get('turno', 'Sin datos'))
                categoria, _ = Categoria.objects.get_or_create(nombre=row.get('categoria', 'Sin datos'))
                tipo_establecimiento, _ = TipoEstablecimiento.objects.get_or_create(nombre=row.get('tipo_establecimiento', 'Sin datos'))
                
                predio_nombre = row.get('predio', 'Sin datos')
                predio, _ = Predio.objects.get_or_create(numero_predio=predio_nombre)
                
                # --- 2. Crear o Actualizar el modelo Escuela ---
                try:
                    latitud = Decimal(row.get('latitud')) if row.get('latitud') else None
                    longitud = Decimal(row.get('longitud')) if row.get('longitud') else None
                except (ValueError, TypeError):
                    latitud = None
                    longitud = None

                escuela_data = {
                    'cue': cue,
                    'clave_provincial': row.get('clave_provincial'),
                    'nombre': nombre,
                    'direccion': direccion,
                    'coordenadas': row.get('coordenadas'),
                    'matricula': matricula,
                    'latitud': latitud,
                    'longitud': longitud,
                    'predio': predio,
                    'region': region,
                    'distrito': distrito,
                    'ciudad': ciudad,
                    'ambito': ambito,
                    'dependencia': dependencia,
                    'turno': turno,
                    'categoria': categoria,
                    'tipo_establecimiento': tipo_establecimiento,
                    'tiene_internet': row.get('tiene_internet', '').upper() == 'SI',
                    'tiene_piso_tecnologico': row.get('tiene_piso_tecnologico', '').upper() == 'SI',
                }
                escuela, created = Escuela.objects.update_or_create(cue=escuela_data['cue'], defaults=escuela_data)
                
                # --- 3. Crear modelos de Conectividad y Piso Tecnológico ---
                if escuela_data['tiene_internet']:
                    proveedor_conectividad, _ = Proveedor.objects.get_or_create(nombre=row.get('proveedor_conectividad', 'Sin datos'))
                    estado_conectividad, _ = EstadoConectividad.objects.get_or_create(nombre=row.get('estado_conectividad', 'Sin datos'))
                    metodo_solicitud, _ = MetodoSolicitud.objects.get_or_create(nombre=row.get('metodo_solicitud', 'Sin datos'))
                    
                    try:
                        velocidad_mbps = int(row.get('velocidad_mbps')) if row.get('velocidad_mbps') else 0
                    except (ValueError, TypeError):
                        velocidad_mbps = 0

                    ServicioConectividad.objects.create(
                        escuela=escuela,
                        proveedor=proveedor_conectividad,
                        estado_conectividad=estado_conectividad,
                        velocidad_mbps=velocidad_mbps,
                        fecha_instalacion=row.get('fecha_instalacion') or None,
                        fecha_mejora=row.get('fecha_mejora') or None,
                        metodo_solicitud=metodo_solicitud,
                        observaciones=row.get('observaciones_conectividad'),
                    )
                
                if escuela_data['tiene_piso_tecnologico']:
                    proveedor_piso, _ = Proveedor.objects.get_or_create(nombre=row.get('proveedor_piso', 'Sin datos'))
                    tipo_piso, _ = TipoPisoTecnologico.objects.get_or_create(nombre=row.get('tipo_piso_instalado', 'Sin datos'))
                    plan_piso, _ = PlanPiso.objects.get_or_create(nombre=row.get('plan_piso', 'Sin datos'))
                    
                    PisoTecnologico.objects.create(
                        escuela=escuela,
                        proveedor=proveedor_piso,
                        tipo_piso_instalado=tipo_piso,
                        fecha_terminado=row.get('fecha_terminado_piso') or None,
                        plan_piso=plan_piso,
                        tipo_mejora=row.get('tipo_mejora_piso'),
                        fecha_mejora=row.get('fecha_mejora_piso') or None,
                        observaciones=row.get('observaciones_piso'),
                    )
                
                if total_rows % 100 == 0:
                    print(f"Llevamos {total_rows - skipped_rows} registros procesados...")

            print(f"¡Carga de datos finalizada! Se procesaron {total_rows - skipped_rows} registros. Se omitieron {skipped_rows} filas.")
            
    except FileNotFoundError:
        print(f"Error: El archivo '{CSV_FILE_PATH}' no se encontró. Asegúrate de que esté en la misma carpeta.")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la carga: {e}")
        
load_data()