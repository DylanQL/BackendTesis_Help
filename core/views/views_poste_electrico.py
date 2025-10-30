# core/views_poste_electrico.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from core.models.models import PosteElectricoWizard, PosteElectricoWizard_2
from core.serializers.serializers import PosteWizardParte2Serializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_save(request):
    """
    Parte 2 del Wizard (características). REQUIERE predecesor (Wizard 1) en draft.
    No crea Wizard 1 automáticamente.
    """
    # 1) Verificar predecesor (Wizard 1) existente y en draft
    parent = PosteElectricoWizard.objects.filter(encargado=request.user, estado='draft')\
                                         .order_by('-actualizado_en').first()
    if parent is None:
        return Response(
            {
                "detail": "No existe un Wizard 1 (predecesor) en estado 'draft'. "
                          "Complete primero la parte 1 antes de continuar con la parte 2."
            },
            status=status.HTTP_409_CONFLICT
        )

    with transaction.atomic():
        # 2) Crear/actualizar la Parte 2 para ese padre (OneToOne)
        parte2, _ = PosteElectricoWizard_2.objects.get_or_create(wizard=parent)

        serializer = PosteWizardParte2Serializer(
            parte2, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            obj = serializer.save()
            payload = PosteWizardParte2Serializer(obj).data
            payload.update({'wizard_parent_id': parent.id, 'wizard_estado': parent.estado})
            return Response(payload, status=status.HTTP_200_OK)
