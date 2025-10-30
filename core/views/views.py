"""
Archivo de vistas principal - REFACTORIZADO

Este archivo ha sido reorganizado en módulos más descriptivos para mejorar la mantenibilidad:

1. auth_views.py - Autenticación y login
2. user_management_views.py - Gestión de usuarios (crear, listar, actualizar, eliminar)
3. catalog_views.py - Catálogos de elementos y formularios

Todos los imports se mantienen aquí para compatibilidad con el sistema de URLs existente.
"""

# Importar vistas de autenticación
from .auth_views import LoginView, login_view

# Importar vistas de gestión de usuarios
from .user_management_views import (
    create_usuario,
    create_supervisor,
    create_encargado,
    list_supervisores,
    list_encargados,
    update_user,
    delete_user,
    filter_users_by_company,
    check_user_access,
)

# Importar vistas de catálogos y formularios
from .catalog_views import (
    elementos_catalogo,
    poste_electrico_save,
    poste_electrico_list,
)

# Exportar todas las vistas para mantener compatibilidad
__all__ = [
    # Autenticación
    'LoginView',
    'login_view',
    # Gestión de usuarios
    'create_usuario',
    'create_supervisor',
    'create_encargado',
    'list_supervisores',
    'list_encargados',
    'update_user',
    'delete_user',
    'filter_users_by_company',
    'check_user_access',
    # Catálogos
    'elementos_catalogo',
    'poste_electrico_save',
    'poste_electrico_list',
]