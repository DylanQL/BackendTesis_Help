# core/urls.py
from django.urls import path
# --- Auth & Usuarios ---
from .views.views import (
    login_view,
    create_supervisor, create_encargado, create_usuario,
    list_supervisores, list_encargados,
    update_user, delete_user,
)

# --- Catálogos / Árbol de ubicación ---
from .views.views_catalogos import CatalogoArbolView

# --- Predios (endpoints “legacy” directos al Reporte) ---
from .views.views_predio import (
    ReporteCreateView,
    DetallePredioUpsertView,
    FotoReporteUploadView,
    ReporteDetailView,
    DetallePredioAvanzadoUpsertView,  # <- marcar para deprecación futura
)

# --- Postes ---
from .views.views_postes import (
    PosteReporteCreateView,
    PosteDetalleElectricoUpsertView,
    PredioDetalleUpsertView,
    PosteFotoCreateView,
    PosteReporteRetrieveView,
)

# --- Wizard de Predios (nuevo flujo recomendado) ---
from .views.views_predio_wizard import (
    PredioWizardStartView,
    PredioWizardCoordsView,
    PredioWizardDetalleUpsertView,
    PredioWizardMediaView,     # foto + observaciones en wizard
    PredioWizardPublishView,   # publica y crea Reporte + DetallePredio (+ foto principal si hay)
)

