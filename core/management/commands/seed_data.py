from django.core.management.base import BaseCommand
from core.models.models import (
    TipoEstructura, Material, ZonaInstalacion, Resistencia,
    EstadoFisico, Inclinacion, Propietario,
    ElementoElectrico, ElementoTelematico, Empresa, Proyecto, Zona, Sector
)

class Command(BaseCommand):
    help = "Carga datos iniciales en catálogos base (seeders)"

    def handle(self, *args, **kwargs):
        # Empresas de prueba
        emp, _ = Empresa.objects.get_or_create(nombre="Empresa Demo", ruc="12345678901", direccion="Av. Siempre Viva 123")

        # Proyecto demo
        proyecto, _ = Proyecto.objects.get_or_create(
            nombre="Proyecto Fibra Óptica Lima",
            empresa=emp,
            descripcion="Despliegue de fibra óptica en Lima Metropolitana",
            fecha_inicio="2025-01-01"
        )

        # Zonas y sectores demo
        zona, _ = Zona.objects.get_or_create(nombre="Zona Centro", proyecto=proyecto)
        Sector.objects.get_or_create(nombre="Sector 1", zona=zona)
        Sector.objects.get_or_create(nombre="Sector 2", zona=zona)

        # Catálogo de estructuras
        estructuras = ["Madera", "Concreto", "Metal"]
        for e in estructuras:
            TipoEstructura.objects.get_or_create(nombre=e)

        # Materiales
        materiales = ["H°A°", "Madera tratada", "Acero galvanizado"]
        for m in materiales:
            Material.objects.get_or_create(nombre=m)

        # Zona instalación
        for z in ["Vereda", "Jardín", "Calzada"]:
            ZonaInstalacion.objects.get_or_create(nombre=z)

        # Resistencia
        for r in ["ND", "OTRO", "100", "200"]:
            Resistencia.objects.get_or_create(valor=r)

        # Estado físico
        for e in ["Bueno", "Regular", "Malo"]:
            EstadoFisico.objects.get_or_create(descripcion=e)

        # Inclinación
        for i in ["Vertical", "Inclinado <5°", "Inclinado >5°"]:
            Inclinacion.objects.get_or_create(descripcion=i)

        # Propietarios
        for p in ["ENEL", "LUMSA", "MOVISTAR", "CLARO"]:
            Propietario.objects.get_or_create(siglas=p)

        # Elementos eléctricos
        for e in ["Transformador", "Corta circuito", "Aislador"]:
            ElementoElectrico.objects.get_or_create(nombre=e)

        # Elementos telemáticos
        for e in ["Caja terminal", "ONT", "Cable fibra óptica"]:
            ElementoTelematico.objects.get_or_create(nombre=e)

        self.stdout.write(self.style.SUCCESS("✅ Seeders ejecutados con éxito"))
