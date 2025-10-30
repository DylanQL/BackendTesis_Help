from django.db import models
from django.conf import settings
from django.utils import timezone

class PosteTelematicWizard(models.Model):
    """Modelo principal del wizard para postes telemáticos"""
    ESTADOS = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    ]

    # Usuario encargado del registro
    encargado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='poste_telematico_wizard_principal',
        null=True
    )

    # Campos básicos parte 1
    cables_telematicos = models.PositiveIntegerField(null=True, blank=True)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    cable_electrico = models.PositiveIntegerField(null=True, blank=True)
    
    # Elementos como JSONField para flexibilidad
    elementos_telematicos = models.JSONField(default=list, blank=True)
    elementos_electricos = models.JSONField(default=list, blank=True)

    # Control de estado y timestamps
    estado = models.CharField(max_length=10, choices=ESTADOS, default='draft')
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-actualizado_en']
        indexes = [
            models.Index(fields=['encargado', 'estado']),
        ]

    def __str__(self):
        return f"PosteTelematico #{self.id} - {self.codigo or 'Sin código'} ({self.estado})"

from django.utils import timezone

from django.utils import timezone

class PosteTelematicWizard_2(models.Model):
    """
    Parte 2 del wizard de poste telemático.
    Características físicas y estructurales.
    """
    # Relación con el wizard principal
    wizard = models.OneToOneField(
        'PosteTelematicWizard',
        on_delete=models.CASCADE,
        related_name='caracteristicas_fisicas',
        null=True
    )
    
    # Campos de características (similar a poste eléctrico)
    estructura = models.ForeignKey(
        'ParametroCatalogo',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='telematico_estructura_parte2'
    )
    
    material = models.ForeignKey(
        'ParametroCatalogo',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='telematico_material_parte2'
    )
    
    zona_instalacion = models.ForeignKey(
        'ParametroCatalogo',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='telematico_zona_parte2'
    )
    
    resistencia = models.ForeignKey(
        'ParametroCatalogo',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='telematico_resistencia_parte2'
    )
    
    # Valor manual de resistencia
    resistencia_valor = models.PositiveIntegerField(null=True, blank=True)
    
    # Datos adicionales como JSON
    coordenadas = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-actualizado_en']
        verbose_name = "Características de Poste Telemático"
        verbose_name_plural = "Características de Postes Telemáticos"

    def __str__(self):
        return f'Características Poste Telemático #{self.wizard_id}'
    
class PosteTelematicWizard_3(models.Model):
    """
    Parte 3 del wizard de poste telemático.
    Estado, condiciones y propietario.
    """
    wizard = models.OneToOneField(
        'PosteTelematicWizard',
        on_delete=models.CASCADE,
        related_name='condiciones_tecnicas',
        null=True
    )
    
    # Campos de condición física
    estado_poste = models.ForeignKey(
        'EstadoFisico',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='telematico_estados_parte3'
    )
    inclinacion = models.ForeignKey(
        'Inclinacion',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='telematico_inclinaciones_parte3'
    )
    propietario = models.ForeignKey(
        'Propietario',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='telematico_propietarios_parte3'
    )
    
    # Altura del poste (opcional)
    altura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notas u observaciones
    notas = models.TextField(blank=True)
    
    # Timestamps
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-actualizado_en']
        verbose_name = "Condición de Poste Telemático"
        verbose_name_plural = "Condiciones de Postes Telemáticos"
    
    def __str__(self):
        return f'Condición Poste Telemático #{self.wizard_id}'


class FotoTelematicWizard(models.Model):
    """
    Fotos asociadas a la Parte 4 del wizard telemático.
    Similar a FotoPosteWizard pero para postes telemáticos.
    """
    wizard = models.ForeignKey(
        'PosteTelematicWizard_4',
        on_delete=models.CASCADE,
        related_name='fotos'
    )
    
    imagen = models.ImageField(upload_to='telematicos/fotos/')
    descripcion = models.CharField(max_length=100, blank=True)
    
    # Control de orden y estado
    orden = models.PositiveIntegerField(default=0)
    is_principal = models.BooleanField(default=False)
    
    # Timestamps
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Foto de Poste Telemático"
        verbose_name_plural = "Fotos de Postes Telemáticos"

    def __str__(self):
        return f'Foto {self.orden} de Poste Telemático #{self.wizard.wizard_id}'

class PosteTelematicWizard_4(models.Model):
    """
    Parte 4 del wizard de poste telemático.
    Ubicación, fotos y observaciones finales.
    """
    wizard = models.OneToOneField(
        'PosteTelematicWizard',
        on_delete=models.CASCADE,
        related_name='ubicacion'
    )
    
    # Campos de ubicación
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    
    # Observaciones finales
    observaciones = models.TextField(blank=True)
    
    # Timestamps
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-actualizado_en']
        verbose_name = "Ubicación de Poste Telemático"
        verbose_name_plural = "Ubicaciones de Postes Telemáticos"
    
    def __str__(self):
        return f'Ubicación Poste Telemático #{self.wizard_id}'