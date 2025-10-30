from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from ..models.models import Distrito, Zona, Sector
from ..serializers.serializers import DistritoTreeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated  # usa AllowAny si lo quieres público
from rest_framework.response import Response
from core.models.models import ParametroCatalogo
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CatalogoArbolView(APIView):
    authentication_classes = []  # ← Si quieres público; si no, usa tu JWT
    permission_classes = []      # ← o IsAuthenticated

    @swagger_auto_schema(
        operation_description="Devuelve el árbol de ubicación: distrito, zonas y sectores.",
        manual_parameters=[
            openapi.Parameter(
                'distrito_id', openapi.IN_QUERY, description="ID del distrito", type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                'incluir', openapi.IN_QUERY, description="Niveles a incluir: zonas,sectores", type=openapi.TYPE_STRING, required=False, default="zonas,sectores"
            ),
        ],
        responses={
            200: openapi.Response(
                description="Árbol de ubicación",
                examples={
                    "application/json": {
                        "id": 1,
                        "nombre": "Distrito Ejemplo",
                        "zonas": [
                            {
                                "id": 1,
                                "nombre": "Zona Ejemplo",
                                "sectores": [
                                    {"id": 1, "nombre": "Sector Ejemplo"}
                                ]
                            }
                        ]
                    }
                }
            ),
            400: "distrito_id es requerido",
            404: "Distrito no encontrado"
        }
    )
    def get(self, request):
        """
        Devuelve el árbol de ubicación: distrito, zonas y sectores.
        Parámetros:
        - distrito_id (int, requerido): ID del distrito
        - incluir (str, opcional): Niveles a incluir separados por coma (zonas,sectores)
        """
        distrito_id = request.query_params.get("distrito_id")
        incluir = request.query_params.get("incluir", "zonas,sectores").split(",")

        if not distrito_id:
            return Response({"detail": "distrito_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        # Optimización: prefetch zonas y sectores
        zonas_qs = Zona.objects.order_by("nombre")
        if "sectores" in incluir:
            zonas_qs = zonas_qs.prefetch_related(Prefetch("sectores", queryset=Sector.objects.order_by("nombre")))

        try:
            distrito = (
                Distrito.objects
                .prefetch_related(Prefetch("zonas", queryset=zonas_qs))
                .get(pk=distrito_id)
            )
        except Distrito.DoesNotExist:
            return Response({"detail": "Distrito no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Si el cliente no pidió sectores, vaciamos la lista
        data = DistritoTreeSerializer(distrito).data
        if "zonas" not in incluir:
            data.pop("zonas", None)
        elif "sectores" not in incluir:
            for z in data.get("zonas", []):
                z.pop("sectores", None)

        return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Devuelve las opciones de catálogo para postes: estructura, material, zona_instalacion, resistencia.",
    responses={
        200: openapi.Response(
            description="Opciones de catálogo",
            examples={
                "application/json": {
                    "estructura": ["Concreto", "Madera", "Metal"],
                    "material": ["Acero", "Aluminio"],
                    "zona_instalacion": ["Urbana", "Rural"],
                    "resistencia": ["Alta", "Media", "Baja"]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # cambia a AllowAny si deseas
def catalogo_poste_opciones(request):
    """
    Devuelve las opciones de catálogo para postes:
    - estructura
    - material
    - zona_instalacion
    - resistencia
    """
    qs = (ParametroCatalogo.objects
          .filter(activo=True)
          .values('categoria', 'nombre', 'orden')
          .order_by('categoria', 'orden', 'nombre'))
    resp = {
        'estructura': [],
        'material': [],
        'zona_instalacion': [],
        'resistencia': [],
    }
    for row in qs:
        resp[row['categoria']].append(row['nombre'])
    return Response(resp, status=200)