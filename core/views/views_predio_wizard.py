"""
Archivo de vistas del wizard de predios - REFACTORIZADO

Este archivo ha sido reorganizado en módulos más descriptivos para mejorar la mantenibilidad:

1. predio_wizard_start.py - Inicio del wizard
2. predio_wizard_details.py - Detalles y coordenadas
3. predio_wizard_media.py - Medios y publicación

Todos los imports se mantienen aquí para compatibilidad con el sistema de URLs existente.
"""

# Importar vistas de inicio del wizard
from .predio_wizard_start import PredioWizardStartView

# Importar vistas de detalles y coordenadas
from .predio_wizard_details import (
    PredioWizardDetalleUpsertView,
    PredioWizardCoordsView,
    _must_be_encargado_owner
)

# Importar vistas de medios y publicación
from .predio_wizard_media import (
    PredioWizardMediaView,
    PredioWizardPublishView
)

# Exportar todas las vistas para mantener compatibilidad
__all__ = [
    'PredioWizardStartView',
    'PredioWizardDetalleUpsertView',
    'PredioWizardCoordsView',
    'PredioWizardMediaView',
    'PredioWizardPublishView',
    '_must_be_encargado_owner',
]