from django.core.management.base import BaseCommand
from core.models.models import ElementoElectrico  # ajusta import

ELECTRICOS = {
    "Medidor eléctrico",
    "Recloser con secciones",
    "Fuente de poder",
    "Sifón Eléctrico",
    "Bajada de Sifon",
}
TELEMATICOS = {
    "Caja NAP",
    "Caja de conexión eléctrica",
    "Brazo extensor",
    "Cable DPI",
    "Cajas terminal telefónica",
}

class Command(BaseCommand):
    help = "Corrige tipos y pobla elementos eléctricos/telemáticos"

    def handle(self, *args, **options):
        # 1) Corregir tipo en filas existentes por nombre
        corregidos = 0
        for e in ElementoElectrico.objects.all():
            nuevo_tipo = None
            if e.nombre in ELECTRICOS:
                nuevo_tipo = "electrico"
            elif e.nombre in TELEMATICOS:
                nuevo_tipo = "telematico"
            if nuevo_tipo and e.tipo != nuevo_tipo:
                e.tipo = nuevo_tipo
                e.save(update_fields=["tipo"])
                corregidos += 1

        # 2) Insertar faltantes (idempotente)
        creados = 0
        for nombre in sorted(ELECTRICOS):
            _, created = ElementoElectrico.objects.get_or_create(
                nombre=nombre, defaults={"tipo": "electrico"}
            )
            creados += int(created)

        for nombre in sorted(TELEMATICOS):
            _, created = ElementoElectrico.objects.get_or_create(
                nombre=nombre, defaults={"tipo": "telematico"}
            )
            creados += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Seed OK. Corregidos: {corregidos}, Creados: {creados}"
        ))
