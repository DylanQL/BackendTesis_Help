from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import (
    TipoEstructura, Material, ZonaInstalacion, Resistencia,
    EstadoFisico, Inclinacion, Propietario, ElementoElectrico, ElementoTelematico
)

DATA = {
    "TipoEstructura": ["MADERA", "CONCRETO", "METÁLICA", "COMPUESTO"],
    "Material": ["MADERA", "CONCRETO", "ACERO GALVANIZADO", "FIBRA"],
    "ZonaInstalacion": ["VEREDA", "BERMA", "CALZADA", "JARDÍN"],
    "Resistencia": ["ND", "OTRO", "100", "150", "200"],
    "EstadoFisico": ["BUENO", "REGULAR", "MALO", "CRÍTICO"],
    "Inclinacion": ["0-5°", "5-10°", "10-15°", ">15°"],
    "Propietario": ["MUNI", "EDEL", "TELECO", "OTRO"],
    "ElementoElectrico": ["LUMINARIA", "TRANSFORMADOR", "SECCIONADOR", "RECONECTADOR"],
    "ElementoTelematico": ["CAJA NAP", "CABLE COAXIAL", "CABLE FIBRA", "AMPLIFICADOR"],
}

CREATE_FUNCS = {
    "TipoEstructura": lambda v: TipoEstructura.objects.get_or_create(nombre=v),
    "Material": lambda v: Material.objects.get_or_create(nombre=v),
    "ZonaInstalacion": lambda v: ZonaInstalacion.objects.get_or_create(nombre=v),
    "Resistencia": lambda v: Resistencia.objects.get_or_create(valor=v),
    "EstadoFisico": lambda v: EstadoFisico.objects.get_or_create(descripcion=v),
    "Inclinacion": lambda v: Inclinacion.objects.get_or_create(descripcion=v),
    "Propietario": lambda v: Propietario.objects.get_or_create(siglas=v),
    "ElementoElectrico": lambda v: ElementoElectrico.objects.get_or_create(nombre=v),
    "ElementoTelematico": lambda v: ElementoTelematico.objects.get_or_create(nombre=v),
}

class Command(BaseCommand):
    help = "Seed de catálogos estáticos (idempotente)."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        created_total = 0
        for model_name, values in DATA.items():
            self.stdout.write(self.style.WARNING(f"Sembrando: {model_name}"))
            creator = CREATE_FUNCS[model_name]
            for v in values:
                _, created = creator(v)
                created_total += 1 if created else 0
                self.stdout.write(f"  {v} {'(nuevo)' if created else ''}")
        self.stdout.write(self.style.SUCCESS(f"Seed catálogos completado. Nuevos: {created_total}"))
