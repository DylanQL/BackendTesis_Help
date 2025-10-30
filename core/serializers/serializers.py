from rest_framework import serializers
from ..models.models import (
    CustomUser, Sector, Distrito, Zona, DetallePredio, CustomUser, Reporte, 
    PredioWizard, Distrito, Zona, Sector, ElementoElectrico, PosteElectricoWizard, 
    ElementoElectrico, PosteElectricoWizard_2, ParametroCatalogo, 
    PosteElectricoWizard_3, PosteElectricoWizard_4, FotoPosteWizard
)


# --- Asumo que este es tu Serializer para CustomUser ---
# --------------------------------------------------------
# Nuevo/Modificado Serializer para DetallePredio    UserSerializer
class DetallePredioSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePredio
        # Añadir todos los campos del formulario avanzado
        fields = [
            'reporte', 'codigo_sector', 'codigo_predio', 'via_acceso', 'nombre_via_acceso',
            'numero_municipal', 'manzana', 'lote', 'urbanizacion', 'centro_poblado',
            'caracteristicas_predio_tipo', 'denominacion', 'nombre_institucion',
            'comercio', 'actividad', 'vivienda', 'terreno', 'esquina', 'estado_registro'
        ]
        # El campo 'reporte' se establecerá en la vista
        read_only_fields = ('reporte',)

    def validate(self, data):
        """Aplica la lógica condicional basada en caracteristicas_predio_tipo y comercio."""
        
        # 1. Obtener valores clave
        tipo = data.get('caracteristicas_predio_tipo')
        denominacion = data.get('denominacion')
        nombre_institucion = data.get('nombre_institucion')
        comercio = data.get('comercio', 0)
        actividad = data.get('actividad')

        # --- Lógica Condicional por Tipo de Predio ---

        # Caso 1: Tipo 1 (Predio simple) -> Nulificar campos condicionales
        if tipo == 1:
            data['denominacion'] = None
            data['nombre_institucion'] = None
            # Nota: Manzana, lote, urbanizacion, centro_poblado deben ser opcionales y pueden ser None/""
        
        # Casos 3, 4, 5: Denominación Obligatoria
        elif tipo in [3, 4, 5]:
            if not denominacion:
                raise serializers.ValidationError({
                    'denominacion': 'El campo Denominación es obligatorio para los tipos de predio 3, 4 y 5.'
                })
            data['nombre_institucion'] = None # Asegurar que el otro campo institucional es nulo
            
        # Caso 6: Nombre de Institución Obligatorio
        elif tipo == 6:
            if not nombre_institucion:
                raise serializers.ValidationError({
                    'nombre_institucion': 'El campo Nombre de Institución es obligatorio para el tipo de predio 6.'
                })
            data['denominacion'] = None # Asegurar que el otro campo institucional es nulo
            
        # Casos Restantes: Nulificar campos condicionales
        else:
            data['denominacion'] = None
            data['nombre_institucion'] = None

        # --- Lógica Condicional por Comercio ---
        
        # Si Comercio es 0, Actividad debe ser nula.
        if comercio == 0:
            data['actividad'] = None
        
        # Si Comercio es > 0, Actividad debe tener valor (se asume que la validación 'required' del campo se encarga de esto, 
        # pero aquí se fuerza la nulificación en caso de ser 0).

        return data

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['id', 'nombre']

