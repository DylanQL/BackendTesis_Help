# core/management/commands/seed_distrito.py
from django.core.management.base import BaseCommand
from core.models.models import Distrito, Empresa

class Command(BaseCommand):
    help = "Crea Distrito pk=1 si no existe (opcionalmente lo asocia a alguna Empresa)."

    def handle(self, *args, **kwargs):
        # Usa una empresa si quieres enlazar (opcional)
        empresa = Empresa.objects.first()  # o None si no tienes
        if not Distrito.objects.filter(pk=1).exists():
            d = Distrito.objects.create(pk=1, nombre="Distrito Demo", empresa=empresa, activo=True)
            self.stdout.write(self.style.SUCCESS(f"Creado Distrito pk=1 (id={d.id})"))
        else:
            d = Distrito.objects.get(pk=1)
            self.stdout.write(self.style.WARNING(f"Ya existe Distrito pk=1 (id={d.id})"))
