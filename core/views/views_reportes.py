from django.conf import settings
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from ..models.models import Reporte
from ..serializers.serializers import PosteReporteDetailSerializer
from datetime import datetime
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models.models import Reporte, FotoReporte
from datetime import datetime
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models.models import Reporte
from ..serializers.serializers import PosteReporteDetailSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

def make_absolute_media_url(request, relative_path):
    """
    Devuelve una URL absoluta a partir de una ruta de media.
    Tolera que request no tenga build_absolute_uri (tests, wrappers).
    
    Args:
        request: Request object
        relative_path: Optional[str] - Ruta relativa del medio
    
    Returns:
        Optional[str] - URL absoluta o None si no hay ruta
    """
    if not relative_path:
        return None
    build_abs = getattr(request, "build_absolute_uri", None)
    if callable(build_abs):
        return build_abs(relative_path)
    # Fallback usando settings.SITE_URL si lo tienes configurado (recomendado en prod)
    base = getattr(settings, "SITE_URL", "").rstrip("/")
    return f"{base}{relative_path}" if base else relative_path


class ReporteCompletarView(APIView):
    """
    POST /api/reportes/<int:reporte_id>/completar/
    - Siempre guarda 'observaciones' (aunque esté vacía).
    - Si viene 'imagen' => reemplaza la principal y pasa estado a 'registrado'.
    - Si NO viene 'imagen' => mantiene/define estado 'pendiente'.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @transaction.atomic
    def post(self, request, reporte_id: int):
        # 1) Cargar reporte
        try:
            rep = Reporte.objects.get(id=reporte_id)
        except Reporte.DoesNotExist:
            return Response({"detail": "Reporte no existe."}, status=status.HTTP_404_NOT_FOUND)

        # 2) Observaciones (siempre)
        # request.data puede ser Any; usamos getattr para no reventar.
        data = getattr(request, "data", {}) or {}
        obs = data.get("observaciones", "")
        rep.observaciones = "" if obs is None else str(obs)
        rep.save(update_fields=["observaciones"])

        # 3) Imagen (opcional)
        files = getattr(request, "FILES", None)
        imagen = None
        if files is not None and hasattr(files, "get"):
            imagen = files.get("imagen")

        if imagen:
            # Coordenadas opcionales (tolerantes)
            lat_raw = data.get("latitud")
            lon_raw = data.get("longitud")
            try:
                lat = float(lat_raw) if lat_raw not in (None, "",) else None
                lon = float(lon_raw) if lon_raw not in (None, "",) else None
            except (TypeError, ValueError):
                return Response({"detail": "latitud/longitud inválidas."}, status=status.HTTP_400_BAD_REQUEST)

            # Reemplazar principal
            FotoReporte.objects.filter(reporte=rep, is_principal=True).delete()
            FotoReporte.objects.create(
                reporte=rep,
                imagen=imagen,
                tipo=str(data.get("tipo") or "fachada"),
                latitud=lat,
                longitud=lon,
                is_principal=True,
            )

            if rep.estado != "registrado":
                rep.estado = "registrado"
                rep.save(update_fields=["estado"])
        else:
            # Sin foto => permanecer/forzar pendiente si no estaba registrado
            if rep.estado != "registrado":
                rep.estado = "pendiente"
                rep.save(update_fields=["estado"])

        # 4) Respuesta consistente (sin reventar si no hay .url)
        principal = (
            FotoReporte.objects.filter(reporte=rep, is_principal=True).first()
        )
        rel_url = getattr(getattr(principal, "imagen", None), "url", None)
        abs_url = make_absolute_media_url(request, rel_url)

        return Response(
            {
                "reporte_id": rep.id,
                "estado": rep.estado,
                "observaciones": rep.observaciones,
                "foto_principal_url": abs_url,  # None si no hay
            },
            status=status.HTTP_200_OK,
        )
# core/views_reportes.py
class ReporteObservacionesUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    # Permitimos JSON y formularios (incluye form-data)
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def patch(self, request, reporte_id: int):
        # 1) Buscar el reporte (si quieres forzar solo predio, agrega tipo="predio")
        try:
            rep = Reporte.objects.get(id=reporte_id)
        except Reporte.DoesNotExist:
            return Response({"detail": "Reporte no existe."}, status=status.HTTP_404_NOT_FOUND)

        # 2) Obtener datos de manera segura (tolera request sin .data)
        data = getattr(request, "data", None) or {}

        # Buscamos la clave en data; si no, intentamos POST (caso form-urlencoded/form-data)
        obs = data.get("observaciones", None)
        if obs is None:
            post = getattr(request, "POST", None)
            if post is not None:
                obs = post.get("observaciones", None)

        if obs is None:
            return Response({"detail": "Falta 'observaciones'."}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Guardar
        rep.observaciones = str(obs)
        rep.save(update_fields=["observaciones"])

        return Response(
            {"reporte_id": rep.id, "observaciones": rep.observaciones},
            status=status.HTTP_200_OK
        )
    

class PredioReporteListView(APIView):
    """
    GET /api/predios/reportes/list/
    Lista reportes tipo 'predio' con filtros y paginación.
    Reglas de visibilidad:
      - superadmin: ve todo
      - admin: ve su empresa (a través de proyecto->empresa)
      - supervisor: ve reportes de sus encargados
      - encargado: solo sus reportes
    Paginación:
      - page: Número de página (opcional, por defecto 1).
      - page_size: Cantidad de elementos por página (opcional, por defecto 10).
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lista reportes tipo 'predio' con filtros y paginación.\n\nReglas de visibilidad:\n  - superadmin: ve todo\n  - admin: ve su empresa (a través de proyecto->empresa)\n  - supervisor: ve reportes de sus encargados\n  - encargado: solo sus reportes\n\nPaginación:\n  - page: Número de página (opcional, por defecto 1).\n  - page_size: Cantidad de elementos por página (opcional, por defecto 10).",
        manual_parameters=[
            openapi.Parameter(
                'estado', openapi.IN_QUERY, description="Estado del reporte", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'sector_id', openapi.IN_QUERY, description="ID del sector", type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'zona_id', openapi.IN_QUERY, description="ID de la zona", type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'distrito_id', openapi.IN_QUERY, description="ID del distrito", type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'fecha_desde', openapi.IN_QUERY, description="Fecha desde (ISO: yyyy-mm-dd)", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'fecha_hasta', openapi.IN_QUERY, description="Fecha hasta (ISO: yyyy-mm-dd)", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'q', openapi.IN_QUERY, description="Búsqueda por código de predio", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'page_size', openapi.IN_QUERY, description="Cantidad de elementos por página", type=openapi.TYPE_INTEGER, required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Lista de reportes",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "nombre": "Reporte 1",
                            "estado": "activo",
                            "fecha_reporte": "2025-10-21T10:00:00Z",
                            "encargado": "Usuario 1",
                            "sector": "Sector 1",
                            "zona": "Zona 1"
                        },
                        {
                            "id": 2,
                            "nombre": "Reporte 2",
                            "estado": "inactivo",
                            "fecha_reporte": "2025-10-20T10:00:00Z",
                            "encargado": "Usuario 2",
                            "sector": "Sector 2",
                            "zona": "Zona 2"
                        }
                    ]
                }
            )
        }
    )
    def get(self, request):
        user = request.user
        qs = Reporte.objects.filter(tipo='predio').select_related(
            'encargado', 'sector', 'zona', 'proyecto'
        ).order_by('-fecha_reporte')

        # --- scope por rol ---
        if getattr(user, 'rol', None) == 'admin' and getattr(user, 'empresa_id', None):
            qs = qs.filter(proyecto__empresa_id=user.empresa_id)
        elif getattr(user, 'rol', None) == 'supervisor':
            qs = qs.filter(encargado__supervisor_id=user.id)
        elif getattr(user, 'rol', None) == 'encargado':
            qs = qs.filter(encargado_id=user.id)
        # superadmin: sin filtro

        # --- filtros opcionales ---
        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        sector_id = request.query_params.get('sector_id')
        if sector_id:
            qs = qs.filter(sector_id=sector_id)

        zona_id = request.query_params.get('zona_id')
        if zona_id:
            qs = qs.filter(zona_id=zona_id)

        distrito_id = request.query_params.get('distrito_id')
        if distrito_id:
            qs = qs.filter(zona__distrito_id=distrito_id)

        f_desde = request.query_params.get('fecha_desde')  # ISO: 2025-10-01
        f_hasta = request.query_params.get('fecha_hasta')  # ISO: 2025-10-12
        # Acepta yyyy-mm-dd (lo convertimos a rango día completo)
        def _to_dt_start(s):
            try:
                return datetime.fromisoformat(s.strip())
            except Exception:
                return None
        def _to_dt_end(s):
            try:
                d = datetime.fromisoformat(s.strip())
                return d.replace(hour=23, minute=59, second=59, microsecond=999999)
            except Exception:
                return None

        if f_desde:
            d1 = _to_dt_start(f_desde)
            if d1:
                qs = qs.filter(fecha_reporte__gte=d1)
        if f_hasta:
            d2 = _to_dt_end(f_hasta)
            if d2:
                qs = qs.filter(fecha_reporte__lte=d2)

        # Búsqueda por código_predio del detalle (si aplica)
        search = request.query_params.get('q')
        if search:
            qs = qs.filter(detalle_predio__codigo_predio__icontains=search)

        # --- paginación simple (page/page_size) ---
        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except ValueError:
            page = 1
        try:
            page_size = min(100, max(1, int(request.query_params.get('page_size', 20))))
        except ValueError:
            page_size = 20

        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()

        serializer = PosteReporteDetailSerializer(qs[start:end], many=True, context={'request': request})
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }, status=status.HTTP_200_OK)