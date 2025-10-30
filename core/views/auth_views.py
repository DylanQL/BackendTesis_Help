"""
Vistas de autenticación y login.
Maneja la autenticación de usuarios mediante DNI y contraseña.
"""
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers.serializers import UserSerializer


class LoginView(APIView):
    """Vista para autenticación de usuarios."""
    
    @swagger_auto_schema(
        operation_description="Autenticación de usuario por DNI y contraseña.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["dni", "password"],
            properties={
                "dni": openapi.Schema(type=openapi.TYPE_STRING, description="DNI del usuario"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Tokens de acceso y datos del usuario",
                examples={
                    "application/json": {
                        "refresh": "<refresh_token>",
                        "access": "<access_token>",
                        "user": {
                            "id": 1,
                            "dni": "12345678",
                            "email": "usuario@ejemplo.com",
                            "rol": "encargado"
                        }
                    }
                }
            ),
            401: "Credenciales incorrectas",
            403: "Usuario inactivo."
        }
    )
    def post(self, request):
        dni = request.data.get('dni')
        password = request.data.get('password')
        user = authenticate(request, username=dni, password=password)
        
        if user is not None:
            # Verificación de estado activo
            if not user.is_active or getattr(user, 'estado', None) == 'inactivo':
                return Response(
                    {'detail': 'Usuario inactivo.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            })
        
        return Response(
            {'detail': 'Credenciales incorrectas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


login_view = LoginView.as_view()
