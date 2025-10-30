# core/views_wizard3.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from core.models.models import (
    PosteElectricoWizard,        # Wizard 1
    PosteElectricoWizard_2,      # Wizard 2 (related_name='caracteristicas')
    PosteElectricoWizard_3,      # Wizard 3 (related_name='condicion')
)
from core.serializers.serializers import PosteWizardParte3Serializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_wizard3_save(request):
    """
    Parte 3 del Wizard.
    Requiere: Wizard 1 en 'draft' + Wizard 2 existente.
    No autocrea predecesores.
    """
    # 1) Buscar Wizard 1 (del usuario) en draft
    parent = (PosteElectricoWizard.objects
              .filter(encargado=request.user, estado='draft')
              .order_by('-actualizado_en')
              .first())
    if parent is None:
        return Response(
            {"detail": "Predecesor faltante: no existe Wizard 1 en estado 'draft'."},
            status=status.HTTP_409_CONFLICT
        )

    # 2) Verificar que Wizard 2 exista PARA ESE parent
    #    Opción A (aprovechando OneToOne y related_name='caracteristicas'):
    try:
        _ = parent.caracteristicas  # si no existe, lanza DoesNotExist
    except PosteElectricoWizard_2.DoesNotExist:
        return Response(
            {"detail": "Predecesor faltante: debe completar Wizard 2 antes de continuar con Wizard 3."},
            status=status.HTTP_409_CONFLICT
        )

    # 3) Crear/actualizar Wizard 3 (OneToOne con el parent) wizard_prechecks
    with transaction.atomic():
        parte3, _created = PosteElectricoWizard_3.objects.get_or_create(wizard=parent)

        serializer = PosteWizardParte3Serializer(parte3, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            payload = PosteWizardParte3Serializer(obj).data
            payload.update({'wizard_parent_id': parent.id, 'wizard_estado': parent.estado})
            return Response(payload, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# core/views_wizard3.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wizard_prechecks(request):
    parent = (PosteElectricoWizard.objects
              .filter(encargado=request.user, estado='draft')
              .order_by('-actualizado_en')
              .first())
    has_w1 = parent is not None
    has_w2 = False
    if has_w1:
        try:
            _ = parent.caracteristicas
            has_w2 = True
        except PosteElectricoWizard_2.DoesNotExist:
            has_w2 = False

    return Response({
        "has_w1_draft": has_w1,
        "has_w2_for_w1": has_w2,
        "wizard_parent_id": parent.id if parent else None
    }, status=200)

