# Generated by Django 4.1.7 on 2023-03-02 22:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment', models.ManyToManyField(blank=True, related_name='appointment', to='hospital.availability')),
            ],
        ),
        migrations.CreateModel(
            name='PatientAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patientappoint', to='hospital.docappointment')),
            ],
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5)),
                ('skill', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('Doctor', 'Doctor'), ('Patient', 'Patient')], default='Patient', max_length=50),
        ),
        migrations.CreateModel(
            name='PatientInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointments', models.ManyToManyField(blank=True, related_name='appointments', to='hospital.patientappointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='customers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='patientappointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DoctorInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descr', models.TextField(max_length=250)),
                ('appointments', models.ManyToManyField(blank=True, related_name='patientappointments', to='hospital.patientappointment')),
                ('availables', models.ManyToManyField(blank=True, related_name='timeavailable', to='hospital.docappointment')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='healthcare', to=settings.AUTH_USER_MODEL)),
                ('non_available', models.ManyToManyField(blank=True, related_name='notavailable', to='hospital.availability')),
                ('skills', models.ManyToManyField(blank=True, related_name='workskills', to='hospital.skills')),
            ],
        ),
        migrations.AddField(
            model_name='docappointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='available', to=settings.AUTH_USER_MODEL),
        ),
    ]