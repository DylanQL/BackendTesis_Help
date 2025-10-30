"""
Vistas de detalles y coordenadas del wizard de predios.
Maneja la actualización de información detallada y geográfica.
"""
from django.utils import timezone as dj_timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models.models import PredioWizard
from ..serializers.serializers import (
    PredioWizardDetalleSerializer,
    PredioWizardCoordsSerializer
)


def _must_be_encargado_owner(request, wizard: PredioWizard):
    """
    Verifica que el usuario sea encargado y dueño del wizard.
    Retorna Response si no cumple, None si todo está bien.
    """
    user = request.user
    if getattr(user, "rol", None) != "encargado" or wizard.encargado_id != user.id:
        return Response(
            {"detail": "No autorizado."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    return None


class PredioWizardDetalleUpsertView(APIView):
    """
    Guarda el detalle validado en el wizard (sin crear Reporte aún).
    Utiliza el método PUT para garantizar idempotencia.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Guarda en el wizard el detalle validado (sin crear Reporte aún).",
        request_body=PredioWizardDetalleSerializer,
        responses={
            200: "Detalle guardado exitosamente",
            403: "No autorizado",
            404: "Wizard no existe"
        }
    )
    def put(self, request, wizard_id):
        # Validar que el wizard existe
        try:
            wizard = PredioWizard.objects.get(id=wizard_id)
        except PredioWizard.DoesNotExist:
            return Response(
                {"detail": "Wizard no existe."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar seguridad: dueño y rol
        not_auth = _must_be_encargado_owner(request, wizard)
        if not_auth:
            return not_auth

        # Validar payload con las reglas avanzadas
        ser = PredioWizardDetalleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # Persistir payload saneado en el wizard
        wizard.detalle_payload = ser.validated_data["payload"]
        if wizard.estado == "started":
            wizard.estado = "in_progress"
        wizard.save(update_fields=["detalle_payload", "estado", "updated_at"])

        return Response(
            {"wizard_id": str(wizard.id), "estado": wizard.estado}, 
            status=status.HTTP_200_OK
        )


class PredioWizardCoordsView(APIView):
    """
    Actualiza las coordenadas geográficas de un wizard.
    Registra el timestamp de captura de las coordenadas.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Actualiza las coordenadas de un wizard.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "latitud": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Latitud del predio"
                ),
                "longitud": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Longitud del predio"
                )
            },
            required=["latitud", "longitud"]
        ),
        responses={
            200: "Coordenadas actualizadas exitosamente",
            403: "No autorizado",
            404: "Wizard no existe"
        }
    )
    def post(self, request, wizard_id):
        try:
            wizard = PredioWizard.objects.get(id=wizard_id)
        except PredioWizard.DoesNotExist:
            return Response(
                {"detail": "Wizard no existe."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar permisos
        user = request.user
        if getattr(user, "rol", None) != "encargado" or wizard.encargado_id != user.id:
            return Response(
                {"detail": "No autorizado."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Validar y guardar coordenadas
        ser = PredioWizardCoordsSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        wizard.latitud = ser.validated_data["latitud"]
        wizard.longitud = ser.validated_data["longitud"]
        wizard.coords_captured_at = dj_timezone.now()
        
        if wizard.estado == "started":
            wizard.estado = "in_progress"
            
        wizard.save(update_fields=[
            "latitud", "longitud", "coords_captured_at", "estado", "updated_at"
        ])

        return Response({
            "wizard_id": str(wizard.id),
            "latitud": wizard.latitud,
            "longitud": wizard.longitud,
            "captured_at": wizard.coords_captured_at.isoformat().replace("+00:00", "Z")
        }, status=status.HTTP_200_OK)
