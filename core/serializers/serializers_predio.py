from rest_framework import serializers
from ..models.models import Reporte, DetallePredio, FotoReporte

class ReporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ["id", "tipo", "proyecto", "zona", "sector",
                  "observaciones", "latitud", "longitud", "estado"]

    def create(self, validated_data):
        # El encargado es el usuario autenticado (rol: encargado)
        validated_data["encargado"] = self.context["request"].user
        return super().create(validated_data)


class DetallePredioSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePredio
        exclude = ("reporte",)  # se inyecta en la view


class FotoReporteCreateSerializer(serializers.ModelSerializer):
    # extras para ver nombre original y almacenado
    original_name = serializers.CharField(read_only=True)
    stored_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = FotoReporte
        fields = ["id", "reporte", "tipo", "imagen", "latitud", "longitud",
                  "original_name", "stored_name", "url"]
        extra_kwargs = {"reporte": {"write_only": True}}

    def create(self, validated_data):
        request = self.context.get("request")
        up = request.FILES.get("imagen") if request else None
        instance = super().create(validated_data)
        instance.original_name = up.name if up else None  # solo para respuesta
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["original_name"] = getattr(instance, "original_name", None)
        return rep

    def get_stored_name(self, obj):
        return obj.imagen.name if obj.imagen else None

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.imagen.url) if (request and obj.imagen) else None


# Para devolver todo junto (detalle + foto principal)
class FotoMinSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = FotoReporte
        fields = ["id", "tipo", "url", "latitud", "longitud"]

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.imagen.url) if (request and obj.imagen) else None


class ReporteDetalleViewSerializer(serializers.ModelSerializer):
    detalle_predio = DetallePredioSerializer()
    fotos = FotoMinSerializer(many=True)
    encargado_nombre = serializers.SerializerMethodField()
    sector_nombre = serializers.CharField(source="sector.nombre", read_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id", "tipo", "estado", "observaciones",
            "latitud", "longitud", "fecha_reporte",
            "encargado_nombre", "sector_nombre",
            "detalle_predio", "fotos",
        ]

    def get_encargado_nombre(self, obj):
        return f"{obj.encargado.nombres} {obj.encargado.apellidos}"
