Core app — guía de refactor incremental
=====================================

Qué haremos primero
--------------------
1. Crear paquetes vacíos para `models`, `views`, `serializers` y `tests` con `__init__.py` que re-exporten las definiciones actuales.
2. Mover `serializers.py` a `serializers/serializers.py` como prueba piloto.
3. Ejecutar pruebas locales y lanzar el servidor.

Reglas de oro
------------
- Mueve archivos con `git mv` para preservar historial.
- No cambies `class` names ni `app_label`.
- Haz commits pequeños y ejecuta `manage.py test` tras cada movimiento.

Cómo empezar (comandos)
-----------------------
```powershell
git checkout -b refactor/core-packages
mkdir core\models
echo "# re-exports" > core\models\__init__.py
mkdir core\views
echo "# re-exports" > core\views\__init__.py
mkdir core\serializers
echo "# re-exports" > core\serializers\__init__.py
mkdir core\tests
echo "# test package" > core\tests\__init__.py
git add core\models core\views core\serializers core\tests
git commit -m "chore: create core subpackages for incremental refactor"
```

Próximo paso (opcional)
-----------------------
Si me confirmas, creo los `__init__.py` con re-exports básicos y muevo `serializers.py` a `core/serializers/serializers.py` en esta rama y ejecuto una prueba local rápida.
