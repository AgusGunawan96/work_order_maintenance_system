# dailyactivity_app/migrations/0002_add_maintenance_fields.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dailyactivity_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='laporandata',
            name='nomor_wo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Nomor WO'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='status_utility',
            field=models.CharField(choices=[('proses', 'Proses'), ('selesai', 'Selesai'), ('hold', 'Hold')], default='proses', max_length=20, verbose_name='Status Utility'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='lokasi',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Lokasi'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='mesin',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Mesin'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='nomor_mesin',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Nomor Mesin'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='jenis_pekerjaan_maintenance',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Jenis Pekerjaan Maintenance'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='penyebab',
            field=models.TextField(blank=True, null=True, verbose_name='Penyebab'),
        ),
        migrations.AddField(
            model_name='laporandata',
            name='tindakan_perbaikan',
            field=models.TextField(blank=True, null=True, verbose_name='Tindakan Perbaikan'),
        ),
    ]