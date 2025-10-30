from rest_framework import serializers
from ..models.models_telematico import (
    PosteTelematicWizard,
    PosteTelematicWizard_2,
    PosteTelematicWizard_3,
    PosteTelematicWizard_4,
    FotoTelematicWizard
)

class PosteTelematicWizardSerializer(serializers.ModelSerializer):
    """Serializer para la creación inicial del wizard telemático"""
    proximo_paso = serializers.SerializerMethodField()

    class Meta:
        model = PosteTelematicWizard
        fields = [
            'id', 'estado', 'creado_en', 'proximo_paso'
        ]
        read_only_fields = ['id', 'estado', 'creado_en']

    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.id}/parte1"

class PosteTelematicoParte1Serializer(serializers.ModelSerializer):
    """Serializer para la parte 1 del wizard telemático"""
    elementos_telematicos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    elementos_electricos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    proximo_paso = serializers.SerializerMethodField()

    class Meta:
        model = PosteTelematicWizard
        fields = [
            'id', 'cables_telematicos', 'codigo', 'cable_electrico',
            'elementos_telematicos', 'elementos_electricos',
            'estado', 'creado_en', 'actualizado_en', 'proximo_paso'
        ]
        read_only_fields = ['id', 'estado', 'creado_en', 'actualizado_en']

    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.id}/parte2"

    def validate_cables_telematicos(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El número de cables telemáticos no puede ser negativo")
        return value

    def validate_cable_electrico(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El número de cables eléctricos no puede ser negativo")
        return value

class PosteTelematicoParte2Serializer(serializers.ModelSerializer):
    """
    Serializer para la parte 2 del wizard telemático.
    Maneja las características físicas y estructurales del poste.
    """
    proximo_paso = serializers.SerializerMethodField()
    
    class Meta:
        model = PosteTelematicWizard_2
        fields = [
            'id', 'wizard', 'estructura', 'material',
            'zona_instalacion', 'resistencia', 'resistencia_valor',
            'coordenadas', 'creado_en', 'actualizado_en',
            'proximo_paso'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.wizard_id}/parte3"
    
    def validate_resistencia_valor(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El valor de resistencia no puede ser negativo"
            )
        return value

class PosteTelematicoParte3Serializer(serializers.ModelSerializer):
    """
    Serializer para la parte 3 del wizard telemático.
    Maneja el estado, condiciones y propietario del poste.
    """
    proximo_paso = serializers.SerializerMethodField()
    
    class Meta:
        model = PosteTelematicWizard_3
        fields = [
            'id', 'wizard', 'estado_poste', 'inclinacion',
            'propietario', 'altura', 'notas',
            'creado_en', 'actualizado_en', 'proximo_paso'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.wizard_id}/parte4"
    
    def validate_altura(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "La altura debe ser un valor positivo"
            )
        return value
    proximo_paso = serializers.SerializerMethodField()
    
    class Meta:
        model = PosteTelematicWizard_2
        fields = [
            'id', 'wizard', 'estructura', 'material',
            'zona_instalacion', 'resistencia', 'resistencia_valor',
            'coordenadas', 'creado_en', 'actualizado_en',
            'proximo_paso'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.wizard_id}/parte3"
    
    def validate_resistencia_valor(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El valor de resistencia no puede ser negativo"
            )
        return value
    elementos_telematicos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    elementos_electricos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    proximo_paso = serializers.SerializerMethodField()

    class Meta:
        model = PosteTelematicWizard
        fields = [
            'id', 'cables_telematicos', 'codigo', 'cable_electrico',
            'elementos_telematicos', 'elementos_electricos',
            'estado', 'creado_en', 'actualizado_en', 'proximo_paso'
        ]
        read_only_fields = ['id', 'estado', 'creado_en', 'actualizado_en']

    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.id}/parte2"

    def validate_cables_telematicos(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El número de cables telemáticos no puede ser negativo")
        return value

    def validate_cable_electrico(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El número de cables eléctricos no puede ser negativo")
        return value

class FotoTelematicWizardSerializer(serializers.ModelSerializer):
    """
    Serializer para manejar las fotos del poste telemático.
    """
    class Meta:
        model = FotoTelematicWizard
        fields = [
            'id', 'wizard', 'imagen', 'descripcion',
            'orden', 'is_principal', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en']

class PosteTelematicoParte4Serializer(serializers.ModelSerializer):
    """
    Serializer para la parte 4 del wizard telemático.
    Maneja ubicación, fotos y observaciones finales.
    """
    fotos = FotoTelematicWizardSerializer(many=True, read_only=True)
    proximo_paso = serializers.SerializerMethodField()

    class Meta:
        model = PosteTelematicWizard_4
        fields = [
            'id', 'wizard', 'latitud', 'longitud',
            'observaciones', 'fotos', 'creado_en',
            'actualizado_en', 'proximo_paso'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def get_proximo_paso(self, obj):
        return f"/api/wizard/telematico/{obj.wizard_id}/publicar"

    def validate(self, data):
        # Validar que latitud y longitud vengan juntos
        if ('latitud' in data and 'longitud' not in data) or \
           ('longitud' in data and 'latitud' not in data):
            raise serializers.ValidationError(
                "Latitud y longitud deben proporcionarse juntos"
            )
        return data

    def validate_latitud(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError(
                "La latitud debe estar entre -90 y 90 grados"
            )
        return value

    def validate_longitud(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError(
                "La longitud debe estar entre -180 y 180 grados"
            )
        return value