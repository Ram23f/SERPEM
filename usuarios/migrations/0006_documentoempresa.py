# Generated by Django 5.1.7 on 2025-04-22 17:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_servicio'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('rfc', 'RFC / SAT'), ('domicilio', 'Comprobante de domicilio'), ('acta', 'Acta constitutiva'), ('licencia', 'Licencia / Permiso'), ('otro', 'Otro')], max_length=50)),
                ('archivo', models.FileField(upload_to='documentos_empresas/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('observaciones', models.TextField(blank=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='usuarios.empresa')),
            ],
        ),
    ]
