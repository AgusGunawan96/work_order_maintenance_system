# wo_maintenance_app/management/commands/generate_test_data.py
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate test data for WO Maintenance system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of test WO records to generate',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing test data first',
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clean = options['clean']
        
        if clean:
            self.clean_test_data()
        
        self.stdout.write(f"Generating {count} test WO records...")
        
        try:
            self.generate_test_wos(count)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully generated {count} test WO records")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to generate test data: {e}"))
    
    def clean_test_data(self):
        """Clean existing test data"""
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    DELETE FROM tabel_pengajuan 
                    WHERE history_id LIKE 'TEST%'
                """)
                
                deleted_count = cursor.rowcount
                self.stdout.write(f"Cleaned {deleted_count} test records")
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not clean test data: {e}"))
    
    def generate_test_wos(self, count):
        """Generate test WO records"""
        
        # Sample data
        test_users = ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005']
        test_descriptions = [
            'Bearing mesin rusak, perlu diganti',
            'Motor conveyor tidak jalan, cek kabel power',
            'Sensor posisi error, perlu kalibrasi',
            'Belt conveyor kendor, perlu tensioning',
            'Cylinder pneumatik bocor, ganti seal',
            'Panel control display blank, cek koneksi',
            'Emergency stop tidak berfungsi, perlu service',
            'Gear reducer bocor oli, ganti gasket',
            'Fan cooling tidak berputar, motor rusak',
            'Limit switch tidak respond, perlu ganti'
        ]
        
        try:
            # Get available machines and lines
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("SELECT id_mesin FROM tabel_mesin WHERE mesin IS NOT NULL")
                machines = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT id_line FROM tabel_line WHERE status = 'A'")
                lines = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT id_section FROM tabel_msection")
                sections = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT id_pekerjaan FROM tabel_pekerjaan")
                pekerjaans = [row[0] for row in cursor.fetchall()]
                
                if not all([machines, lines, sections, pekerjaans]):
                    raise Exception("Missing reference data (machines, lines, sections, or pekerjaans)")
                
                for i in range(count):
                    # Generate test data
                    history_id = f"TEST{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(3)}"
                    number_wo = f"TESTW{datetime.now().strftime('%y%m%d')}{str(i+1).zfill(3)}"
                    
                    # Random date within last 30 days
                    random_days = random.randint(0, 30)
                    test_date = datetime.now() - timedelta(days=random_days)
                    
                    # Random status (more pending for testing approval)
                    status_weights = ['0', '0', '0', '1', '2', '4']  # More pending
                    status = random.choice(status_weights)
                    
                    # Insert test record
                    cursor.execute("""
                        INSERT INTO tabel_pengajuan 
                        (history_id, tgl_his, jam_his, id_line, id_mesin, number_wo,
                         deskripsi_perbaikan, status, user_insert, tgl_insert, oleh,
                         approve, id_section, id_pekerjaan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        history_id,
                        test_date,
                        test_date.strftime('%H:%M:%S'),
                        random.choice(lines),
                        random.choice(machines),
                        number_wo,
                        random.choice(test_descriptions),
                        status,
                        random.choice(test_users),
                        test_date,
                        f"Test User {random.choice(test_users)}",
                        status if status != '0' else '0',
                        random.choice(sections),
                        random.choice(pekerjaans)
                    ])
                    
                    if (i + 1) % 10 == 0:
                        self.stdout.write(f"Generated {i + 1} records...")
                        
        except Exception as e:
            raise Exception(f"Failed to generate test data: {e}")