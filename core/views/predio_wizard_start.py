"""
Vista de inicio del wizard de predios.
Maneja la creación inicial del wizard y la configuración del contexto.
"""
from django.utils import timezone as dj_timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from ..models.models import PredioWizard
from ..serializers.serializers import PredioWizardStartSerializer


class PredioWizardStartView(APIView):
    """
    Inicia un nuevo wizard para gestionar detalles de predios.
    Solo los encargados pueden iniciar wizards.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Inicia un nuevo wizard para gestionar detalles de predios.",
        request_body=PredioWizardStartSerializer,
        responses={
            201: "Wizard iniciado exitosamente",
            403: "Solo encargados pueden iniciar el wizard",
            400: "Errores de validación",
            409: "Ya existe un wizard activo para este distrito/zona/sector"
        }
    )
    def post(self, request):
        # Validar que el usuario sea encargado
        if getattr(request.user, "rol", None) != "encargado":
            return Response(
                {"detail": "Solo encargados pueden iniciar el wizard."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Idempotencia (opcional): reutilizar wizard existente
        idem = request.headers.get("Idempotency-Key")
        if idem:
            # Implementar lógica de idempotencia si es necesario
            pass

        # Validar y crear wizard
        ser = PredioWizardStartSerializer(data=request.data, context={"request": request})
        if not ser.is_valid():
            if "_conflict" in ser.errors:
                return Response({
                    "detail": "Ya existe un wizard activo para este distrito/zona/sector.",
                    "wizard_id": ser.errors["_conflict"][0]
                }, status=status.HTTP_409_CONFLICT)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        wizard = ser.save()
        
        # Construir respuesta con URLs de siguiente paso
        data = {
            "id": str(wizard.id),
            "distrito": wizard.distrito_id,
            "zona": wizard.zona_id,
            "sector": wizard.sector_id,
            "estado": wizard.estado,
            "next": {
                "detalle_url": f"/api/predios/wizard/{wizard.id}/detalle/",
                "coords_url": f"/api/predios/wizard/{wizard.id}/coords/",
                "fotos_url": f"/api/predios/wizard/{wizard.id}/fotos/",
                "publish_url": f"/api/predios/wizard/{wizard.id}/publish/",
            }
        }
        return Response(data, status=status.HTTP_201_CREATED)
