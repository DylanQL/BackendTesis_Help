# core/management/commands/seed_ubicaciones.py
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import Distrito, Zona, Sector, Empresa, Proyecto  # ← agrega Proyecto

DIST_DATA = [
    {
        "nombre": "Huamalíes",
        "zonas": {"Zona A": ["Sector 1", "Sector 2", "Sector 3"], "Zona B": ["Sector 1", "Sector 2"]},
    },
    {
        "nombre": "Huánuco",
        "zonas": {"Zona Centro": ["Sector 1", "Sector 2"], "Zona Norte": ["Sector 1"]},
    },
    {
        "nombre": "Amarilis",
        "zonas": {"Zona Este": ["Sector 1", "Sector 2", "Sector 3", "Sector 4"]},
    },
]

class Command(BaseCommand):
    help = "Seed de ubicaciones: Distrito -> Zonas -> Sectores (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--empresa", type=str, default=None,
                            help="Nombre de Empresa para asociar distritos (opcional).")

    @transaction.atomic
    def handle(self, *args, **opts):
        empresa_name = opts.get("empresa")
        empresa = None
        if empresa_name:
            empresa, _ = Empresa.objects.get_or_create(nombre=empresa_name)

        # 🔧 Proyecto temporal para cumplir NOT NULL en Zona.proyecto
        proyecto_temp, _ = Proyecto.objects.get_or_create(
            nombre="PROYECTO_TEMP_SEED",
            defaults={
                "descripcion": "Temporal para seed de Zonas",
                "empresa": empresa or Empresa.objects.get_or_create(nombre="EMPRESA_TEMP")[0],
                "fecha_inicio": "2025-01-01",
                "activo": True,
            },
        )

        total_d = total_z = total_s = 0
        for d in DIST_DATA:
            distrito, created_d = Distrito.objects.get_or_create(
                nombre=d["nombre"],
                defaults={"empresa": empresa, "activo": True}
            )
            if empresa and distrito.empresa_id != empresa.id:
                distrito.empresa = empresa
                distrito.save(update_fields=["empresa"])
            total_d += 1 if created_d else 0
            self.stdout.write(self.style.SUCCESS(f"Distrito: {distrito.nombre} (id={distrito.id})"))

            for zona_nombre, sectores in d["zonas"].items():
                # ✅ Siempre pasamos un proyecto válido
                zona, created_z = Zona.objects.get_or_create(
                    nombre=zona_nombre,
                    distrito=distrito,
                    defaults={"proyecto": proyecto_temp},
                )
                # Si ya existía sin proyecto, lo saneamos
                if not zona.proyecto_id:
                    zona.proyecto = proyecto_temp
                    zona.save(update_fields=["proyecto"])
                total_z += 1 if created_z else 0
                self.stdout.write(f"  Zona: {zona.nombre} (id={zona.id})")

                for sector_nombre in sectores:
                    sector, created_s = Sector.objects.get_or_create(
                        nombre=sector_nombre,
                        zona=zona
                    )
                    total_s += 1 if created_s else 0
                    self.stdout.write(f"    Sector: {sector.nombre} (id={sector.id})")

        self.stdout.write(self.style.SUCCESS(
            f"Seed completado. Nuevos -> Distritos: {total_d}, Zonas: {total_z}, Sectores: {total_s}"
        ))
