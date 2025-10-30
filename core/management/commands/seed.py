from django.core.management.base import BaseCommand
from core.models.models import Empresa, Proyecto, Zona, Sector
from datetime import date

class Command(BaseCommand):
    help = "Cargar datos iniciales de prueba"

    def handle(self, *args, **kwargs):
        empresa, _ = Empresa.objects.get_or_create(
            nombre="Empresa Demo",
            defaults={"ruc": "20123456789", "direccion": "Av. Principal 123"}
        )
        proyecto, _ = Proyecto.objects.get_or_create(
            nombre="Proyecto Demo",
            empresa=empresa,
            defaults={"descripcion": "Proyecto inicial", "fecha_inicio": date.today()}
        )
        zona, _ = Zona.objects.get_or_create(
            id=2, nombre="Zona A", proyecto=proyecto
        )
        sector, _ = Sector.objects.get_or_create(
            id=3, nombre="Sector Z3S804", zona=zona
        )
        self.stdout.write(self.style.SUCCESS("Seeders cargados correctamente"))
