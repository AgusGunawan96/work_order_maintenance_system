# File: dailyactivity_app/migrations/0002_add_mechanical_fields.py
# Buat file ini secara manual

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dailyactivity_app', '0001_initial'),  # Ganti dengan migration terakhir yang berhasil
    ]

    operations = [
        # Cek apakah kolom sudah ada sebelum menambahkan
        migrations.RunSQL(
            """
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'dailyactivity_app_mechanical_data' 
                AND COLUMN_NAME = 'tindakan_perbaikan'
            )
            BEGIN
                ALTER TABLE dailyactivity_app_mechanical_data 
                ADD tindakan_perbaikan NVARCHAR(MAX) NULL;
            END
            """,
            reverse_sql="""
            IF EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'dailyactivity_app_mechanical_data' 
                AND COLUMN_NAME = 'tindakan_perbaikan'
            )
            BEGIN
                ALTER TABLE dailyactivity_app_mechanical_data 
                DROP COLUMN tindakan_perbaikan;
            END
            """
        ),
        
        migrations.RunSQL(
            """
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'dailyactivity_app_mechanical_data' 
                AND COLUMN_NAME = 'tindakan_pencegahan'
            )
            BEGIN
                ALTER TABLE dailyactivity_app_mechanical_data 
                ADD tindakan_pencegahan NVARCHAR(MAX) NULL;
            END
            """,
            reverse_sql="""
            IF EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'dailyactivity_app_mechanical_data' 
                AND COLUMN_NAME = 'tindakan_pencegahan'
            )
            BEGIN
                ALTER TABLE dailyactivity_app_mechanical_data 
                DROP COLUMN tindakan_pencegahan;
            END
            """
        ),
    ]