class UserSerializer(serializers.ModelSerializer):
    # TUS DEFINICIONES DE CAMPOS (están perfectas)
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(rol='supervisor'),
        required=False,
        allow_null=True
    )
    sectores = SectorSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        # TU LISTA DE CAMPOS (está más completa, la usamos)
        fields = [
            'id', 'dni', 'nombres', 'apellidos', 'email', 'celular',
            'rol', 'empresa', 'supervisor', 'sectores',
            'estado_contrasena', 'estado', 'password', 'date_joined'
        ]
        read_only_fields = ['date_joined']

    # --- NUEVO MÉTODO DE VALIDACIÓN ---
    def validate(self, data):
        # Evita errores si el serializador se usa sin un request (ej. en tests)
        if 'request' not in self.context:
            return data
            
        request_user = self.context['request'].user
        supervisor = data.get('supervisor')
        
        if request_user.rol == 'admin' and supervisor:
            if supervisor.empresa_id != request_user.empresa_id:
                raise serializers.ValidationError({
                    "supervisor": "El supervisor debe pertenecer a su misma empresa."
                })
        return data

    # --- MÉTODO CREATE MODIFICADO Y MEJORADO ---
    def create(self, validated_data):
        # La lógica de negocio ahora vive aquí
        if 'request' in self.context:
            request_user = self.context['request'].user
            if 'empresa' not in validated_data and hasattr(request_user, 'empresa'):
                validated_data['empresa'] = request_user.empresa
        
        # Usamos el método correcto para crear usuarios
        user = CustomUser.objects.create_user(**validated_data)
        return user

    # TU MÉTODO UPDATE (está perfecto, se mantiene igual)
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        supervisor = validated_data.pop('supervisor', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        # Esto es un poco riesgoso si se manda supervisor=null, lo ajustamos
        if supervisor is not None:
             instance.supervisor = supervisor
        instance.save()
        return instance


#Postes
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

class SectorLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ("id", "nombre")

class ZonaWithSectoresSerializer(serializers.ModelSerializer):
    sectores = SectorLiteSerializer(many=True, read_only=True)

    class Meta:
        model = Zona
        fields = ("id", "nombre", "sectores")

class DistritoTreeSerializer(serializers.ModelSerializer):
    zonas = ZonaWithSectoresSerializer(many=True, read_only=True)

    class Meta:
        model = Distrito
        fields = ("id", "nombre", "zonas")

class DetallePredioAvanzadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePredio
        fields = (
            "reporte",
            "codigo_sector", "codigo_predio",
            "via_acceso", "nombre_via_acceso", "numero_municipal",
            "manzana", "lote", "urbanizacion", "centro_poblado",
            "caracteristicas_predio_tipo",
            "comercio", "actividad",
            "denominacion", "nombre_institucion",
            "vivienda",
            "terreno", "esquina", "homepass",
            "estado_registro",
        )
        read_only_fields = ("reporte",)

    def validate(self, data):
        """
        Reglas solicitadas:
        - caracteristicas_predio_tipo:
            1 => manzana/lote/urbanizacion/centro_poblado/denominacion/nombre_institucion/actividad => NULL/None
            3,4,5 => denominacion OBLIGATORIA, nombre_institucion = None
            6 => nombre_institucion OBLIGATORIO, denominacion = None
            otro => predio básico (sin forzar especiales)
        - comercio == 0 => actividad = None
        """
        tipo = data.get("caracteristicas_predio_tipo")
        comercio = data.get("comercio", 0) or 0

        # Comercio → Actividad
        if int(comercio) == 0:
            data["actividad"] = None

        # Lógica por tipo
        if tipo == 1:
            data["manzana"] = None
            data["lote"] = None
            data["urbanizacion"] = None
            data["centro_poblado"] = None
            data["denominacion"] = None
            data["nombre_institucion"] = None
            data["actividad"] = None

        elif tipo in (3, 4, 5):
            if not (data.get("denominacion") or "").strip():
                raise serializers.ValidationError({
                    "denominacion": "El campo denominación es obligatorio para los tipos 3, 4 y 5."
                })
            data["nombre_institucion"] = None

        elif tipo == 6:
            if not (data.get("nombre_institucion") or "").strip():
                raise serializers.ValidationError({
                    "nombre_institucion": "El campo nombre_institucion es obligatorio para el tipo 6."
                })
            data["denominacion"] = None

        # Otros tipos: no se fuerza nada extra
        return data


# Aquí puedes añadir más serializers según necesites Chango
class PredioWizardStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredioWizard
        fields = ("id", "distrito", "zona", "sector")
        read_only_fields = ("id",)

    def validate(self, attrs):
        distrito = attrs.get("distrito")
        zona = attrs.get("zona")
        sector = attrs.get("sector")

        # 1) Existencia (DRF ya valida FK, pero hacemos chequeos explícitos si llegan IDs)
        if not Distrito.objects.filter(id=distrito.id).exists():
            raise serializers.ValidationError({"distrito": "Distrito no existe."})
        if not Zona.objects.filter(id=zona.id).exists():
            raise serializers.ValidationError({"zona": "Zona no existe."})
        if not Sector.objects.filter(id=sector.id).exists():
            raise serializers.ValidationError({"sector": "Sector no existe."})

        # 2) Consistencia jerárquica
        if zona.distrito_id != distrito.id:
            raise serializers.ValidationError({"zona": f"La zona {zona.id} no pertenece al distrito {distrito.id}."})
        if sector.zona_id != zona.id:
            raise serializers.ValidationError({"sector": f"El sector {sector.id} no pertenece a la zona {zona.id}."})

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        empresa = getattr(user, "empresa", None)
        # Anti-duplicado por combinación
        existing = PredioWizard.objects.filter(
            encargado=user,
            distrito=validated_data["distrito"],
            zona=validated_data["zona"],
            sector=validated_data["sector"],
            estado__in=["started", "in_progress", "ready"]
        ).first()
        if existing:
            # Lanza excepción para que la view responda 409
            raise serializers.ValidationError({"_conflict": str(existing.id)})
        return PredioWizard.objects.create(encargado=user, empresa=empresa, **validated_data)
   
class PredioWizardCoordsSerializer(serializers.Serializer):
    latitud = serializers.FloatField(required=True)
    longitud = serializers.FloatField(required=True)

    def validate(self, attrs):
        lat = attrs["latitud"]
        lon = attrs["longitud"]
        if not (-90.0 <= lat <= 90.0):
            raise serializers.ValidationError({"latitud": "Rango inválido (-90 a 90)."})
        if not (-180.0 <= lon <= 180.0):
            raise serializers.ValidationError({"longitud": "Rango inválido (-180 a 180)."})
        return attrs
    
class PredioWizardDetalleSerializer(serializers.Serializer):
    """
    Valida el JSON del detalle usando DetallePredioAvanzadoSerializer,
    y guarda el payload SANEADO en el wizard (sin crear DetallePredio todavía).
    """
    payload = serializers.JSONField()

    def validate(self, attrs):
        payload = attrs.get("payload", {})
        # Re-usa tu validador avanzado (aplica reglas: tipo 1/3/4/5/6, comercio, nulificaciones)
        ser = DetallePredioAvanzadoSerializer(data=payload)
        ser.is_valid(raise_exception=True)
        # Sustituimos por la data validada/saneada
        attrs["payload"] = ser.validated_data
        return attrs
    
class ElementoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoElectrico  # 👈 nombre real de la clase del modelo
        fields = ('id', 'nombre', 'tipo')
    
class PosteWizardParte1Serializer(serializers.ModelSerializer):
    """
    Serializer para la parte 1 del wizard de poste eléctrico.
    Maneja los datos básicos: tensión, cables, código y elementos.
    """
    tension = serializers.ChoiceField(choices=['BT', 'MT', 'AT'], required=True)
    cables_electricos = serializers.IntegerField(min_value=0, required=True)
    cables_telematicos = serializers.IntegerField(min_value=0, required=True)
    codigo = serializers.CharField(required=True, allow_blank=False)
    elementos_electricos = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True
    )
    elementos_telematicos = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True
    )

    class Meta:
        model = PosteElectricoWizard
        fields = (
            'id', 'tension', 'cables_electricos', 'cables_telematicos', 'codigo',
            'elementos_electricos', 'elementos_telematicos',
            'estado', 'creado_en', 'actualizado_en'
        )
        read_only_fields = ('id', 'estado', 'creado_en', 'actualizado_en')

    def _validate_ids_by_tipo(self, ids, tipo):
        """Valida que todos los IDs existan y correspondan al tipo esperado en ElementoElectrico."""
        if not ids:
            return []

        ids_unicos = list(set(ids))
        qs = ElementoElectrico.objects.filter(id__in=ids_unicos, tipo=tipo).values_list('id', flat=True)
        validos = set(qs)
        invalidos = [i for i in ids_unicos if i not in validos]
        return invalidos

    def validate(self, attrs):
        # Validar cruces con catálogo
        invalid_electricos = self._validate_ids_by_tipo(attrs.get('elementos_electricos', []), 'electrico')
        invalid_telematicos = self._validate_ids_by_tipo(attrs.get('elementos_telematicos', []), 'telematico')

        errors = {}
        if invalid_electricos:
            errors['elementos_electricos'] = [f'IDs inválidos o no eléctricos: {invalid_electricos}']
        if invalid_telematicos:
            errors['elementos_telematicos'] = [f'IDs inválidos o no telemáticos: {invalid_telematicos}']
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

