from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models.models import PredioWizard  # o tu modelo de wizard actual

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def wizard_elementos(request, wizard_id):
    """
    Permite registrar y obtener elementos eléctricos y telemáticos asociados a un wizard existente.
    """

    # 1️⃣ Verificar si el wizard existe y pertenece al usuario autenticado
    try:
        wizard = PredioWizard.objects.get(id=wizard_id, encargado=request.user)
    except PredioWizard.DoesNotExist:
        return Response(
            {"error": f"No existe un wizard con ID {wizard_id} o no pertenece al usuario autenticado."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2️⃣ Si es GET → devolver los elementos guardados
    if request.method == 'GET':
        data = {
            "wizard_id": wizard.id,
            "elementos_electricos": wizard.detalle_payload.get("elementos_electricos", []),
            "elementos_telematicos": wizard.detalle_payload.get("elementos_telematicos", [])
        }
        return Response(data, status=status.HTTP_200_OK)

    # 3️⃣ Si es POST → actualizar ambos tipos de elementos
    if request.method == 'POST':
        elementos_electricos = request.data.get("elementos_electricos", [])
        elementos_telematicos = request.data.get("elementos_telematicos", [])

        # Validación: deben ser listas de números
        if not isinstance(elementos_electricos, list) or not all(isinstance(i, int) for i in elementos_electricos):
            return Response({"error": "elementos_electricos debe ser una lista de números."}, status=400)

        if not isinstance(elementos_telematicos, list) or not all(isinstance(i, int) for i in elementos_telematicos):
            return Response({"error": "elementos_telematicos debe ser una lista de números."}, status=400)

        # 4️⃣ Actualizar el payload dentro del wizard
        detalle = wizard.detalle_payload or {}
        detalle["elementos_electricos"] = elementos_electricos
        detalle["elementos_telematicos"] = elementos_telematicos
        wizard.detalle_payload = detalle
        wizard.save(update_fields=["detalle_payload"])

        return Response({
            "success": "Elementos actualizados correctamente.",
            "wizard_id": wizard.id,
            "elementos_electricos": elementos_electricos,
            "elementos_telematicos": elementos_telematicos
        }, status=status.HTTP_200_OK)
