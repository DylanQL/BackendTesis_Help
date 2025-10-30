from typing import Any, Dict, Optional
from django.db import models
from django.core.exceptions import ValidationError

class WizardCharacteristicsService:
    """
    Servicio compartido para manejar las características físicas de los postes
    en la Parte 2 del wizard (tanto eléctrico como telemático).
    """
    
    def __init__(self, wizard_model: models.Model):
        self.wizard_model = wizard_model
    
    def validate_characteristics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los datos de características comunes.
        
        Args:
            data: Diccionario con los datos a validar
                - estructura_id: ID del tipo de estructura
                - material_id: ID del material
                - zona_instalacion_id: ID de la zona de instalación
                - resistencia_id: ID o valor numérico de resistencia
        """
        from ..models.models_telematico import PosteTelematicWizard
        
        # Validar que existe el wizard padre
        if not PosteTelematicWizard.objects.filter(id=data.get('wizard_id')).exists():
            raise ValidationError('El wizard padre no existe')
            
        # Validar resistencia_valor si se proporciona
        resistencia_valor = data.get('resistencia_valor')
        if resistencia_valor is not None and resistencia_valor < 0:
            raise ValidationError('El valor de resistencia no puede ser negativo')
            
        return data
    
    def save_characteristics(self, 
                           wizard_part2_instance: models.Model,
                           data: Dict[str, Any]) -> models.Model:
        """
        Guarda las características físicas del poste.
        
        Args:
            wizard_part2_instance: Instancia del modelo Parte 2 (eléctrico o telemático)
            data: Datos validados a guardar
        """
        for field, value in data.items():
            if hasattr(wizard_part2_instance, field):
                setattr(wizard_part2_instance, field, value)
                
        wizard_part2_instance.save()
        return wizard_part2_instance
        
    def get_characteristics(self, wizard_id: int) -> Optional[models.Model]:
        """
        Obtiene las características existentes para un wizard.
        
        Args:
            wizard_id: ID del wizard padre
        """
        try:
            return self.wizard_model.objects.get(id=wizard_id)
        except self.wizard_model.DoesNotExist:
            return None