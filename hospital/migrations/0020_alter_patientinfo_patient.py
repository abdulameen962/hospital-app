# Generated by Django 3.2.6 on 2023-03-12 17:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0019_rename_profile_change_user_is_profile_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientinfo',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='customers', to=settings.AUTH_USER_MODEL),
        ),
    ]
