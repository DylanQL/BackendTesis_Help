from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from ..models.models import PosteElectricoWizard
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Obtiene estadísticas de los reportes de postes eléctricos.",
    responses={
        200: openapi.Response(
            description="Estadísticas de reportes de postes",
            examples={
                "application/json": {
                    "total_reportes": 100,
                    "por_estado": {
                        "draft": 60,
                        "published": 40
                    },
                    "mis_reportes": {
                        "total": 10,
                        "por_estado": {
                            "draft": 7,
                            "published": 3
                        }
                    }
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_postes(request):
    """
    Obtiene estadísticas de los reportes de postes eléctricos.
    
    Retorna:
    - total_reportes: Número total de reportes
    - por_estado: Conteo de reportes por estado (draft, published)
    - mis_reportes: Conteo de reportes del usuario autenticado
    """
    # Estadísticas generales
    total_reportes = PosteElectricoWizard.objects.count()
    
    # Conteo por estado
    por_estado = (PosteElectricoWizard.objects
                 .values('estado')
                 .annotate(total=Count('id'))
                 .order_by('estado'))
    
    # Estadísticas del usuario autenticado
    mis_reportes = {
        'total': PosteElectricoWizard.objects.filter(encargado=request.user).count(),
        'por_estado': PosteElectricoWizard.objects
                    .filter(encargado=request.user)
                    .values('estado')
                    .annotate(total=Count('id'))
                    .order_by('estado')
    }
    
    # Formatear respuesta
    response_data = {
        'total_reportes': total_reportes,
        'por_estado': {item['estado']: item['total'] for item in por_estado},
        'mis_reportes': {
            'total': mis_reportes['total'],
            'por_estado': {item['estado']: item['total'] for item in mis_reportes['por_estado']}
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)