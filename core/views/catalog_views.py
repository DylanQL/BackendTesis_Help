"""
Vistas de catálogos y formularios de elementos.
Maneja elementos eléctricos, telemáticos y formularios de poste eléctrico.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models.models import ElementoElectrico, PosteElectricoWizard
from core.serializers.serializers import ElementoSerializer, PosteElectricoWizardSerializer


@swagger_auto_schema(
    method='get',
    operation_description="Devuelve los elementos eléctricos y telemáticos disponibles.",
    responses={
        200: openapi.Response(
            description="Elementos eléctricos y telemáticos",
            examples={
                "application/json": {
                    "elementos_electricos": [
                        {"id": 1, "nombre": "Transformador", "tipo": "electrico"},
                        {"id": 2, "nombre": "Poste", "tipo": "electrico"}
                    ],
                    "elementos_telematicos": [
                        {"id": 3, "nombre": "Antena", "tipo": "telematico"}
                    ]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def elementos_catalogo(request):
    """
    Devuelve los elementos eléctricos y telemáticos disponibles.
    Los elementos se agrupan por tipo para facilitar su uso en el frontend.
    """
    elementos = ElementoElectrico.objects.all().only('id', 'nombre', 'tipo')
    data = ElementoSerializer(elementos, many=True).data
    
    resp = {
        "elementos_electricos": [e for e in data if e["tipo"] == "electrico"],
        "elementos_telematicos": [e for e in data if e["tipo"] == "telematico"],
    }
    return Response(resp, status=200)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def poste_electrico_save(request):
    """
    Crea o actualiza el wizard más reciente en estado 'draft' para el usuario autenticado.
    - POST: crea si no existe draft; si existe, actualiza (upsert).
    - PATCH: siempre actualiza parcialmente el último draft (o crea si no hay).
    
    Esto permite que el usuario trabaje en un solo borrador a la vez.
    """
    with transaction.atomic():
        instance = PosteElectricoWizard.objects.filter(
            encargado=request.user, estado='draft'
        ).order_by('-actualizado_en').first()

        serializer = PosteElectricoWizardSerializer(
            instance, 
            data=request.data, 
            partial=True, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            obj = serializer.save(encargado=request.user)
            # 201 si creó, 200 si actualizó
            http_status = status.HTTP_201_CREATED if instance is None else status.HTTP_200_OK
            return Response(PosteElectricoWizardSerializer(obj).data, status=http_status)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def poste_electrico_list(request):
    """
    Lista todos los formularios de poste eléctrico del usuario autenticado.
    Incluye tanto borradores (draft) como publicados, ordenados por fecha de actualización.
    """
    registros = PosteElectricoWizard.objects.filter(
        encargado=request.user
    ).order_by('-actualizado_en')
    
    data = PosteElectricoWizardSerializer(registros, many=True).data
    return Response(data, status=status.HTTP_200_OK)
