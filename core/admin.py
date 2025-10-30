from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.models import (
    Empresa, CustomUser, Proyecto, Zona, Sector, Reporte,
    DetallePosteElectrico, FotoReporte,
    TipoEstructura, Material, ZonaInstalacion, Resistencia,
    EstadoFisico, Inclinacion, Propietario,
    ElementoElectrico, ElementoTelematico
)
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Usuario
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'id', 'dni', 'nombres', 'apellidos', 'email', 'celular',
        'rol', 'empresa', 'supervisor', 'estado_contrasena', 'estado', 'date_joined', 'is_active'
    )
    list_filter = ('rol', 'empresa', 'is_active', 'estado', 'estado_contrasena')
    search_fields = ('dni', 'email', 'nombres', 'apellidos', 'celular')
    ordering = ('dni',)

    fieldsets = (
        (None, {'fields': ('dni', 'email', 'password')}),
        ('Información personal', {'fields': (
            'nombres', 'apellidos', 'celular', 'rol', 'empresa', 'supervisor'
        )}),
        ('Estado', {'fields': ('estado_contrasena', 'estado', 'date_joined')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'dni', 'email', 'nombres', 'apellidos', 'celular', 'rol', 'empresa', 'supervisor',
                'estado_contrasena', 'estado', 'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.rol == 'superadmin':
            return qs
        return qs.filter(empresa=request.user.empresa)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "empresa":
            # Si es superadmin, ve todas las empresas
            if hasattr(request.user, 'rol') and request.user.rol == 'superadmin':
                kwargs["queryset"] = Empresa.objects.all()
            # Si el usuario tiene empresa, solo esa
            elif hasattr(request.user, 'empresa') and request.user.empresa:
                kwargs["queryset"] = Empresa.objects.filter(id=request.user.empresa_id)
            # Si no tiene empresa (caso raro), muestra todas
            else:
                kwargs["queryset"] = Empresa.objects.all()
        if db_field.name == "supervisor":
            # Si el usuario tiene empresa, filtra por esa empresa
            if hasattr(request.user, 'empresa') and request.user.empresa:
                kwargs["queryset"] = CustomUser.objects.filter(rol='supervisor', empresa=request.user.empresa)
            else:
                kwargs["queryset"] = CustomUser.objects.filter(rol='supervisor')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Admins por modelo con filtro por empresa
class BaseEmpresaAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.rol == 'superadmin':
            return qs
        return qs.filter(empresa=request.user.empresa)

class ProyectoAdmin(BaseEmpresaAdmin):
    list_display = ('nombre', 'empresa', 'activo')

class ZonaAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.rol == 'superadmin':
            return qs
        return qs.filter(proyecto__empresa=request.user.empresa)

class SectorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.rol == 'superadmin':
            return qs
        return qs.filter(zona__proyecto__empresa=request.user.empresa)

class ReporteAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.rol == 'superadmin':
            return qs
        return qs.filter(proyecto__empresa=request.user.empresa)

class DetallePosteElectricoAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'codigo', 'tension', 'altura', 'propietario')

class FotoReporteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'tipo', 'latitud', 'longitud')

# Registro
admin.site.register(Empresa)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Zona, ZonaAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Reporte, ReporteAdmin)
admin.site.register(DetallePosteElectrico, DetallePosteElectricoAdmin)
admin.site.register(FotoReporte, FotoReporteAdmin)

# Catálogos dinámicos
admin.site.register(TipoEstructura)
admin.site.register(Material)
admin.site.register(ZonaInstalacion)
admin.site.register(Resistencia)
admin.site.register(EstadoFisico)
admin.site.register(Inclinacion)
admin.site.register(Propietario)
admin.site.register(ElementoElectrico)
admin.site.register(ElementoTelematico)
