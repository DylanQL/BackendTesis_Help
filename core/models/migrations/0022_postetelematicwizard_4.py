from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20251018_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='PosteTelematicWizard_4',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitud', models.DecimalField(decimal_places=8, max_digits=10, null=True)),
                ('longitud', models.DecimalField(decimal_places=8, max_digits=11, null=True)),
                ('observaciones', models.TextField(blank=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('wizard', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ubicacion', to='core.PosteTelematicWizard')),
            ],
            options={
                'verbose_name': 'Ubicación de Poste Telemático',
                'verbose_name_plural': 'Ubicaciones de Postes Telemáticos',
                'ordering': ['-actualizado_en'],
            },
        ),
        migrations.CreateModel(
            name='FotoTelematicWizard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='telematicos/fotos/')),
                ('descripcion', models.CharField(blank=True, max_length=100)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('is_principal', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('wizard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='core.PosteTelematicWizard_4')),
            ],
            options={
                'verbose_name': 'Foto de Poste Telemático',
                'verbose_name_plural': 'Fotos de Postes Telemáticos',
                'ordering': ['orden'],
            },
        ),
    ]