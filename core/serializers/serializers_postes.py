# core/serializers.py
from rest_framework import serializers
from ..models.models import (
    Reporte, DetallePosteElectrico, DetallePredio, FotoReporte,
    ElementoElectrico, ElementoTelematico,
    TipoEstructura, Material, ZonaInstalacion, Resistencia,
    EstadoFisico, Inclinacion, Propietario
)

class PosteReporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ("id","tipo","proyecto","zona","sector","estado","observaciones","latitud","longitud")

    def create(self, validated_data):
        validated_data["encargado"] = self.context["request"].user
        return super().create(validated_data)


class PosteDetalleElectricoSerializer(serializers.ModelSerializer):
    elementos_electricos = serializers.PrimaryKeyRelatedField(
        queryset=ElementoElectrico.objects.all(), many=True, required=False
    )
    elementos_telematicos = serializers.PrimaryKeyRelatedField(
        queryset=ElementoTelematico.objects.all(), many=True, required=False
    )

    class Meta:
        model = DetallePosteElectrico
        fields = (
            "tension","codigo","cables_electricos","cables_telematicos",
            "elementos_electricos","elementos_telematicos",
            "tipo_estructura","material","zona_instalacion","resistencia",
            "estado_fisico","inclinacion","altura","propietario",
        )


class PredioDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePredio
        fields = (
            "codigo_sector","codigo_predio","via_acceso","numero_municipal",
            "terreno","denominacion","comercio","vivienda","homepass",
            "esquina","actividad","nombre_institucion","estado_registro",
        )


class PosteFotoCreateSerializer(serializers.ModelSerializer):
    original_name = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FotoReporte
        fields = ("id","tipo","imagen","latitud","longitud","original_name","url")

    def get_original_name(self, obj):
        return getattr(obj.imagen, "name", "").split("/")[-1]

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.imagen.url) if request and obj.imagen else None


class PosteFotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoReporte
        fields = ("id","tipo","latitud","longitud","imagen")


class PosteReporteDetailSerializer(serializers.ModelSerializer):
    detalle_poste = serializers.SerializerMethodField()
    detalle_predio = serializers.SerializerMethodField()
    fotos = PosteFotoSerializer(many=True, read_only=True)
    encargado_nombre = serializers.SerializerMethodField()
    sector_nombre = serializers.CharField(source="sector.nombre", read_only=True)

    class Meta:
        model = Reporte
        fields = (
            "id","tipo","estado","observaciones","latitud","longitud","fecha_reporte",
            "encargado_nombre","sector_nombre","detalle_poste","detalle_predio","fotos"
        )

    def get_encargado_nombre(self, obj):
        return f"{obj.encargado.nombres} {obj.encargado.apellidos}"

    def get_detalle_poste(self, obj):
        d = getattr(obj, "detalle_electrico", None)
        if not d:
            return None
        return {
            "tension": d.tension,
            "codigo": d.codigo,
            "cables_electricos": d.cables_electricos,
            "cables_telematicos": d.cables_telematicos,
            "resistencia": d.resistencia.valor if d.resistencia else None,
            "altura": str(d.altura),
            "propietario": d.propietario.siglas if d.propietario else None,
            "tipo_estructura": d.tipo_estructura.nombre if d.tipo_estructura else None,
            "material": d.material.nombre if d.material else None,
            "zona_instalacion": d.zona_instalacion.nombre if d.zona_instalacion else None,
            "estado_fisico": d.estado_fisico.descripcion if d.estado_fisico else None,
        }

    def get_detalle_predio(self, obj):
        dp = getattr(obj, "detalle_predio", None)
        return PredioDetalleSerializer(dp).data if dp else None
