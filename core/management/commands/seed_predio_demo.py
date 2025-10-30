from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.models import (
    Empresa, CustomUser, Proyecto, Zona, Sector,
    Reporte, FotoReporte
)

class Command(BaseCommand):
    help = "Carga datos de prueba para Reporte Predio con imágenes demo"

    def handle(self, *args, **kwargs):
        # 1. Empresa
        empresa, _ = Empresa.objects.get_or_create(
            nombre="DemoCorp",
            defaults={"ruc": "12345678901", "direccion": "Av. Demo 123"}
        )

        # 2. Supervisor
        supervisor, _ = CustomUser.objects.get_or_create(
            dni="11111111",
            defaults={
                "email": "supervisor@demo.com",
                "nombres": "Juan",
                "apellidos": "Supervisor",
                "rol": "supervisor",
                "empresa": empresa,
                "is_active": True
            }
        )

        # 3. Encargado
        encargado, _ = CustomUser.objects.get_or_create(
            dni="22222222",
            defaults={
                "email": "encargado@demo.com",
                "nombres": "Pedro",
                "apellidos": "Encargado",
                "rol": "encargado",
                "empresa": empresa,
                "supervisor": supervisor,
                "is_active": True
            }
        )

        # 4. Proyecto, Zona y Sector
        proyecto, _ = Proyecto.objects.get_or_create(
            nombre="Proyecto Demo",
            empresa=empresa,
            defaults={"descripcion": "Proyecto inicial", "fecha_inicio": timezone.now()}
        )

        zona, _ = Zona.objects.get_or_create(nombre="Zona A", proyecto=proyecto)
        sector, _ = Sector.objects.get_or_create(nombre="Z38504", zona=zona)

        # 5. Reporte
        reporte, _ = Reporte.objects.get_or_create(
            encargado=encargado,
            proyecto=proyecto,
            zona=zona,
            sector=sector,
            defaults={
                "tipo": "electrico",
                "observaciones": "Observación de prueba",
                "latitud": -11.07869414488,
                "longitud": -75.328717213143,
                "estado": "pendiente",
            }
        )

        # 6. Fotos (usar solo rutas relativas a /media/seed_images/)
        fotos = ["img1.jpg", "img2.png", "img3.jpg"]
        for idx, fname in enumerate(fotos, start=1):
            FotoReporte.objects.get_or_create(
                reporte=reporte,
                tipo=f"fachada_{idx}",
                defaults={
                    "imagen": f"seed_images/{fname}",  # Solo guardamos la ruta
                    "latitud": -11.0785374,
                    "longitud": -75.3288026,
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Seed de Reporte Predio demo creado."))
