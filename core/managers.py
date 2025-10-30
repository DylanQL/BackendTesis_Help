from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, dni=None, email=None, password=None, **extra_fields):
        username_field = self.model.USERNAME_FIELD
        if not dni and username_field != 'dni':
            raise ValueError(f'El campo {username_field} es obligatorio')
        # Normalizar email si existe
        if email:
            email = self.normalize_email(email)
            extra_fields['email'] = email
        # Si no se proporciona rol explícitamente, asumimos 'encargado' por defecto
        # para evitar crear usuarios sin un rol válido (campo requerido en el modelo).
        extra_fields.setdefault('rol', 'encargado')
        extra_fields[username_field] = dni
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, dni=None, email=None, password=None, **extra_fields):
        # Asegurar banderas administrativas
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        # Forzar rol de superusuario para que no quede en el valor por defecto
        # (evita casos donde se crea un superuser sin rol y termina como 'encargado').
        extra_fields.setdefault('rol', 'superadmin')
        return self.create_user(dni=dni, email=email, password=password, **extra_fields)