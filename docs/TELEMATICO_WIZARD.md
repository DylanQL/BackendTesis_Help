# Documentación de Endpoints del Wizard Telemático

Este documento describe los endpoints disponibles para el manejo del wizard de postes telemáticos.

## Endpoints Base

Todos los endpoints requieren autenticación mediante token y están bajo la ruta base `/api/telematico/`.

## Listado de Endpoints

### 1. Listar Wizards Telemáticos

**Endpoint:** `GET /api/telematico/wizard/list/`

Lista todos los wizards de postes telemáticos del usuario autenticado.

**Permisos requeridos:**
- Usuario autenticado

**Respuesta exitosa (200 OK):**
```json
[
    {
        "id": 1,
        "estado": "draft",
        "cables_telematicos": null,
        "codigo": null,
        "cable_electrico": null,
        "elementos_telematicos": [],
        "elementos_electricos": [],
        "creado_en": "2025-10-18T10:00:00Z",
        "actualizado_en": "2025-10-18T10:00:00Z"
    }
]
```

### 2. Iniciar Nuevo Wizard

**Endpoint:** `POST /api/telematico/wizard/iniciar/`

Inicia un nuevo wizard de poste telemático en estado borrador.

**Permisos requeridos:**
- Usuario autenticado

**Respuesta exitosa (201 Created):**
```json
{
    "id": 1,
    "estado": "draft",
    "cables_telematicos": null,
    "codigo": null,
    "cable_electrico": null,
    "elementos_telematicos": [],
    "elementos_electricos": [],
    "creado_en": "2025-10-18T10:00:00Z",
    "actualizado_en": "2025-10-18T10:00:00Z"
}
```

### 3. Guardar Parte 1

**Endpoint:** `POST /api/telematico/wizard/{wizard_id}/parte1/`

Guarda los datos básicos del poste telemático.

**Permisos requeridos:**
- Usuario autenticado
- Ser propietario del wizard
- Wizard en estado borrador

**Parámetros en el cuerpo (JSON):**
```json
{
    "cables_telematicos": 5,
    "codigo": "PT-001",
    "cable_electrico": 2,
    "elementos_telematicos": [],
    "elementos_electricos": []
}
```

**Respuesta exitosa (200 OK):**
```json
{
    "id": 1,
    "cables_telematicos": 5,
    "codigo": "PT-001",
    "cable_electrico": 2,
    "elementos_telematicos": [],
    "elementos_electricos": [],
    "estado": "draft",
    "creado_en": "2025-10-18T10:00:00Z",
    "actualizado_en": "2025-10-18T10:00:00Z"
}
```

**Respuestas de error:**
- 404 Not Found: Wizard no encontrado o no pertenece al usuario
- 400 Bad Request: Datos inválidos

## Validaciones Importantes

1. **Estado del Wizard:**
   - Todas las operaciones de guardado requieren que el wizard esté en estado `draft`
   - Solo el propietario del wizard puede modificarlo
   - Una vez publicado (`published`), no se pueden realizar más modificaciones

2. **Códigos de Error:**
   - `404`: El wizard no existe o no pertenece al usuario autenticado
   - `400`: Los datos enviados son inválidos o incompletos
   - `403`: El usuario no tiene permisos para acceder al wizard

3. **Campos Requeridos:**
   - `codigo`: Identificador único del poste (opcional en draft)
   - Al menos un tipo de cable (`cables_telematicos` o `cable_electrico`)
   - Las listas de elementos pueden estar vacías inicialmente

## Notas Adicionales

- Todos los endpoints retornan timestamps de creación y actualización
- Los datos se guardan automáticamente en formato UTC
- Se puede actualizar parcialmente la información usando PATCH
- Las listas de elementos se guardan como JSON y pueden ser extendidas posteriormente