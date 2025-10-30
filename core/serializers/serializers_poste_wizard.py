from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from ..models.models import PosteElectricoWizard_4, FotoPosteWizard

class FotoPosteWizardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoPosteWizard
        fields = ['id', 'foto', 'orden', 'creado_en']
        read_only_fields = ['id', 'creado_en']

class PosteWizardParte4Serializer(serializers.ModelSerializer):
    fotos = FotoPosteWizardSerializer(many=True, read_only=True)
    uploaded_fotos = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000,  # 1MB máximo por foto
            allow_empty_file=False,
            use_url=False
        ),
        write_only=True,
        required=False,
        max_length=6  # máximo 6 fotos
    )
    
    publicar = serializers.BooleanField(default=False, write_only=True)
    
    class Meta:
        model = PosteElectricoWizard_4
        fields = [
            'id', 'latitud', 'longitud', 'observaciones',
            'fotos', 'uploaded_fotos', 'publicar',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def validate_uploaded_fotos(self, fotos):
        """Validar cantidad y tamaño de fotos"""
        if fotos:
            if len(fotos) > 6:
                raise serializers.ValidationError("No se pueden subir más de 6 fotos.")
            for foto in fotos:
                if foto.size > 1000000:  # 1MB
                    raise serializers.ValidationError(
                        f"Foto {foto.name} excede el tamaño máximo (1MB)."
                    )
        return fotos
    
    def validate(self, attrs):
        """Validar coordenadas en rangos válidos"""
        latitud = attrs.get('latitud')
        longitud = attrs.get('longitud')
        
        if latitud is not None and (latitud < -90 or latitud > 90):
            raise serializers.ValidationError({
                'latitud': 'Debe estar entre -90 y 90 grados.'
            })
            
        if longitud is not None and (longitud < -180 or longitud > 180):
            raise serializers.ValidationError({
                'longitud': 'Debe estar entre -180 y 180 grados.'
            })
            
        return attrs
    
    def create(self, validated_data):
        """Crear Parte 4 y procesar fotos si hay"""
        fotos = validated_data.pop('uploaded_fotos', [])
        instance = super().create(validated_data)
        
        # Procesar fotos si existen
        for i, foto in enumerate(fotos, 1):
            FotoPosteWizard.objects.create(
                wizard=instance.wizard,
                foto=foto,
                orden=i
            )
        
        return instance
    
    def update(self, instance, validated_data):
        """Actualizar Parte 4 y añadir nuevas fotos si hay"""
        fotos = validated_data.pop('uploaded_fotos', [])
        instance = super().update(instance, validated_data)
        
        # Añadir nuevas fotos si hay espacio
        current_count = instance.wizard.fotos.count()
        for i, foto in enumerate(fotos, current_count + 1):
            if i > 6:  # Límite de 6 fotos
                break
            FotoPosteWizard.objects.create(
                wizard=instance.wizard,
                foto=foto,
                orden=i
            )
        
        return instance