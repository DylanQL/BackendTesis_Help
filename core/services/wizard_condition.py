from typing import Any, Dict, Optional
from django.db import models
from django.core.exceptions import ValidationError

class WizardConditionService:
    """
    Servicio compartido para manejar las condiciones y estado del poste
    en la Parte 3 del wizard (tanto eléctrico como telemático).
    """
    
    def __init__(self, wizard_model: models.Model):
        self.wizard_model = wizard_model
    
    def validate_condition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los datos de condición del poste.
        
        Args:
            data: Diccionario con los datos a validar
                - estado_poste_id: ID del estado físico
                - inclinacion_id: ID del tipo de inclinación
                - propietario_id: ID del propietario
                - altura: Valor decimal de altura (opcional)
                - notas: Texto de observaciones (opcional)
        """
        from ..models.models_telematico import PosteTelematicWizard
        
        # Validar que existe el wizard padre
        if not PosteTelematicWizard.objects.filter(id=data.get('wizard_id')).exists():
            raise ValidationError('El wizard padre no existe')
            
        # Validar altura si se proporciona
        altura = data.get('altura')
        if altura is not None and float(altura) <= 0:
            raise ValidationError('La altura debe ser un valor positivo')
            
        return data
    
    def save_condition(self, 
                      wizard_part3_instance: models.Model,
                      data: Dict[str, Any]) -> models.Model:
        """
        Guarda las condiciones y estado del poste.
        
        Args:
            wizard_part3_instance: Instancia del modelo Parte 3
            data: Datos validados a guardar
        """
        for field, value in data.items():
            if hasattr(wizard_part3_instance, field):
                setattr(wizard_part3_instance, field, value)
                
        wizard_part3_instance.save()
        return wizard_part3_instance
        
    def get_condition(self, wizard_id: int) -> Optional[models.Model]:
        """
        Obtiene las condiciones existentes para un wizard.
        
        Args:
            wizard_id: ID del wizard padre
        """
        try:
            return self.wizard_model.objects.get(id=wizard_id)
        except self.wizard_model.DoesNotExist:
            return None