from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profesionales', '0006_profesional_rubros_m2m_suscripcion_aviso_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='suscripcion',
            name='mp_preference_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='suscripcion',
            name='mp_payment_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
