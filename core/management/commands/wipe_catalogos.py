from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import (
    TipoEstructura, Material, ZonaInstalacion, Resistencia,
    EstadoFisico, Inclinacion, Propietario, ElementoElectrico, ElementoTelematico
)

class Command(BaseCommand):
    help = "Elimina TODOS los catálogos. ¡Cuidado!"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for m in [ElementoTelematico, ElementoElectrico, Propietario, Inclinacion, EstadoFisico,
                  Resistencia, ZonaInstalacion, Material, TipoEstructura]:
            m.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Catálogos eliminados."))
