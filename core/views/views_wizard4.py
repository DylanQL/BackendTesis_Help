from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from core.models.models import (
    PosteElectricoWizard,
    PosteElectricoWizard_3,
    PosteElectricoWizard_4,
    FotoPosteWizard
)
from core.serializers.serializers_poste_wizard import PosteWizardParte4Serializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def poste_wizard4_save(request):
    """
    Parte 4 del Wizard de Poste Eléctrico.
    
    Requisitos:
    - Wizard 1 (parent) en estado 'draft'
    - Wizard 3 existente
    
    Acepta:
    - latitud (decimal, opcional): -90 a 90
    - longitud (decimal, opcional): -180 a 180
    - observaciones (texto, opcional)
    - fotos (archivos, opcional): hasta 6 fotos, máximo 1MB cada una
    
    Ejemplo de uso con curl:
    curl -X POST \\
      -H "Authorization: Bearer <token>" \\
      -F "latitud=-12.0461" \\
      -F "longitud=-77.0305" \\
      -F "observaciones=Poste en buen estado" \\
      -F "uploaded_fotos[]=@foto1.jpg" \\
      -F "uploaded_fotos[]=@foto2.jpg" \\
      http://localhost:8000/api/wizard/poste-electrico/parte-4/
    """
    # 1) Buscar Wizard 1 (del usuario) en draft
    parent = (PosteElectricoWizard.objects
             .filter(encargado=request.user, estado='draft')
             .order_by('-actualizado_en')
             .first())
             
    if parent is None:
        return Response(
            {"detail": "No existe Wizard 1 en estado 'draft'."},
            status=status.HTTP_409_CONFLICT
        )
    
    # 2) Verificar que existe Parte 3
    try:
        _ = parent.condicion  # OneToOne a PosteElectricoWizard_3
    except PosteElectricoWizard_3.DoesNotExist:
        return Response(
            {"detail": "Debe completar Wizard 3 antes de continuar con la Parte 4."},
            status=status.HTTP_409_CONFLICT
        )
    
    # 3) Crear/actualizar Parte 4
    with transaction.atomic():
        parte4, created = PosteElectricoWizard_4.objects.get_or_create(wizard=parent)
        
        # Preparar datos combinando POST y FILES
        data = request.POST.dict()
        if request.FILES:
            data['uploaded_fotos'] = request.FILES.getlist('uploaded_fotos')
            
        serializer = PosteWizardParte4Serializer(
            parte4,
            data=data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            obj = serializer.save()
            
            # Si se indica publicar=True, cambiar estado a 'published'
            if serializer.validated_data.get('publicar', False):
                parent.estado = 'published'
                parent.save()
                
            response_data = PosteWizardParte4Serializer(obj).data
            response_data.update({
                'wizard_parent_id': parent.id,
                'wizard_estado': parent.estado,
                'foto_count': parent.fotos.count()
            })
            return Response(response_data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)