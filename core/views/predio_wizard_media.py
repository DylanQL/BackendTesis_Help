"""
Vistas de medios y publicación del wizard de predios.
Maneja imágenes, observaciones y la publicación final del wizard.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models.models import PredioWizard, Reporte, DetallePredio, FotoReporte
from ..serializers.serializers import PredioWizardMediaSerializer


class PredioWizardMediaView(APIView):
    """
    Agrega imagen y observaciones al wizard de predio.
    Acepta multipart/form-data para subida de archivos.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_description="Agrega imagen y observaciones al wizard de predio.",
        request_body=PredioWizardMediaSerializer,
        responses={
            200: "Datos actualizados en el wizard",
            404: "Wizard no existe o no es tuyo."
        }
    )
    def post(self, request, wizard_id):
        # Buscar wizard y validar dueño/rol
        try:
            wz = PredioWizard.objects.get(id=wizard_id, encargado=request.user)
        except PredioWizard.DoesNotExist:
            return Response(
                {"detail": "Wizard no existe o no es tuyo."}, 
                status=404
            )

        # Guardar observaciones (si viene)
        obs = request.data.get("observaciones", "")
        wz.observaciones = "" if obs is None else str(obs)

        # Guardar imagen (si viene)
        imagen = request.FILES.get("imagen")
        if imagen:
            wz.imagen = imagen

        # Actualizar estado si es necesario
        if wz.estado == "started":
            wz.estado = "in_progress"
            
        wz.save(update_fields=["observaciones", "imagen", "estado"])

        return Response({
            "wizard_id": str(wz.id),
            "estado": wz.estado,
            "has_imagen": bool(wz.imagen),
            "observaciones": wz.observaciones
        }, status=200)


class PredioWizardPublishView(APIView):
    """
    Publica un wizard y crea un reporte basado en los datos del wizard.
    Convierte el wizard en un reporte oficial con todos sus detalles.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Publica un wizard y crea un reporte basado en los datos del wizard.",
        responses={
            201: "Wizard publicado exitosamente y reporte creado.",
            400: "Error en los datos del wizard o falta de proyecto asociado.",
            403: "No autorizado.",
            404: "Wizard no existe."
        }
    )
    def post(self, request, wizard_id):
        # Validar wizard existe y pertenece al usuario
        try:
            wz = PredioWizard.objects.get(id=wizard_id, encargado=request.user)
        except PredioWizard.DoesNotExist:
            return Response({"detail": "Wizard no existe."}, status=404)

        # Determinar proyecto
        proyecto = wz.proyecto
        if proyecto is None and wz.zona:
            proyecto = wz.zona.proyecto
        
        if proyecto is None:
            return Response(
                {"detail": "No se pudo determinar el proyecto. Define proyecto en el wizard start o asócialo a la Zona."},
                status=400
            )

        # Crear Reporte
        rep = Reporte.objects.create(
            tipo="predio",
            encargado=request.user,
            proyecto=proyecto,
            zona=wz.zona,
            sector=wz.sector,
            observaciones=wz.observaciones or "",
            latitud=wz.latitud,
            longitud=wz.longitud,
            estado="pendiente",
        )

        # Crear DetallePredio desde payload
        DetallePredio.objects.create(
            reporte=rep,
            **(wz.detalle_payload or {})
        )

        # Migrar foto si existe
        if getattr(wz, "imagen", None):
            FotoReporte.objects.create(
                reporte=rep,
                imagen=wz.imagen,
                tipo="fachada",
                latitud=wz.latitud,
                longitud=wz.longitud,
                is_principal=True,
            )
            rep.estado = "registrado"
            rep.save(update_fields=["estado"])

        # Marcar wizard como publicado
        wz.is_published = True
        wz.save(update_fields=["is_published"])

        return Response(
            {"reporte_id": rep.id, "estado": rep.estado}, 
            status=201
        )