class PosteElectricoWizardSerializer(serializers.ModelSerializer):
    # Validaciones declarativas
    tension = serializers.ChoiceField(choices=['BT', 'MT', 'AT'], required=False, allow_null=True)
    cables_electricos = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    cables_telematicos = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    codigo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    elementos_electricos = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False
    )
    elementos_telematicos = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False
    )

    class Meta:
        model = PosteElectricoWizard
        fields = (
            'id', 'tension', 'cables_electricos', 'cables_telematicos', 'codigo',
            'elementos_electricos', 'elementos_telematicos',
            'estado', 'encargado', 'creado_en', 'actualizado_en'
        )
        read_only_fields = ('id', 'estado', 'encargado', 'creado_en', 'actualizado_en')

    def _validate_ids_by_tipo(self, ids, tipo):
        """Valida que todos los IDs existan y correspondan al tipo esperado en ElementoElectrico."""
        if not ids:
            return []

        ids_unicos = list(set(ids))
        qs = ElementoElectrico.objects.filter(id__in=ids_unicos, tipo=tipo).values_list('id', flat=True)
        validos = set(qs)
        invalidos = [i for i in ids_unicos if i not in validos]
        return invalidos

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        # Traer listas a validar (mezclando partial update con el valor previo si existe)
        ee_ids = attrs.get('elementos_electricos', instance.elementos_electricos if instance else [])
        et_ids = attrs.get('elementos_telematicos', instance.elementos_telematicos if instance else [])

        # Validar cruces con catálogo
        invalid_electricos = self._validate_ids_by_tipo(ee_ids, 'electrico')
        invalid_telematicos = self._validate_ids_by_tipo(et_ids, 'telematico')

        errors = {}
        if invalid_electricos:
            errors['elementos_electricos'] = [f'IDs inválidos o no eléctricos: {invalid_electricos}']
        if invalid_telematicos:
            errors['elementos_telematicos'] = [f'IDs inválidos o no telemáticos: {invalid_telematicos}']
        if errors:
            raise serializers.ValidationError(errors)

        return attrs
    

