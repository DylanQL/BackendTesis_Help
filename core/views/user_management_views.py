"""
Vistas de gestión de usuarios.
Maneja creación, listado, actualización y eliminación de usuarios (supervisores y encargados).
"""
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models.models import CustomUser, Empresa
from ..serializers.serializers import UserSerializer
from ..permissions import (
    IsAdminOrSuperAdmin,
    IsSupervisorOrAdmin,
)

ROLES_VALIDOS = {"superadmin", "admin", "supervisor", "encargado"}


def _password_valida(pw: str) -> bool:
    """
    Valida que la contraseña tenga al menos 8 caracteres,
    contenga letras y números.
    """
    if not pw or len(pw) < 8:
        return False
    has_alpha = any(c.isalpha() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    return has_alpha and has_digit


def filter_users_by_company(queryset, user):
    """
    Filtra el queryset según el rol y la empresa del usuario autenticado.
    Los administradores solo ven usuarios de su misma empresa.
    """
    if user.rol == 'admin' and user.empresa_id:
        return queryset.filter(empresa_id=user.empresa_id)
    return queryset


def check_user_access(request, user_instance):
    """
    Verifica si el usuario autenticado tiene permiso para editar/eliminar el usuario objetivo.
    - Superadmin puede editar/eliminar a todos.
    - Admin solo puede editar/eliminar usuarios de su empresa.
    """
    if request.user.rol == 'superadmin':
        return True
    
    if request.user.rol == 'admin' and user_instance.empresa_id == request.user.empresa_id:
        return True
    
    return False


@api_view(['POST'])
@permission_classes([AllowAny])
def create_usuario(request):
    """
    Crea un usuario. Por defecto rol='encargado'.
    Body (JSON) requerido:
      - dni (8 dígitos)
      - email (único y válido)
      - password (mín. 8, con letras y números)
      - nombres
      - apellidos
    Opcional:
      - rol (superadmin|admin|supervisor|encargado)  [default: encargado]
      - celular
      - empresa_id (FK a Empresa)
      - supervisor_id (si creas un encargado y quieres asociarle un supervisor existente)
    """
    data = request.data

    # Validación de campos requeridos
    required = ['dni', 'email', 'password', 'nombres', 'apellidos']
    missing = [k for k in required if not str(data.get(k) or "").strip()]
    if missing:
        return Response(
            {"detail": f"Faltan campos requeridos: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    dni = str(data['dni']).strip()
    email = str(data['email']).strip().lower()
    password = str(data['password'])
    nombres = str(data['nombres']).strip()
    apellidos = str(data['apellidos']).strip()

    # Validación de DNI
    if not (dni.isdigit() and len(dni) == 8):
        return Response(
            {"detail": "El DNI debe tener 8 dígitos numéricos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validación de email
    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"detail": "Email inválido."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validación de contraseña
    if not _password_valida(password):
        return Response(
            {"detail": "Password débil: mínimo 8 caracteres, con letras y números."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificación de unicidad
    if CustomUser.objects.filter(dni=dni).exists():
        return Response(
            {"detail": "El DNI ya está registrado."},
            status=status.HTTP_409_CONFLICT
        )
    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"detail": "El email ya está registrado."},
            status=status.HTTP_409_CONFLICT
        )

    # Validación de rol
    rol = str(data.get('rol') or 'encargado').strip().lower()
    if rol not in ROLES_VALIDOS:
        return Response(
            {"detail": f"Rol inválido. Usa uno de: {', '.join(sorted(ROLES_VALIDOS))}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validación de empresa
    empresa = None
    empresa_id = data.get('empresa_id')
    if empresa_id:
        try:
            empresa = Empresa.objects.get(id=int(empresa_id))
        except (Empresa.DoesNotExist, ValueError):
            return Response(
                {"detail": "empresa_id inválido o no existe."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Validación de supervisor
    supervisor = None
    supervisor_id = data.get('supervisor_id')
    if supervisor_id:
        try:
            supervisor = CustomUser.objects.get(id=int(supervisor_id))
            if supervisor.rol != 'supervisor':
                return Response(
                    {"detail": "El supervisor_id no corresponde a un usuario con rol 'supervisor'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (CustomUser.DoesNotExist, ValueError):
            return Response(
                {"detail": "supervisor_id inválido o no existe."},
                status=status.HTTP_400_BAD_REQUEST
            )

    celular = str(data.get('celular') or '').strip() or None

    try:
        with transaction.atomic():
            user = CustomUser(
                dni=dni,
                email=email,
                nombres=nombres,
                apellidos=apellidos,
                celular=celular,
                rol=rol,
                empresa=empresa,
                supervisor=supervisor,
                is_active=True,
                is_staff=(rol in {'admin', 'superadmin'}),
            )
            user.set_password(password)
            user.save()

            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response(
            {"detail": "Error de integridad al crear el usuario."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"detail": f"Error al crear usuario: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def create_supervisor(request):
    """
    Crea un supervisor. Requiere permisos de Admin o SuperAdmin.
    La empresa se asigna automáticamente según el usuario autenticado.
    """
    data = request.data.copy()
    data['rol'] = 'supervisor'
    
    serializer = UserSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def create_encargado(request):
    """
    Crea un encargado. Requiere permisos de Admin o SuperAdmin.
    La empresa se asigna automáticamente según el usuario autenticado.
    """
    data = request.data.copy()
    data['rol'] = 'encargado'
    
    serializer = UserSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisorOrAdmin])
def list_supervisores(request):
    """
    Lista todos los supervisores.
    Los administradores solo ven supervisores de su empresa.
    """
    supervisores_qs = CustomUser.objects.filter(rol='supervisor')
    supervisores = filter_users_by_company(supervisores_qs, request.user)
    
    serializer = UserSerializer(supervisores, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisorOrAdmin])
def list_encargados(request):
    """
    Lista todos los encargados.
    Los administradores solo ven encargados de su empresa.
    Los supervisores solo ven sus propios encargados.
    """
    encargados_qs = CustomUser.objects.filter(rol='encargado')
    encargados = filter_users_by_company(encargados_qs, request.user)
    
    # Los supervisores solo ven sus encargados
    if request.user.rol == 'supervisor':
        encargados = encargados.filter(supervisor=request.user)
        
    serializer = UserSerializer(encargados, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def update_user(request, pk):
    """
    Actualiza cualquier usuario (supervisor, encargado, etc.) por su ID.
    Los permisos de quién puede editar a quién son manejados por check_user_access.
    """
    try:
        user_to_edit = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    if not check_user_access(request, user_to_edit):
        return Response(
            {'detail': 'No tiene permiso para editar este usuario.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
        
    serializer = UserSerializer(user_to_edit, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def delete_user(request, pk):
    """
    Elimina cualquier usuario por su ID.
    Los permisos son manejados por check_user_access.
    """
    try:
        user_to_delete = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    if not check_user_access(request, user_to_delete):
        return Response(
            {'detail': 'No tiene permiso para eliminar este usuario.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_to_delete.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
