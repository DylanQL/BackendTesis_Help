# core/views_reportes.py (por ejemplo)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models.models import Reporte, DetallePosteElectrico, DetallePredio, FotoReporte
from ..serializers.serializers import (
    PosteReporteCreateSerializer, PosteReporteDetailSerializer,
    PosteDetalleElectricoSerializer, PredioDetalleSerializer,
    PosteFotoCreateSerializer
)

class PosteReporteCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PosteReporteCreateSerializer
    queryset = Reporte.objects.all()


class PosteDetalleElectricoUpsertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk:int):
        reporte = get_object_or_404(Reporte, pk=pk)
        try:
            detalle = reporte.detalle_electrico
            serializer = PosteDetalleElectricoSerializer(detalle, data=request.data, partial=True)
        except DetallePosteElectrico.DoesNotExist:
            serializer = PosteDetalleElectricoSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(reporte=reporte)
            return Response(PosteDetalleElectricoSerializer(obj).data, status=200)
        return Response(serializer.errors, status=400)


class PredioDetalleUpsertView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Crea o actualiza el detalle de un predio asociado a un reporte.",
        request_body=PredioDetalleSerializer,
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
    def post(self, request, pk: int):
        reporte = get_object_or_404(Reporte, pk=pk)
        try:
            detalle = reporte.detalle_predio
            serializer = PredioDetalleSerializer(detalle, data=request.data, partial=True)
        except DetallePredio.DoesNotExist:
            serializer = PredioDetalleSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(reporte=reporte)
            return Response(PredioDetalleSerializer(obj).data, status=200)
        return Response(serializer.errors, status=400)


class PosteFotoCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PosteFotoCreateSerializer
    queryset = FotoReporte.objects.all()

    def perform_create(self, serializer):
        reporte_id = self.kwargs["pk"]
        reporte = get_object_or_404(Reporte, pk=reporte_id)
        serializer.save(reporte=reporte)


class PosteReporteRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PosteReporteDetailSerializer
    queryset = Reporte.objects.select_related("encargado","sector").prefetch_related("fotos")
