# Generated by Django 4.1.7 on 2023-03-08 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0011_remove_patientinfo_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='itemprice',
            field=models.IntegerField(default=0),
        ),
    ]
