from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import Sector, Zona, Distrito

class Command(BaseCommand):
    help = "Elimina TODAS las ubicaciones (Sector/Zona/Distrito). ¡Cuidado!"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        Sector.objects.all().delete()
        Zona.objects.all().delete()
        Distrito.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Ubicaciones eliminadas."))
