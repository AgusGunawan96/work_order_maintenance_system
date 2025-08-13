# wo_maintenance_app/forms.py - FIXED VERSION
from django import forms
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class PengajuanMaintenanceForm(forms.Form):
    """Form untuk input pengajuan maintenance baru - FIXED"""
    
    line_section = forms.ChoiceField(
        label='Line/Section',
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'required': True
        }),
        help_text='Pilih line/section tempat mesin berada'
    )
    
    nama_mesin = forms.CharField(
        label='Nama Mesin',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'required': True
        }),
        help_text='Pilih mesin yang akan di-maintenance'
    )
    
    section_tujuan = forms.ChoiceField(
        label='Section Tujuan',
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'required': True
        }),
        help_text='Pilih section yang akan menangani maintenance'
    )
    
    jenis_pekerjaan = forms.ChoiceField(
        label='Jenis Pekerjaan',
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'required': True
        }),
        help_text='Pilih jenis pekerjaan maintenance'
    )
    
    deskripsi_pekerjaan = forms.CharField(
        label='Deskripsi Pekerjaan',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': True,
            'placeholder': 'Jelaskan detail pekerjaan maintenance yang diperlukan (minimal 10 karakter)...'
        }),
        help_text='Uraikan dengan detail pekerjaan maintenance yang diperlukan'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        employee_data = kwargs.pop('employee_data', None)
        super().__init__(*args, **kwargs)
        
        # Load choices dari database
        self.load_line_choices()
        self.load_section_choices()
        self.load_pekerjaan_choices()
        
        # nama_mesin menggunakan CharField, akan diisi via AJAX
        # Set placeholder untuk dropdown kosong
        self.fields['nama_mesin'].widget.attrs.update({
            'data-placeholder': 'Pilih Line terlebih dahulu'
        })
    
    def load_line_choices(self):
        """Load pilihan line dari database - FIXED untuk menghindari duplikasi"""
        try:
            choices = [('', 'Pilih Line/Section')]
            seen_ids = set()  # Track ID yang sudah ditambahkan
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_line, line 
                    FROM tabel_line 
                    WHERE status = 'A' AND line IS NOT NULL
                    ORDER BY id_line, line
                """)
                
                for row in cursor.fetchall():
                    # Konversi ID ke integer untuk konsistensi
                    line_id = int(float(row[0]))  # Handle float to int conversion
                    line_name = str(row[1]).strip()
                    
                    # Skip jika ID sudah ada (menghindari duplikasi)
                    if line_id not in seen_ids and line_name:
                        choices.append((str(line_id), line_name))
                        seen_ids.add(line_id)
            
            self.fields['line_section'].choices = choices
            logger.debug(f"Loaded {len(choices)-1} unique line choices")
            
        except Exception as e:
            logger.error(f"Error loading line choices: {e}")
            self.fields['line_section'].choices = [('', 'Error loading line data')]
    
    def load_section_choices(self):
        """Load pilihan section tujuan dari database"""
        try:
            choices = [('', 'Pilih Section Tujuan')]
            seen_ids = set()
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) AND seksi IS NOT NULL
                    ORDER BY id_section, seksi
                """)
                
                for row in cursor.fetchall():
                    section_id = int(float(row[0]))
                    section_name = str(row[1]).strip()
                    
                    if section_id not in seen_ids and section_name:
                        choices.append((str(section_id), section_name))
                        seen_ids.add(section_id)
            
            self.fields['section_tujuan'].choices = choices
            logger.debug(f"Loaded {len(choices)-1} unique section choices")
            
        except Exception as e:
            logger.error(f"Error loading section choices: {e}")
            self.fields['section_tujuan'].choices = [('', 'Error loading section data')]
    
    def load_pekerjaan_choices(self):
        """Load pilihan jenis pekerjaan dari database"""
        try:
            choices = [('', 'Pilih Jenis Pekerjaan')]
            seen_ids = set()
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_pekerjaan, pekerjaan 
                    FROM tabel_pekerjaan 
                    WHERE (status = 'A' OR status IS NULL) AND pekerjaan IS NOT NULL
                    ORDER BY id_pekerjaan, pekerjaan
                """)
                
                for row in cursor.fetchall():
                    pekerjaan_id = int(float(row[0]))
                    pekerjaan_name = str(row[1]).strip()
                    
                    if pekerjaan_id not in seen_ids and pekerjaan_name:
                        choices.append((str(pekerjaan_id), pekerjaan_name))
                        seen_ids.add(pekerjaan_id)
            
            self.fields['jenis_pekerjaan'].choices = choices
            logger.debug(f"Loaded {len(choices)-1} unique pekerjaan choices")
            
        except Exception as e:
            logger.error(f"Error loading pekerjaan choices: {e}")
            self.fields['jenis_pekerjaan'].choices = [('', 'Error loading pekerjaan data')]
    
    def clean_nama_mesin(self):
        """Custom validation untuk nama_mesin - DYNAMIC VALIDATION"""
        nama_mesin = self.cleaned_data.get('nama_mesin')
        line_section = self.cleaned_data.get('line_section')
        
        logger.debug(f"Validating mesin: {nama_mesin} for line: {line_section}")
        
        if not nama_mesin:
            raise forms.ValidationError('Pilih mesin yang valid')
        
        if not line_section:
            raise forms.ValidationError('Pilih line/section terlebih dahulu')
        
        # Validasi bahwa input adalah integer
        try:
            mesin_id_int = int(nama_mesin)
            line_id_int = int(line_section)
        except ValueError:
            logger.error(f"Invalid ID format - mesin: {nama_mesin}, line: {line_section}")
            raise forms.ValidationError(f'ID tidak valid: mesin={nama_mesin}, line={line_section}')
        
        # DYNAMIC VALIDATION: Query database langsung
        try:
            with connections['DB_Maintenance'].cursor() as cursor:
                # Cek apakah mesin dengan ID ini ada dan sesuai dengan line
                cursor.execute("""
                    SELECT tm.id_mesin, tm.mesin, tl.line 
                    FROM tabel_mesin tm
                    INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                    WHERE tm.id_mesin = %s 
                        AND CAST(tl.id_line AS int) = %s
                        AND tm.mesin IS NOT NULL 
                        AND tm.mesin != ''
                        AND (tm.status IS NULL OR tm.status != '0')
                        AND tl.status = 'A'
                """, [mesin_id_int, line_id_int])
                
                result = cursor.fetchone()
                
                logger.debug(f"Validation query result: {result}")
                
                if not result:
                    # Log untuk debugging
                    logger.error(f"VALIDATION FAILED: Mesin {mesin_id_int} tidak ditemukan untuk line {line_id_int}")
                    
                    # Cek apa yang ada di database untuk debugging
                    cursor.execute("""
                        SELECT COUNT(*) as total,
                               STRING_AGG(CAST(tm.id_mesin AS varchar), ', ') as mesin_ids
                        FROM tabel_mesin tm
                        INNER JOIN tabel_line tl ON CAST(tl.id_line AS varchar(10)) = tm.id_line
                        WHERE CAST(tl.id_line AS int) = %s
                            AND tm.mesin IS NOT NULL 
                            AND (tm.status IS NULL OR tm.status != '0')
                            AND tl.status = 'A'
                    """, [line_id_int])
                    
                    debug_result = cursor.fetchone()
                    available_mesins = debug_result[1] if debug_result[1] else "none"
                    
                    logger.error(f"Available mesins for line {line_id_int}: {available_mesins}")
                    
                    raise forms.ValidationError(
                        f'Mesin dengan ID {mesin_id_int} tidak valid untuk line {line_id_int}. '
                        f'Mesin yang tersedia: {available_mesins}'
                    )
                
                logger.info(f"Validation SUCCESS: {result[1]} (ID: {result[0]}) di {result[2]}")
                return str(mesin_id_int)  # Return validated ID
                
        except Exception as e:
            logger.error(f"Error validating mesin: {e}")
            raise forms.ValidationError('Error validasi mesin - hubungi administrator')
    
    
    def clean_deskripsi_pekerjaan(self):
        """Validasi deskripsi pekerjaan"""
        deskripsi = self.cleaned_data.get('deskripsi_pekerjaan', '')
        if len(deskripsi.strip()) < 10:
            raise forms.ValidationError('Deskripsi pekerjaan minimal 10 karakter')
        return deskripsi.strip()


class PengajuanFilterForm(forms.Form):
    """Form untuk filter daftar pengajuan"""
    
    STATUS_CHOICES = [
        ('', 'Semua Status'),
        ('0', 'Pending'),
        ('1', 'Approved'),
        ('2', 'Rejected'),
        ('3', 'In Progress'),
        ('4', 'Completed'),
    ]
    
    tanggal_dari = forms.DateField(
        label='Tanggal Dari',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    tanggal_sampai = forms.DateField(
        label='Tanggal Sampai',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        label='Status',
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    nama_mesin = forms.CharField(
        label='Nama Mesin',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari nama mesin...'
        })
    )
    
    pengaju = forms.CharField(
        label='Pengaju',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari nama pengaju...'
        })
    )
    
    history_id = forms.CharField(
        label='History ID',
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari History ID...'
        })
    )


class ApprovalForm(forms.Form):
    """Form untuk approval pengajuan"""
    
    ACTION_CHOICES = [
        ('1', 'Approve'),
        ('2', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        label='Aksi',
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    keterangan = forms.CharField(
        label='Keterangan',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Opsional: Tambahkan keterangan untuk keputusan approval...'
        }),
        help_text='Keterangan opsional untuk keputusan approval'
    )

class ReviewFilterForm(forms.Form):
    """Form untuk filter review pengajuan - ENHANCED"""
    
    REVIEW_STATUS_CHOICES = [
        ('', 'Semua Status Review'),
        ('0', 'Pending Review'),
        ('1', 'Reviewed (Processed)'),
        ('2', 'Reviewed (Rejected)'),
    ]
    
    tanggal_dari = forms.DateField(
        label='Tanggal Dari',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    tanggal_sampai = forms.DateField(
        label='Tanggal Sampai',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    review_status = forms.ChoiceField(
        label='Status Review',
        choices=REVIEW_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    section_filter = forms.ChoiceField(
        label='Section Filter',
        choices=[
            ('', 'Semua Section'),
            ('it', '💻 IT'),
            ('elektrik', '⚡ Elektrik'),
            ('utility', '🏭 Utility'),
            ('mekanik', '🔧 Mekanik'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load additional sections from database if needed
        self.load_additional_section_choices()


# wo_maintenance_app/forms.py - ADD/UPDATE ReviewForm

class ReviewForm(forms.Form):
    """Form untuk review pengajuan oleh SITI FATIMAH - ENHANCED dengan Reject dan Process"""
    
    ACTION_CHOICES = [
        ('process', 'Process Pengajuan'),
        ('reject', 'Reject'),
    ]
    
    SECTION_CHOICES = [
        ('', '-- Pilih Section (Opsional) --'),
        ('it', '💻 IT'),
        ('elektrik', '⚡ Elektrik'),
        ('utility', '🏭 Utility'),
        ('mekanik', '🔧 Mekanik'),
    ]
    
    action = forms.ChoiceField(
        label='Keputusan Review',
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input review-action'
        }),
        help_text='Pilih "Process Pengajuan" untuk melanjutkan atau "Reject" untuk menolak'
    )
    
    target_section = forms.ChoiceField(
        label='Tujuan Section (Opsional)',
        choices=SECTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-section',
            'data-placeholder': 'Pilih section tujuan (opsional)...'
        }),
        help_text='🎯 Opsional: Tentukan section spesifik yang akan menangani pengajuan ini'
    )
    
    review_notes = forms.CharField(
        label='Catatan Review',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Opsional: Tambahkan catatan untuk keputusan review dan instruksi khusus...'
        }),
        help_text='Catatan opsional untuk dokumentasi dan instruksi'
    )
    
    priority_level = forms.ChoiceField(
        label='Tingkat Prioritas',
        choices=[
            ('normal', 'Normal'),
            ('urgent', 'Urgent'),
            ('critical', 'Critical')
        ],
        initial='normal',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Tentukan tingkat prioritas pengajuan ini'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load section choices dari database untuk mapping
        self.load_section_mapping()
    
    def load_section_mapping(self):
        """Load mapping section dari database untuk referensi"""
        try:
            self.section_mapping = {}
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) 
                        AND seksi IS NOT NULL
                        AND seksi != ''
                    ORDER BY seksi
                """)
                
                for row in cursor.fetchall():
                    section_id = int(float(row[0]))
                    section_name = str(row[1]).strip().upper()
                    
                    # Map section berdasarkan kata kunci
                    if any(keyword in section_name for keyword in ['IT', 'INFORMATION', 'SYSTEM', 'TEKNOLOGI']):
                        if 'it' not in self.section_mapping:
                            self.section_mapping['it'] = section_id
                    elif any(keyword in section_name for keyword in ['ELEKTRIK', 'ELECTRIC', 'LISTRIK']):
                        if 'elektrik' not in self.section_mapping:
                            self.section_mapping['elektrik'] = section_id
                    elif any(keyword in section_name for keyword in ['UTILITY', 'UTILITIES', 'UMUM']):
                        if 'utility' not in self.section_mapping:
                            self.section_mapping['utility'] = section_id
                    elif any(keyword in section_name for keyword in ['MEKANIK', 'MECHANIC', 'MECHANICAL']):
                        if 'mekanik' not in self.section_mapping:
                            self.section_mapping['mekanik'] = section_id
            
            logger.info(f"Section mapping loaded: {self.section_mapping}")
            
        except Exception as e:
            logger.error(f"Error loading section mapping: {e}")
            # Default mapping sebagai fallback
            self.section_mapping = {
                'it': 1,
                'elektrik': 2,
                'mekanik': 3,
                'utility': 4
            }
    
    def get_final_section_id(self):
        """Get final section ID berdasarkan pilihan target_section"""
        target_section = self.cleaned_data.get('target_section')
        
        if target_section and hasattr(self, 'section_mapping'):
            return self.section_mapping.get(target_section)
        
        return None
    
    def clean(self):
        """Custom validation untuk review form"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        target_section = cleaned_data.get('target_section')
        review_notes = cleaned_data.get('review_notes')
        
        # Validasi berdasarkan action
        if action == 'process':
            # Untuk process, section adalah opsional
            if not review_notes:
                cleaned_data['review_notes'] = 'Pengajuan diproses untuk ditindaklanjuti'
        
        elif action == 'reject':
            # Untuk reject, notes direkomendasikan
            if not review_notes:
                cleaned_data['review_notes'] = 'Pengajuan ditolak oleh reviewer'
            
            # Clear target section jika reject
            cleaned_data['target_section'] = ''
        
        return cleaned_data