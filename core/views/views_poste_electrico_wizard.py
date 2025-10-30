from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models.models import (
    PosteElectricoWizard,
    PosteElectricoWizard_2,
    PosteElectricoWizard_3,
    PosteElectricoWizard_4,
    FotoPosteWizard
)
from ..serializers.serializers import (
    PosteElectricoWizardSerializer,
    PosteWizardParte1Serializer,
    PosteWizardParte2Serializer,
    PosteWizardParte3Serializer,
    PosteWizardParte4Serializer
)
from ..services.wizard_characteristics import WizardCharacteristicsService
from ..services.wizard_condition import WizardConditionService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_wizard_iniciar(request):
    """
    Inicia un nuevo wizard de poste eléctrico.
    Crea un registro vacío y retorna el ID para los siguientes pasos.
    """
    with transaction.atomic():
        # Crear wizard vacío
        wizard = PosteElectricoWizard.objects.create(
            encargado=request.user,
            estado='draft'
        )
        
        serializer = PosteElectricoWizardSerializer(wizard)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_parte1_save(request, wizard_id):
    """
    Guarda los datos de la parte 1 del wizard de poste eléctrico.
    """
    try:
        wizard = PosteElectricoWizard.objects.get(
            id=wizard_id,
            encargado=request.user,
            estado='draft'
        )
    except PosteElectricoWizard.DoesNotExist:
        return Response(
            {"detail": "Wizard no encontrado o no en estado draft"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PosteWizardParte1Serializer(
        wizard,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        with transaction.atomic():
            wizard = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_parte2_save(request, wizard_id):
    """
    Guarda los datos de la parte 2 del wizard de poste eléctrico.
    Utiliza el servicio compartido WizardCharacteristicsService.
    """
    try:
        # 1. Verificar que existe el wizard y pertenece al usuario
        wizard = PosteElectricoWizard.objects.get(
            id=wizard_id,
            encargado=request.user,
            estado='draft'
        )
    except PosteElectricoWizard.DoesNotExist:
        return Response(
            {"detail": "Wizard no encontrado o no en estado draft"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2. Inicializar el servicio de características
    characteristics_service = WizardCharacteristicsService(PosteElectricoWizard_2)
    
    try:
        # 3. Validar datos usando el servicio
        data = request.data.copy()
        data['wizard_id'] = wizard_id
        validated_data = characteristics_service.validate_characteristics(data)
        
        # 4. Obtener o crear instancia de Parte 2
        parte2, _ = PosteElectricoWizard_2.objects.get_or_create(wizard=wizard)
        
        # 5. Guardar usando el servicio
        parte2 = characteristics_service.save_characteristics(parte2, validated_data)
        
        # 6. Serializar y retornar respuesta
        serializer = PosteWizardParte2Serializer(parte2)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_parte3_save(request, wizard_id):
    """
    Guarda los datos de la parte 3 del wizard de poste eléctrico.
    Utiliza el servicio compartido WizardConditionService.
    """
    try:
        # 1. Verificar que existe el wizard y pertenece al usuario
        wizard = PosteElectricoWizard.objects.get(
            id=wizard_id,
            encargado=request.user,
            estado='draft'
        )
    except PosteElectricoWizard.DoesNotExist:
        return Response(
            {"detail": "Wizard no encontrado o no en estado draft"},
            status=status.HTTP_404_NOT_FOUND
        )
        
    # 2. Verificar que existe parte 2
    if not hasattr(wizard, 'caracteristicas'):
        return Response(
            {"detail": "Debe completar la Parte 2 antes de continuar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Inicializar el servicio de condiciones
    condition_service = WizardConditionService(PosteElectricoWizard_3)
    
    try:
        # 4. Validar datos usando el servicio
        data = request.data.copy()
        data['wizard_id'] = wizard_id
        validated_data = condition_service.validate_condition(data)
        
        # 5. Obtener o crear instancia de Parte 3
        parte3, _ = PosteElectricoWizard_3.objects.get_or_create(wizard=wizard)
        
        # 6. Guardar usando el servicio
        parte3 = condition_service.save_condition(parte3, validated_data)
        
        # 7. Serializar y retornar respuesta
        serializer = PosteWizardParte3Serializer(parte3)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_parte4_save(request, wizard_id):
    """
    Guarda los datos de la parte 4 del wizard de poste eléctrico.
    Maneja ubicación, fotos y observaciones finales.
    """
    try:
        # 1. Verificar que existe el wizard y pertenece al usuario
        wizard = PosteElectricoWizard.objects.get(
            id=wizard_id,
            encargado=request.user,
            estado='draft'
        )
    except PosteElectricoWizard.DoesNotExist:
        return Response(
            {"detail": "Wizard no encontrado o no en estado draft"},
            status=status.HTTP_404_NOT_FOUND
        )
        
    # 2. Verificar que existe parte 3
    if not hasattr(wizard, 'condicion'):
        return Response(
            {"detail": "Debe completar la Parte 3 antes de continuar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # 3. Procesar datos de ubicación y observaciones
            data = request.data.copy()
            parte4, _ = PosteElectricoWizard_4.objects.get_or_create(wizard=wizard)
            
            serializer = PosteWizardParte4Serializer(
                parte4,
                data=data,
                partial=True
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            parte4 = serializer.save()
            
            # 4. Procesar fotos si las hay
            fotos = request.FILES.getlist('fotos', [])
            for idx, foto in enumerate(fotos):
                FotoPosteWizard.objects.create(
                    wizard=parte4,
                    imagen=foto,
                    orden=idx,
                    is_principal=(idx == 0)  # Primera foto como principal
                )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
    except ValidationError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def poste_electrico_wizard_publicar(request, wizard_id):
    """
    Publica un wizard de poste eléctrico completo.
    Verifica que todas las partes requeridas estén completas.
    """
    try:
        # 1. Obtener wizard y verificar propiedad
        wizard = PosteElectricoWizard.objects.get(
            id=wizard_id,
            encargado=request.user,
            estado='draft'
        )
    except PosteElectricoWizard.DoesNotExist:
        return Response(
            {"detail": "Wizard no encontrado o no en estado draft"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2. Verificar que todas las partes estén completas
    if not all([
        hasattr(wizard, 'caracteristicas'),  # Parte 2
        hasattr(wizard, 'condicion'),        # Parte 3
        hasattr(wizard, 'ubicacion'),        # Parte 4
    ]):
        return Response(
            {"detail": "Faltan partes del wizard por completar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # 3. Cambiar estado a publicado
            wizard.estado = 'published'
            wizard.save()
            
            # 4. Retornar datos actualizados
            serializer = PosteElectricoWizardSerializer(wizard)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def poste_electrico_wizard_list(request):
    """
    Lista todos los wizards de poste eléctrico del usuario autenticado.
    Incluye tanto los que están en borrador como los publicados.
    """
    registros = (PosteElectricoWizard.objects
                .filter(encargado=request.user)
                .order_by('-actualizado_en'))
                
    serializer = PosteElectricoWizardSerializer(registros, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)