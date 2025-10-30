from django.core.management.base import BaseCommand
from core.models.models import ParametroCatalogo

DATA = {
    'estructura': ['Simple', 'Doble', 'Triple'],
    'material': ['Concreto', 'Madera', 'Metal', 'Fibra'],
    'zona_instalacion': ['Tierra', 'Jardin', 'Rocoso', 'Vereda'],
    'resistencia': ['100', '200', '250', '300', '400', '500', 'ND'],
}

class Command(BaseCommand):
    help = 'Seed de parámetros de poste (estructura, material, zona_instalacion, resistencia).'

    def handle(self, *args, **options):
        creados = 0
        for categoria, valores in DATA.items():
            for idx, nombre in enumerate(valores, start=1):
                _, was_created = ParametroCatalogo.objects.get_or_create(
                    categoria=categoria,
                    nombre=nombre,
                    defaults={'orden': idx, 'activo': True},
                )
                creados += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Seed OK. Nuevos: {creados}'))
