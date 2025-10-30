# core/management/commands/seed_zona.py
from django.core.management.base import BaseCommand
from core.models.models import Zona, Distrito, Proyecto

class Command(BaseCommand):
    help = "Crea Zona pk=1 en Distrito pk=1."

    def handle(self, *args, **kwargs):
        try:
            distrito = Distrito.objects.get(pk=1)
        except Distrito.DoesNotExist:
            self.stdout.write(self.style.ERROR("Falta Distrito pk=1. Ejecuta: python manage.py seed_distrito"))
            return

        proyecto = Proyecto.objects.first()  # opcional, si tu modelo lo requiere
        if not Zona.objects.filter(pk=1).exists():
            z = Zona.objects.create(pk=1, nombre="Zona A", distrito=distrito, proyecto=proyecto)
            self.stdout.write(self.style.SUCCESS(f"Creada Zona pk=1 (id={z.id})"))
        else:
            z = Zona.objects.get(pk=1)
            self.stdout.write(self.style.WARNING(f"Ya existe Zona pk=1 (id={z.id})"))
