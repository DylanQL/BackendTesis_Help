Migration playbook — pruebas locales antes de tocar producción

Este documento recoge pasos seguros y reproducibles para probar migraciones en una rama local sin tocar la base de datos de producción. Incluye comandos para PowerShell y una plantilla Bash que podrás adaptar y ejecutar en el servidor cuando estés listo.

IMPORTANTE: nunca subas copias de db.sqlite3 al repositorio. Mantén las copias de prueba fuera del control de versiones y protegidas.

Resumen del flujo recomendado:
- Crear una rama local para las pruebas.
- Hacer commits de los cambios de código (sin db.sqlite3).
- Borrar el db.sqlite3 local para recrear la base de datos con el nuevo esquema.
- Ejecutar makemigrations / migrate hasta que todo funcione.
- Documentar cada intento (errores y cambios aplicados).
- Cuando esté todo OK, merge a main y desplegar usando la estrategia de despliegue con puerto alternativo en el servidor.

Pasos principales (resumidos):
1) Crear rama de pruebas:
   - git checkout -b staging-migrations
   - git add .
   - git commit -m "WIP: empezar pruebas de migraciones"

2) Preparar entorno:
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1
   - pip install -r requirements.txt

3) Iterar migraciones localmente:
   - Remove-Item -Force db.sqlite3
   - python manage.py makemigrations
   - python manage.py migrate
   - python manage.py runserver

---

## Seeding: crear usuarios por rol (seed_users)

Para evitar perder el usuario admin al eliminar `db.sqlite3`, hemos añadido un comando de management que crea un usuario por cada rol definido en el modelo `CustomUser`.

- Comando (local):
   - git add .
   - git commit -m "WIP: empezar pruebas de migraciones"
   - python manage.py seed_users --password "miPassSeguro123" --empresa "MiEmpresa" (Importante)

Qué hace el comando:
- Crea (o reutiliza) una `Empresa` con el nombre que pases en `--empresa` (por defecto "Empresa Demo").
- Recorre `CustomUser.ROLES` y crea un usuario por cada rol con valores por defecto para facilitar login en pruebas.

Usuarios/credenciales generadas por defecto (ejemplo cuando ejecutaste el comando con password "miPassSeguro123"):
- Role: superadmin
   - dni: 99999991
   - email: superadmin@example.com
   - contraseña: miPassSeguro123
   - is_staff: True
- Role: admin
   - dni: 99999992
   - email: admin@example.com
   - contraseña: miPassSeguro123
   - is_staff: True
- Role: supervisor
   - dni: 99999993
   - email: supervisor@example.com
   - contraseña: miPassSeguro123
   - is_staff: False
- Role: encargado
   - dni: 99999994
   - email: encargado@example.com
   - contraseña: miPassSeguro123
   - is_staff: False

Notas importantes:
- `USERNAME_FIELD = 'dni'` en el modelo, por lo que para iniciar sesión en el admin o autenticación debes usar el DNI y la contraseña.
- Si el usuario ya existía (mismo `dni`), el seeder no sobrescribe la contraseña por defecto. Para forzar cambio habría que ejecutar el comando con una opción `--force` (no incluida aún) o modificar la contraseña manualmente.
- Cambia las contraseñas por defecto antes de usar en producción.

Ejecutar el seeder dentro del contenedor Docker (cuando pruebes con la instancia temporal o en producción):

 - docker compose exec -T django_app python manage.py seed_users --password "miPassSeguro123" --empresa "MiEmpresa"

O, si estás usando la instancia temporal creada por el workflow con project name `tempdeploy_<ts>` y override, usa:

 - docker compose -p tempdeploy_<ts> -f docker-compose.yml -f docker-compose.override.temp.<ts>.yml exec -T <service> python manage.py seed_users --password "miPassSeguro123" --empresa "MiEmpresa"

Siempre documenta en `docs/migration_attempts.md` el resultado de cada ejecución del seeder (fecha, comando, si creó usuarios nuevos o si ya existían).

4) Documentar cada intento en docs/migration_attempts.md (fecha, comando, error, solución)

5) Pruebas en servidor (sin tocar producción): el workflow soporta NEW_HOST_PORT para crear una instancia temporal en otro puerto.

6) Plantilla de script para servidor (adaptar antes de usar):
   - crear archivo docker-compose.override.temp.<ts>.yml que remapea el puerto
   - docker compose -f docker-compose.yml -f <override> -p tempdeploy_<ts> up -d --build
   - docker compose -p tempdeploy_<ts> exec <service> python manage.py migrate --noinput (con reintentos)

Si quieres, añado un workflow_dispatch para lanzar manualmente pruebas con NEW_HOST_PORT, o creo el script final en cicd/ y un deploy.log en el servidor para registrar backups.
