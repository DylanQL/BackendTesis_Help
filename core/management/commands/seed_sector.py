# core/management/commands/seed_sector.py
from django.core.management.base import BaseCommand
from core.models.models import Sector, Zona

class Command(BaseCommand):
    help = "Crea Sector pk=1 en Zona pk=1."

    def handle(self, *args, **kwargs):
        try:
            zona = Zona.objects.get(pk=1)
        except Zona.DoesNotExist:
            self.stdout.write(self.style.ERROR("Falta Zona pk=1. Ejecuta: python manage.py seed_zona"))
            return

        if not Sector.objects.filter(pk=1).exists():
            s = Sector.objects.create(pk=1, nombre="Sector 1", zona=zona)
            self.stdout.write(self.style.SUCCESS(f"Creado Sector pk=1 (id={s.id})"))
        else:
            s = Sector.objects.get(pk=1)
            self.stdout.write(self.style.WARNING(f"Ya existe Sector pk=1 (id={s.id})"))
