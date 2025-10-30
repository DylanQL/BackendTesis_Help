from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models.models import Reporte, DetallePredio
from ..serializers.serializers_predio import (
    ReporteCreateSerializer, DetallePredioSerializer,
    FotoReporteCreateSerializer, ReporteDetalleViewSerializer
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from ..models.models import Reporte, DetallePredio
from ..serializers.serializers import DetallePredioAvanzadoSerializer

class DetallePredioAvanzadoUpsertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reporte_id: int):
        # 1) Reporte existe
        try:
            reporte = Reporte.objects.select_related("encargado").get(id=reporte_id)
        except Reporte.DoesNotExist:
            return Response({"detail": "Reporte no existe."}, status=status.HTTP_404_NOT_FOUND)

        # 2) Autorización: solo el encargado dueño
        user = request.user
        if getattr(user, "rol", None) != "encargado" or reporte.encargado_id != user.id:
            return Response({"detail": "No autorizado para modificar este reporte."}, status=status.HTTP_403_FORBIDDEN)

        # 3) Solo aplica a reportes de tipo 'predio'
        if reporte.tipo != "predio":
            return Response({"detail": "Este endpoint solo aplica a reportes de tipo 'predio'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 4) Upsert
        detalle, _ = DetallePredio.objects.get_or_create(reporte=reporte)
        serializer = DetallePredioAvanzadoSerializer(detalle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporte=reporte)

        return Response(serializer.data, status=status.HTTP_200_OK)
# 1) Crear Reporte base (encargado = request.user)
class ReporteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crea un nuevo reporte base asociado al usuario encargado.",
        request_body=ReporteCreateSerializer,
        responses={
            201: openapi.Response(
                description="Reporte creado exitosamente",
                examples={
                    "application/json": {
                        "id": 1,
                        "nombre": "Reporte de predio",
                        "descripcion": "Descripción del reporte",
                        "fecha_creacion": "2025-10-21T10:00:00Z"
                    }
                }
            ),
            400: "Errores de validación"
        }
    )
    def post(self, request):
        ser = ReporteCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        reporte = ser.save()
        return Response({"id": reporte.id, **ser.data}, status=status.HTTP_201_CREATED)


# 2) Upsert del detalle del predio (crea/actualiza)
class DetallePredioUpsertView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crea o actualiza el detalle de un predio asociado a un reporte.",
        request_body=DetallePredioSerializer,
        responses={
            200: openapi.Response(
                description="Detalle del predio actualizado",
                examples={
                    "application/json": {
                        "id": 1,
                        "codigo_predio": "12345",
                        "direccion": "Av. Principal 123",
                        "area": 150.5,
                        "uso": "Residencial"
                    }
                }
            ),
            400: "Errores de validación"
        }
    )
    def post(self, request, reporte_id: int):
        reporte = get_object_or_404(Reporte, pk=reporte_id)
        detalle = getattr(reporte, "detalle_predio", None)

        if detalle:
            ser = DetallePredioSerializer(detalle, data=request.data, partial=True)
        else:
            ser = DetallePredioSerializer(data=request.data)

        ser.is_valid(raise_exception=True)
        obj = ser.save(reporte=reporte)
        return Response(DetallePredioSerializer(obj).data, status=status.HTTP_200_OK)


# 3) Subir foto (multipart/form-data)
class FotoReporteUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Sube fotos asociadas a un reporte utilizando multipart/form-data.",
        manual_parameters=[
            openapi.Parameter(
                "foto", openapi.IN_FORM, description="Archivo de la foto", type=openapi.TYPE_FILE, required=True
            ),
            openapi.Parameter(
                "descripcion", openapi.IN_FORM, description="Descripción de la foto", type=openapi.TYPE_STRING, required=False
            )
        ],
        responses={
            201: openapi.Response(
                description="Foto subida exitosamente",
                examples={
                    "application/json": {
                        "id": 1,
                        "url": "https://example.com/foto1.jpg",
                        "descripcion": "Foto del predio"
                    }
                }
            ),
            400: "Errores de validación"
        }
    )
    def post(self, request, reporte_id: int):
        get_object_or_404(Reporte, pk=reporte_id)
        data = request.data.copy()
        data["reporte"] = reporte_id
        ser = FotoReporteCreateSerializer(data=data, context={"request": request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


# 4) Obtener todo el reporte con detalle + fotos (para pintar el modal)
class ReporteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtiene el detalle completo de un reporte, incluyendo fotos.",
        responses={
            200: openapi.Response(
                description="Detalle del reporte",
                examples={
                    "application/json": {
                        "id": 1,
                        "nombre": "Reporte de predio",
                        "descripcion": "Descripción del reporte",
                        "fecha_creacion": "2025-10-21T10:00:00Z",
                        "encargado": "Usuario 1",
                        "sector": "Sector 1",
                        "fotos": [
                            {
                                "url": "https://example.com/foto1.jpg",
                                "descripcion": "Foto del predio"
                            },
                            {
                                "url": "https://example.com/foto2.jpg",
                                "descripcion": "Foto adicional"
                            }
                        ]
                    }
                }
            ),
            404: "Reporte no encontrado"
        }
    )
    def get(self, request, reporte_id: int):
        reporte = (
            Reporte.objects
            .select_related("encargado", "sector")
            .prefetch_related("fotos")
            .get(pk=reporte_id)
        )
        ser = ReporteDetalleViewSerializer(reporte, context={"request": request})
        return Response(ser.data)