# --- Operaciones genéricas sobre Reportes publicados ---
from .views.views_reportes import (
    ReporteObservacionesUpdateView,  # PATCH observaciones de un Reporte
    ReporteCompletarView,            # POST completar/actualizar foto principal + obs
    PredioReporteListView, 
)
from .views.views_wizard_elementos import wizard_elementos
from .views.views_estadisticas import estadisticas_postes
from .views.views_telematico import (
    telematico_wizard_iniciar,
    telematico_parte1_save,
    telematico_parte2_save,
    telematico_parte3_save,
    telematico_parte4_save,
    telematico_wizard_publicar,
    telematico_wizard_list
)
from .views.views_poste_electrico_wizard import (
    poste_electrico_wizard_iniciar,
    poste_electrico_parte1_save,
    poste_electrico_parte2_save,
    poste_electrico_parte3_save,
    poste_electrico_parte4_save,
    poste_electrico_wizard_publicar,
    poste_electrico_wizard_list
)
from core.views.views import elementos_catalogo
from core.views.views_catalogos import catalogo_poste_opciones
urlpatterns = [
    # ---------------- Auth & Usuarios ----------------
    path("login/", login_view, name="login"),

    path("usuarios/supervisor/", create_supervisor, name="create_supervisor"),
    path("usuarios/encargado/", create_encargado, name="create_encargado"),
    path("usuarios/", create_usuario, name="create_usuario"),

    path("usuarios/supervisores/", list_supervisores, name="list_supervisores"),
    path("usuarios/encargados/", list_encargados, name="list_encargados"),
    
    path('usuarios/editar/<int:pk>/', update_user, name='update-user'),
    path('usuarios/eliminar/<int:pk>/', delete_user, name='delete-user'),

    # ---------------- Catálogos ----------------
    path("catalogos/arbol", CatalogoArbolView.as_view(), name="catalogo_arbol"),

    # ---------------- Predios (legacy directos) ----------------
    path("predios/reportes/", ReporteCreateView.as_view(), name="reporte-create"),
    path("predios/reportes/<int:reporte_id>/detalle/", DetallePredioUpsertView.as_view(), name="reporte-detalle-upsert"),
    path("predios/reportes/<int:reporte_id>/fotos/", FotoReporteUploadView.as_view(), name="reporte-foto-upload"),
    path("predios/reportes/<int:reporte_id>/", ReporteDetailView.as_view(), name="reporte-detail"),

    # Temporal / Demo (marcado para deprecación cuando el wizard esté estable)
    path("reportes/<int:reporte_id>/detalle-predio-avanzado/", DetallePredioAvanzadoUpsertView.as_view(), name="detalle-predio-avanzado"),

    # ---------------- Postes ----------------
    path("postes/reportes/", PosteReporteCreateView.as_view(), name="p_poste_reporte_create"),
    path("postes/reportes/<int:pk>/detalle-electrico/", PosteDetalleElectricoUpsertView.as_view(), name="p_poste_detalle_electrico"),
    path("postes/reportes/<int:pk>/detalle-predio/", PredioDetalleUpsertView.as_view(), name="p_poste_detalle_predio"),
    path("postes/reportes/<int:pk>/fotos/", PosteFotoCreateView.as_view(), name="p_poste_foto_upload"),
    path("postes/reportes/<int:pk>/", PosteReporteRetrieveView.as_view(), name="p_poste_reporte_detail"),

    # ---------------- Wizard de Predios (nuevo flujo) ----------------
    path("predios/wizard/start/", PredioWizardStartView.as_view(), name="predio-wizard-start"),
    path("predios/wizard/<uuid:wizard_id>/coords/", PredioWizardCoordsView.as_view(), name="predio-wizard-coords"),
    path("predios/wizard/<uuid:wizard_id>/detalle/", PredioWizardDetalleUpsertView.as_view(), name="predio-wizard-detalle"),
    path("predios/wizard/<uuid:wizard_id>/media/", PredioWizardMediaView.as_view(), name="predio-wizard-media"),
    path("predios/wizard/<uuid:wizard_id>/publish/", PredioWizardPublishView.as_view(), name="predio-wizard-publish"),

    # ---------------- Operaciones sobre Reportes publicados predio ----------------
    path("reportes/<int:reporte_id>/observaciones/", ReporteObservacionesUpdateView.as_view(), name="reporte-observaciones-update"),
    path("reportes/<int:reporte_id>/completar/", ReporteCompletarView.as_view(), name="reporte-completar"),

    path("predios/reportes/list/", PredioReporteListView.as_view(), name="predio-reporte-list"),

    # ---------------- Demo elementos electricos ----------------
    path('wizard/<int:wizard_id>/elementos/', wizard_elementos, name='wizard_elementos'),
    
    # ---------------- Estadísticas de Postes ----------------
    path('postes/estadisticas/', estadisticas_postes, name='postes_estadisticas'),

    # ---------------- Wizard Poste Telemático ----------------
    path('wizard/telematico/iniciar/', telematico_wizard_iniciar, name='telematico_wizard_iniciar'),
    path('wizard/telematico/<int:wizard_id>/parte1/', telematico_parte1_save, name='telematico_parte1_save'),
    path('wizard/telematico/<int:wizard_id>/parte2/', telematico_parte2_save, name='telematico_parte2_save'),
    path('wizard/telematico/<int:wizard_id>/parte3/', telematico_parte3_save, name='telematico_parte3_save'),
    path('wizard/telematico/<int:wizard_id>/parte4/', telematico_parte4_save, name='telematico_parte4_save'),
    path('wizard/telematico/<int:wizard_id>/publicar/', telematico_wizard_publicar, name='telematico_wizard_publicar'),
    path('wizard/telematico/listar/', telematico_wizard_list, name='telematico_wizard_list'),

    # ---------------- Wizard Poste Eléctrico ----------------
    path('wizard/poste-electrico/iniciar/', poste_electrico_wizard_iniciar, name='poste_electrico_wizard_iniciar'),
    path('wizard/poste-electrico/<int:wizard_id>/parte1/', poste_electrico_parte1_save, name='poste_electrico_parte1_save'),
    path('wizard/poste-electrico/<int:wizard_id>/parte2/', poste_electrico_parte2_save, name='poste_electrico_parte2_save'),
    path('wizard/poste-electrico/<int:wizard_id>/parte3/', poste_electrico_parte3_save, name='poste_electrico_parte3_save'),
    path('wizard/poste-electrico/<int:wizard_id>/parte4/', poste_electrico_parte4_save, name='poste_electrico_parte4_save'),
    path('wizard/poste-electrico/<int:wizard_id>/publicar/', poste_electrico_wizard_publicar, name='poste_electrico_wizard_publicar'),
    path('wizard/poste-electrico/listar/', poste_electrico_wizard_list, name='poste_electrico_wizard_list'),

    # ---------------- Elementos y Catálogos ----------------
    path('elementos', elementos_catalogo, name='elementos_catalogo'),
    path('catalogos/poste-opciones', catalogo_poste_opciones, name='catalogo_poste_opciones'),
]