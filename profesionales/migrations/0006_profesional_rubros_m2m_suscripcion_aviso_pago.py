from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0005_resena'),
    ]

    operations = [
        # 1. Agregar campo rubros (ManyToMany) temporal
        migrations.AddField(
            model_name='profesional',
            name='rubros',
            field=models.ManyToManyField(related_name='profesionales', to='profesionales.rubro', blank=True),
        ),
        # 2. Migración de datos: copiar rubro -> rubros (via RunPython)
        migrations.RunPython(
            code=lambda apps, schema_editor: [
                prof.rubros.add(prof.rubro_id)
                for prof in apps.get_model('profesionales', 'Profesional').objects.filter(rubro_id__isnull=False)
            ],
            reverse_code=migrations.RunPython.noop,
        ),
        # 3. Quitar campo rubro (ForeignKey)
        migrations.RemoveField(
            model_name='profesional',
            name='rubro',
        ),
        # 4. activo default False
        migrations.AlterField(
            model_name='profesional',
            name='activo',
            field=models.BooleanField(default=False),
        ),
        # 5. Modelo Suscripcion
        migrations.CreateModel(
            name='Suscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('1_rubro', '1 rubro - $7.500/mes'), ('2_rubros', '2 rubros - $10.000/mes'), ('mas_rubros', '3 o mas rubros - $15.000/mes')], max_length=20)),
                ('precio_mensual', models.PositiveIntegerField()),
                ('metodo_pago', models.CharField(choices=[('mercadopago', 'MercadoPago'), ('transferencia', 'Transferencia bancaria')], max_length=20)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente de pago'), ('activo', 'Activo'), ('cancelado', 'Cancelado'), ('suspendido', 'Suspendido')], default='pendiente', max_length=20)),
                ('mp_subscription_id', models.CharField(blank=True, max_length=200, null=True)),
                ('mp_payer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('email_contacto', models.EmailField(blank=True, max_length=254)),
                ('telefono_contacto', models.CharField(blank=True, max_length=20)),
                ('fecha_alta', models.DateTimeField(auto_now_add=True)),
                ('fecha_aprobacion', models.DateTimeField(blank=True, null=True)),
                ('notas_admin', models.TextField(blank=True)),
                ('profesional', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='suscripcion', to='profesionales.profesional')),
            ],
            options={'verbose_name': 'Suscripcion', 'verbose_name_plural': 'Suscripciones', 'ordering': ['-fecha_alta']},
        ),
        # 6. Campos de pago en Aviso
        migrations.AddField(
            model_name='aviso',
            name='nombre_contacto',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='aviso',
            name='email_contacto',
            field=models.EmailField(blank=True),
        ),
        migrations.AddField(
            model_name='aviso',
            name='semanas',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='aviso',
            name='precio_total',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='aviso',
            name='estado_pago',
            field=models.CharField(choices=[('pendiente', 'Pendiente de pago'), ('pagado', 'Pagado')], default='pendiente', max_length=20),
        ),
        migrations.AddField(
            model_name='aviso',
            name='mp_payment_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='aviso',
            name='mp_preference_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='aviso',
            name='creado',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='aviso',
            name='activo',
            field=models.BooleanField(default=False),
        ),
    ]
