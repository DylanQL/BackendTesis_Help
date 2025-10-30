from django.core.management.base import BaseCommand
from django.conf import settings
from core.models.models import CustomUser, Empresa


class Command(BaseCommand):
    help = 'Seed default users: one user per role defined in CustomUser.ROLES'

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, help='Password to set for all seeded users', default='password123')
        parser.add_argument('--empresa', type=str, help='Name of empresa to create/use', default='Empresa Demo')
        parser.add_argument('--force', action='store_true', help='If set, overwrite password even if user exists')

    def handle(self, *args, **options):
        password = options['password']
        empresa_name = options['empresa']

        empresa, created = Empresa.objects.get_or_create(nombre=empresa_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created empresa: {empresa.nombre}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing empresa: {empresa.nombre}'))

        roles = [r[0] for r in CustomUser.ROLES]
        created_users = []
        for idx, role in enumerate(roles, start=1):
            dni = f'9999999{idx}'
            email = f'{role}@example.com'
            nombres = role.capitalize()
            apellidos = 'Seed'
            # determine default flags
            is_staff_flag = True if role in ['superadmin', 'admin'] else False
            is_superuser_flag = True if role == 'superadmin' else False

            user, user_created = CustomUser.objects.get_or_create(
                dni=dni,
                defaults={
                    'email': email,
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'rol': role,
                    'empresa': empresa,
                    'is_staff': is_staff_flag,
                    'is_superuser': is_superuser_flag,
                }
            )

            if user_created:
                user.set_password(password)
                user.save()
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user {email} with role {role} (dni={dni})'))
            else:
                # User exists: optionally overwrite password and ensure superuser flag for superadmin
                changed = False
                if role == 'superadmin' and not user.is_superuser:
                    user.is_superuser = True
                    changed = True
                if options.get('force'):
                    user.set_password(password)
                    changed = True
                if changed:
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated existing user for role {role}: {user.email}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User for role {role} already exists and was not changed: {user.email}'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
