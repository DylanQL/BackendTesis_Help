from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
"""Core models for the VOT system.

This module defines the main domain models used across the application:
- Empresa, CustomUser and related geographic/project models
- Reporte and its detail models for postes and predios
- Wizard helper models used during multi-step data entry

Keep models small and avoid business logic that belongs in services or forms.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..managers import CustomUserManager
import uuid
from django.conf import settings

class Empresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ruc = models.CharField(max_length=11, unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    estado_activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nombre

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('superadmin', 'Superadministrador'),
        ('admin', 'Administrador Local'),
        ('supervisor', 'Supervisor'),
        ('encargado', 'Encargado'),
    )
    ESTADO_CONTRASENA = (
        ('por_defecto', 'Por defecto'),
        ('cambiada', 'Cambiada'),
    )
    ESTADO_USUARIO = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    dni = models.CharField(max_length=8, unique=True)
    email = models.EmailField(unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    celular = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROLES)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'rol': 'supervisor'}, related_name='encargados')
    estado_contrasena = models.CharField(max_length=20, choices=ESTADO_CONTRASENA, default='por_defecto')
    estado = models.CharField(max_length=10, choices=ESTADO_USUARIO, default='activo')
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    sectores = models.ManyToManyField('Sector', blank=True, related_name='supervisores')

    USERNAME_FIELD = 'dni'
    REQUIRED_FIELDS = ['email', 'nombres', 'apellidos']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.dni} - {self.nombres} {self.apellidos} ({self.get_rol_display()})"

# Proyecto, Zona, Sector
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"

# NUEVO: Distrito
class Distrito(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)  # opcional si manejas multi-empresa
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Cambios en Zona y Sector
class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, blank=True)  # ← cambia aquí
    distrito = models.ForeignKey('Distrito', on_delete=models.CASCADE, null=True, blank=True, related_name='zonas')  # ← NUEVO
    def __str__(self):
        # Prefiere mostrar distrito si existe
        prefix = self.distrito.nombre if self.distrito_id else self.proyecto.nombre
        return f"{self.nombre} - {prefix}"

class Sector(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='sectores')  # ← related_name agregado
    def __str__(self):
        return f"{self.nombre} - {self.zona.nombre}"
# Modelos de catálogo (desplegables dinámicos)
class TipoEstructura(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Material(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class ZonaInstalacion(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Resistencia(models.Model):
    valor = models.CharField(max_length=10)  # Puede ser ND, OTRO, 100, etc.
    def __str__(self):
        return self.valor

class EstadoFisico(models.Model):
    descripcion = models.CharField(max_length=100)
    def __str__(self):
        return self.descripcion

class Inclinacion(models.Model):
    descripcion = models.CharField(max_length=100)
    def __str__(self):
        return self.descripcion

class Propietario(models.Model):
    siglas = models.CharField(max_length=10)
    def __str__(self):
        return self.siglas

class ElementoElectrico(models.Model):
    TIPO_CHOICES = (
        ('electrico', 'Eléctrico'),
        ('telematico', 'Telemático'),
    )
    nombre = models.CharField(max_length=120, unique=True)
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    class Meta:
        db_table = 'elementos'
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class ElementoTelematico(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

# Reporte base
# --- En Reporte: añade el tipo 'predio'
class Reporte(models.Model):
    TIPO_REPORTE = (
        ('electrico', 'Poste Eléctrico'),
        ('telematico', 'Poste Telemático'),
        ('predio', 'Predio'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_REPORTE)

    encargado = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'rol': 'encargado'})
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    fecha_reporte = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    ESTADOS = (("pendiente","Pendiente"), ("registrado","Registrado"), ("observado","Observado"))
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.encargado.email} - {self.fecha_reporte.date()}"

    def clean(self):
        # Exclusividad de detalle por tipo
        has_elec = hasattr(self, 'detalle_electrico') and self.detalle_electrico_id is not None
        has_tel  = hasattr(self, 'detalle_telematico') and self.detalle_telematico_id is not None
        has_pred = hasattr(self, 'detalle_predio') and self.detalle_predio_id is not None

        if self.tipo == 'predio':
            if has_elec or has_tel:
                raise ValidationError("Un reporte 'predio' no puede tener detalle eléctrico/telemático.")
        elif self.tipo == 'electrico':
            if has_tel or has_pred:
                raise ValidationError("Un reporte 'eléctrico' no puede tener detalle telemático/predio.")
        elif self.tipo == 'telematico':
            if has_elec or has_pred:
                raise ValidationError("Un reporte 'telemático' no puede tener detalle eléctrico/predio.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nota: si quieres forzar presencia del detalle después de crear el Reporte, hazlo en la capa de API.
        # 'clean()' se ejecuta si llamas full_clean() o via ModelForm; para forzar, puedes llamar self.full_clean() antes del super().


# Detalles para Poste Eléctrico
class DetallePosteElectrico(models.Model):
    reporte = models.OneToOneField(Reporte, on_delete=models.CASCADE, related_name='detalle_electrico')
    tension = models.CharField(max_length=10)  # BT, MT, AT
    codigo = models.CharField(max_length=50)
    cables_electricos = models.IntegerField(default=0)
    cables_telematicos = models.IntegerField(default=0)
    elementos_electricos = models.ManyToManyField(ElementoElectrico, blank=True)
    elementos_telematicos = models.ManyToManyField(ElementoTelematico, blank=True)
    tipo_estructura = models.ForeignKey(TipoEstructura, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    zona_instalacion = models.ForeignKey(ZonaInstalacion, on_delete=models.SET_NULL, null=True)
    resistencia = models.ForeignKey(Resistencia, on_delete=models.SET_NULL, null=True)
    estado_fisico = models.ForeignKey(EstadoFisico, on_delete=models.SET_NULL, null=True)
    inclinacion = models.ForeignKey(Inclinacion, on_delete=models.SET_NULL, null=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2)
    propietario = models.ForeignKey(Propietario, on_delete=models.SET_NULL, null=True)

# Fotos (estructura flexible)
class FotoReporte(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='fotos_reportes/')
    tipo = models.CharField(max_length=50, blank=True, default="")
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    is_principal = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reporte"],
                condition=models.Q(is_principal=True),
                name="uniq_foto_principal_por_reporte"
            )
        ]



class DetallePredio(models.Model):  # Predio
    ESTADO_REGISTRO = (
        ("registrado", "Registrado"),
        ("observado", "Observado"),
        ("pendiente", "Pendiente"),
    )

    reporte = models.OneToOneField(Reporte, on_delete=models.CASCADE, related_name="detalle_predio")

    # Identificación / localización Elemento
    codigo_sector = models.CharField(max_length=50, blank=True, default="")
    codigo_predio = models.CharField(max_length=50, blank=True, default="", db_index=True)
    via_acceso = models.CharField(max_length=100, blank=True, default="")
    nombre_via_acceso = models.CharField(max_length=150, blank=True, default="")
    numero_municipal = models.CharField(max_length=50, blank=True, default="")  # SN permitido

    # Atributos urbanísticos
    manzana = models.CharField(max_length=20, blank=True, null=True)
    lote = models.IntegerField(blank=True, null=True)
    urbanizacion = models.CharField(max_length=150, blank=True, null=True)
    centro_poblado = models.CharField(max_length=150, blank=True, null=True)

    # Lógica condicional
    caracteristicas_predio_tipo = models.IntegerField(blank=True, null=True, db_index=True)

    # Atributos funcionales
    terreno = models.CharField(max_length=50, blank=True, default="")  # texto libre
    denominacion = models.CharField(max_length=100, blank=True, null=True)         # ← puede ser NULL (tipos 3/4/5)
    nombre_institucion = models.CharField(max_length=150, blank=True, null=True)   # ← puede ser NULL (tipo 6)
    comercio = models.IntegerField(default=0)
    actividad = models.CharField(max_length=100, blank=True, null=True)            # ← puede ser NULL si comercio=0
    vivienda = models.IntegerField(default=0)
    homepass = models.IntegerField(default=0)
    esquina = models.BooleanField(default=False)

    # Estado
    estado_registro = models.CharField(max_length=20, choices=ESTADO_REGISTRO, default="registrado")

    def __str__(self):
        return f"DetallePredio(reporte={self.reporte_id}, codigo_predio={self.codigo_predio})"


#Aqui empieza chango a Predios reporte
class PredioWizard(models.Model):
    ESTADOS = (
        ("started", "Iniciado"),
        ("in_progress", "En progreso"),
        ("ready", "Listo para publicar"),
        ("published", "Publicado"),
        ("expired", "Expirado"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, null=True, blank=True)
 
    # Contexto geográfico
    distrito = models.ForeignKey('Distrito', on_delete=models.CASCADE)
    zona = models.ForeignKey('Zona', on_delete=models.CASCADE)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE)

    # Payloads temporales (se llenan en otros pasos)
    detalle_payload = models.JSONField(default=dict, blank=True)

    # Coordenadas se suben en paso 'coords'PosteElectricoWizard
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    coords_captured_at = models.DateTimeField(null=True, blank=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="started")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

     # <<< añade este campo >>> 
    observaciones = models.TextField(blank=True, default="")
    # payload de detalle

    is_published = models.BooleanField(default=False)

    def mark_in_progress(self):
        if self.estado == "started":
            self.estado = "in_progress"

    def __str__(self):
        return f"Wizard {self.id} ({self.estado}) - Encargado {self.encargado_id}"
    
class PosteElectricoWizard(models.Model):
    TENSION_CHOICES = [
        ('BT', 'Baja Tensión'),
        ('MT', 'Media Tensión'),
        ('AT', 'Alta Tensión'),
    ]
    ESTADOS = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    ]

    encargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='poste_wizards')
    tension = models.CharField(max_length=2, choices=TENSION_CHOICES, null=True, blank=True)
    cables_electricos = models.PositiveIntegerField(null=True, blank=True)
    cables_telematicos = models.PositiveIntegerField(null=True, blank=True)
    codigo = models.CharField(max_length=50, null=True, blank=True)

    # IDs de elementos del catálogo `elementos`
    elementos_electricos = models.JSONField(default=list, blank=True)    # ej: [1,2,3]
    elementos_telematicos = models.JSONField(default=list, blank=True)   # ej: [6,8]

    estado = models.CharField(max_length=10, choices=ESTADOS, default='draft')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado_en']
        indexes = [
            models.Index(fields=['encargado', 'estado']),
        ]

    def __str__(self):
        return f"PosteWizard {self.id} - {self.tension or 'Sin tensión'} - {self.estado}"
    

class ParametroCatalogo(models.Model):
    CATEGORIA_CHOICES = (
        ('estructura', 'Estructura'),
        ('material', 'Material'),
        ('zona_instalacion', 'Zona de instalación'),
        ('resistencia', 'Resistencia'),
    )
    categoria = models.CharField(max_length=32, choices=CATEGORIA_CHOICES, db_index=True)
    nombre = models.CharField(max_length=64)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'parametros_catalogo'
        unique_together = ('categoria', 'nombre')
        ordering = ['categoria', 'orden', 'nombre']

    def __str__(self):
        return f'{self.categoria}: {self.nombre}'

class PosteElectricoWizard_2(models.Model):
    # 🔗 Enlace obligatorio al “wizard grande” (parte 1) PosteElectricoWizard_3
    wizard = models.OneToOneField(
        'PosteElectricoWizard',
        on_delete=models.CASCADE,
        related_name='caracteristicas'   # ahora wizard.caracteristicas → parte 2
    )

    # ❌ Ya no repetimos encargado/estado; se toman del padre
    # ✅ Timestamps propios (útil para trazabilidad por paso)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    # ✅ Campos seleccionables (FK al catálogo)
    estructura = models.ForeignKey('ParametroCatalogo', null=True, blank=True, on_delete=models.PROTECT, related_name='w2_estructura')
    material = models.ForeignKey('ParametroCatalogo', null=True, blank=True, on_delete=models.PROTECT, related_name='w2_material')
    zona_instalacion = models.ForeignKey('ParametroCatalogo', null=True, blank=True, on_delete=models.PROTECT, related_name='w2_zona')
    resistencia = models.ForeignKey('ParametroCatalogo', null=True, blank=True, on_delete=models.PROTECT, related_name='w2_resistencia')

    # Si el usuario escribe un número libre (OTRO), prioriza sobre la FK
    resistencia_valor = models.PositiveIntegerField(null=True, blank=True)

    # (opcional) coordenadas u otros campos
    coordenadas = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-actualizado_en']
        # Un registro de parte 2 por wizard (OneToOne ya lo garantiza)

    def __str__(self):
        return f'PosteWizard2 #{self.id} → Wizard {self.wizard_id}'

class PosteElectricoWizard_3(models.Model):
    wizard = models.OneToOneField(
        'PosteElectricoWizard',
        on_delete=models.CASCADE,
        related_name='condicion'  # wizard.condicion → parte 3
    )
    # Usa los catálogos que SÍ existen en tus modelos:
    estado_poste = models.ForeignKey(EstadoFisico, null=True, blank=True, on_delete=models.PROTECT)
    inclinacion  = models.ForeignKey(Inclinacion,   null=True, blank=True, on_delete=models.PROTECT)
    propietario  = models.ForeignKey(Propietario,   null=True, blank=True, on_delete=models.PROTECT)

    notas = models.TextField(blank=True)
    # Altura del poste en metros (opcional). Usamos DecimalField para precisión.
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado_en']

class PosteElectricoWizard_4(models.Model):
    """
    Parte 4 del wizard de poste eléctrico.
    Contiene ubicación y observaciones finales.
    Las fotos se guardan en modelo FotoPosteWizard relacionado.
    """
    wizard = models.OneToOneField(
        'PosteElectricoWizard',
        on_delete=models.CASCADE,
        related_name='ubicacion'  # wizard.ubicacion → parte 4
    )
    
    # Ubicación (opcional pero recomendado)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Notas u observaciones finales
    observaciones = models.TextField(blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actualizado_en']
        verbose_name = "Ubicación y Observaciones de Poste"
        verbose_name_plural = "Ubicaciones y Observaciones de Postes"

    def __str__(self):
        return f'Ubicación Poste #{self.wizard_id}'

class FotoPosteWizard(models.Model):
    """
    Fotos asociadas a la Parte 4 del wizard.
    Se permiten hasta 6 fotos por poste.
    """
    wizard = models.ForeignKey(
        'PosteElectricoWizard',
        on_delete=models.CASCADE,
        related_name='fotos'  # wizard.fotos.all()
    )
    
    # Archivo de imagen
    foto = models.ImageField(
        upload_to='fotos_postes/%Y/%m/',
        help_text='Foto del poste eléctrico'
    )
    
    # Orden de la foto (1-6)
    orden = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ],
        help_text='Orden de la foto (1-6)'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['wizard', 'orden']
        unique_together = ['wizard', 'orden']  # No permitir duplicar orden para el mismo wizard
        verbose_name = "Foto de Poste"
        verbose_name_plural = "Fotos de Postes"

    def __str__(self):
        return f'Foto {self.orden} - Poste #{self.wizard_id}'

    def clean(self):
        """Validar límite de 6 fotos por poste"""
        if self.wizard:
            count = self.wizard.fotos.count()
            if not self.pk and count >= 6:  # Solo al crear
                raise ValidationError('No se pueden agregar más de 6 fotos por poste.')