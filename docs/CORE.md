Core app — propuesta de reestructuración
======================================

Objetivo
--------
Mejorar la legibilidad y la escalabilidad del paquete `core` dividiendo responsabilidades, facilitando tests y simplificando imports.

Principios
---------
- Separar por capas: modelos, serializers, vistas (API/views), forms, admin, management, tests.
- Mantener compatibilidad incremental: crear paquetes y re-exportar mientras se mueven archivos gradualmente.
- Documentar convenciones y cómo hacer refactors seguros (git mv, pruebas locales).

Propuesta de estructura
-----------------------

core/
  __init__.py
  apps.py
  models/                # paquete nuevo (opcional, permite dividir modelos por dominio)
    __init__.py          # importará y re-exportará los modelos más usados
    user.py
    ubicaciones.py
    reporte.py
    wizards.py
  views/                 # paquete para views, cada archivo por área
    __init__.py
    poste.py
    predio.py
    catalogos.py
    admin_views.py
  serializers/           # paquete para serializers
    __init__.py
    postes.py
    predio.py
  admin.py               # puede quedarse o dividirse en admin/ con módulos por modelo
  forms.py
  managers.py
  permissions.py
  urls.py
  tests/                 # pruebas organizadas por módulo
    __init__.py
    test_models.py
    test_views.py
  management/            # ya existe, mantener

Razonamiento y beneficios
-------------------------
- Claridad: cada archivo más pequeño y con responsabilidad única.
- Escalabilidad: facilita trabajo simultáneo en distintas áreas (por ejemplo, frontend y API teams).
- Testing: los tests pueden mapearse directamente a módulos pequeños.
- Import ergonomics: `from core.models import CustomUser` seguirá funcionando si `core/models/__init__.py` re-exporta.

Plan incremental (seguro)
------------------------
1. Documentar (este archivo) y acordar convenciones.
2. Crear paquetes vacíos `core/models`, `core/views`, `core/serializers`, `core/tests` con `__init__.py` que re-exporten desde los archivos actuales. Esto no rompe imports externos.
3. Mover (git mv) archivos individualmente en pequeños commits, actualizando imports y ejecutando tests/local server.
4. Opcional: dividir `admin.py` en `core/admin/` si crece mucho.

Ejemplo de re-export (core/models/__init__.py)
--------------------------------------------
from ..models import CustomUser, Empresa  # mientras movemos el contenido, mantener compatibilidad

Notas sobre migraciones
-----------------------
- Mover definiciones de modelos cambia rutas de import, pero Django sigue usando el nombre de la app y el modelo (app_label.ModelName). Para evitar problemas de migraciones debes:
  - No cambiar `app_label` ni el nombre de la app.
  - Mantener los modelos con el mismo `class` name.
  - Realizar los movimientos en un commit separado sin modificar la definición de clases, luego ejecutar `makemigrations` sólo si hay cambios reales en modelos.

Próximos pasos sugeridos
-----------------------
1. Crear los packages con `__init__.py` que re-exporten (commit pequeño).
2. Mover un área de baja complejidad (por ejemplo, `serializers.py` → `serializers/serializers.py`) y actualizar imports.
3. Ejecutar `python manage.py test` y `python manage.py runserver` localmente.

Si quieres, implemento el paso 1 ahora (crear paquetes y `__init__.py` con re-exports). Lo dejo a tu confirmación.