def _get_param(categoria, pid=None, nombre=None):
    qs = ParametroCatalogo.objects.filter(categoria=categoria, activo=True)
    if pid is not None:
        return qs.filter(id=pid).first()
    if nombre:
        return qs.filter(nombre__iexact=nombre.strip()).first()
    return None

class PosteWizardParte2Serializer(serializers.ModelSerializer):
    # Inputs alternativos (id o nombre)
    estructura_id = serializers.IntegerField(required=False)
    estructura_nombre = serializers.CharField(required=False)
    material_id = serializers.IntegerField(required=False)
    material_nombre = serializers.CharField(required=False)
    zona_instalacion_id = serializers.IntegerField(required=False)
    zona_instalacion_nombre = serializers.CharField(required=False)
    resistencia_id = serializers.IntegerField(required=False)
    resistencia_nombre = serializers.CharField(required=False)
    resistencia_valor = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = PosteElectricoWizard_2
        fields = (
            'id',
            'estructura', 'material', 'zona_instalacion', 'resistencia', 'resistencia_valor',
            'estructura_id','estructura_nombre',
            'material_id','material_nombre',
            'zona_instalacion_id','zona_instalacion_nombre',
            'resistencia_id','resistencia_nombre',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        # Resolver estructura
        estr = _get_param('estructura', attrs.pop('estructura_id', None), attrs.pop('estructura_nombre', None))
        if 'estructura_id' in self.initial_data or 'estructura_nombre' in self.initial_data:
            if not estr:
                raise serializers.ValidationError({'estructura': ['No existe en catálogo (estructura).']})
            attrs['estructura'] = estr

        # Resolver material
        mat = _get_param('material', attrs.pop('material_id', None), attrs.pop('material_nombre', None))
        if 'material_id' in self.initial_data or 'material_nombre' in self.initial_data:
            if not mat:
                raise serializers.ValidationError({'material': ['No existe en catálogo (material).']})
            attrs['material'] = mat

        # Resolver zona_instalacion
        zona = _get_param('zona_instalacion', attrs.pop('zona_instalacion_id', None), attrs.pop('zona_instalacion_nombre', None))
        if 'zona_instalacion_id' in self.initial_data or 'zona_instalacion_nombre' in self.initial_data:
            if not zona:
                raise serializers.ValidationError({'zona_instalacion': ['No existe en catálogo (zona_instalacion).']})
            attrs['zona_instalacion'] = zona

        # Resistencia: catálogo o número libre
        res = _get_param('resistencia', attrs.pop('resistencia_id', None), attrs.pop('resistencia_nombre', None))
        libre = self.initial_data.get('resistencia_valor', None)
        if libre not in (None, ''):
            try:
                libre = int(libre)
            except ValueError:
                raise serializers.ValidationError({'resistencia_valor': ['Debe ser numérico.']})
            if libre < 0:
                raise serializers.ValidationError({'resistencia_valor': ['Debe ser >= 0.']})
            attrs['resistencia'] = None
            attrs['resistencia_valor'] = libre
        else:
            if 'resistencia_id' in self.initial_data or 'resistencia_nombre' in self.initial_data:
                if not res:
                    raise serializers.ValidationError({'resistencia': ['No existe en catálogo (resistencia).']})
                attrs['resistencia'] = res
                attrs['resistencia_valor'] = None

        return attrs    
    
#PosteWizardParte3Serializer

# core/serializers.py
from rest_framework import serializers
from core.models.models import PosteElectricoWizard_3, EstadoFisico, Inclinacion, Propietario


def _get_by_id_or_name(qs, pid=None, nombre=None, field='descripcion'):
    if pid is not None:
        return qs.filter(id=pid).first()
    if nombre:
        # Prohibir múltiples valores tipo "A / B"
        if any(sep in nombre for sep in ('/', ',', ';')):
            return None
        return qs.filter(**{f'{field}__iexact': nombre.strip()}).first()
    return None

class FotoPosteWizardSerializer(serializers.ModelSerializer):
    """
    Serializer para las fotos del poste eléctrico en el wizard.
    """
    class Meta:
        model = FotoPosteWizard
        fields = [
            'id', 'wizard', 'imagen', 'descripcion',
            'orden', 'is_principal', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en']

class PosteWizardParte4Serializer(serializers.ModelSerializer):
    """
    Serializer para la parte 4 del wizard de poste eléctrico.
    Maneja ubicación, fotos y observaciones finales.
    """
    fotos = FotoPosteWizardSerializer(many=True, read_only=True)
    
    class Meta:
        model = PosteElectricoWizard_4
        fields = [
            'id', 'wizard', 'latitud', 'longitud',
            'observaciones', 'fotos', 'creado_en',
            'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def validate(self, data):
        # Validar que latitud y longitud vengan juntos
        if ('latitud' in data and 'longitud' not in data) or \
           ('longitud' in data and 'latitud' not in data):
            raise serializers.ValidationError(
                "Latitud y longitud deben proporcionarse juntos"
            )

        # Validar rangos
        if 'latitud' in data and (data['latitud'] < -90 or data['latitud'] > 90):
            raise serializers.ValidationError(
                {"latitud": "La latitud debe estar entre -90 y 90 grados"}
            )
        
        if 'longitud' in data and (data['longitud'] < -180 or data['longitud'] > 180):
            raise serializers.ValidationError(
                {"longitud": "La longitud debe estar entre -180 y 180 grados"}
            )
            
        return data

class PosteWizardParte3Serializer(serializers.ModelSerializer):
    estado_poste_id = serializers.IntegerField(required=False)
    estado_poste_nombre = serializers.CharField(required=False)
    inclinacion_id = serializers.IntegerField(required=False)
    inclinacion_nombre = serializers.CharField(required=False)
    propietario_id = serializers.IntegerField(required=False)
    propietario_nombre = serializers.CharField(required=False)

    class Meta:
        model = PosteElectricoWizard_3
        fields = (
            'id',
            'altura',
            'estado_poste','inclinacion','propietario','notas',
            'estado_poste_id','estado_poste_nombre',
            'inclinacion_id','inclinacion_nombre',
            'propietario_id','propietario_nombre',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        data = self.initial_data

        # EstadoFisico (campo 'descripcion')
        if 'estado_poste_id' in data or 'estado_poste_nombre' in data:
            est = _get_by_id_or_name(EstadoFisico.objects.all(),
                                     attrs.pop('estado_poste_id', None),
                                     attrs.pop('estado_poste_nombre', None),
                                     field='descripcion')
            if not est:
                raise serializers.ValidationError({
                    'estado_poste': [
                        'Valor inválido o múltiples valores no permitidos. '
                        'Ejemplos válidos: "Pequenas grietas", "Grandes grietas / corroido". '
                        'Si desea "Grandes grietas", envíe exactamente "Grandes grietas".'
                    ]
                })
            attrs['estado_poste'] = est

        # Inclinacion (campo 'descripcion')
        if 'inclinacion_id' in data or 'inclinacion_nombre' in data:
            inc = _get_by_id_or_name(Inclinacion.objects.all(),
                                     attrs.pop('inclinacion_id', None),
                                     attrs.pop('inclinacion_nombre', None),
                                     field='descripcion')
            if not inc:
                raise serializers.ValidationError({'inclinacion': ['Valor inválido o múltiples valores no permitidos.']})
            attrs['inclinacion'] = inc

        # Propietario (campo 'siglas')
        if 'propietario_id' in data or 'propietario_nombre' in data:
            prop = _get_by_id_or_name(Propietario.objects.all(),
                                      attrs.pop('propietario_id', None),
                                      attrs.pop('propietario_nombre', None),
                                      field='siglas')
            if not prop:
                raise serializers.ValidationError({'propietario': ['Valor inválido o múltiples valores no permitidos.']})
            attrs['propietario'] = prop

        return attrs

    def validate_altura(self, value):
        # permitir nulos/blank por el modelo (campo opcional)
        if value is None or value == '':
            return None
        try:
            # Decimal comes through as Decimal or string/float; coerce to float for range checks
            altura = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError('Altura debe ser numérica.')
        if altura < 0:
            raise serializers.ValidationError('Altura debe ser >= 0.')
        if altura > 100:
            raise serializers.ValidationError('Altura parece demasiado alta.')
        return value

class PredioWizardMediaSerializer(serializers.Serializer):
    imagen = serializers.ImageField(required=False, allow_null=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)