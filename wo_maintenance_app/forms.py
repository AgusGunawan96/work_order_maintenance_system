# wo_maintenance_app/forms.py - FIXED VERSION dengan Status A & Approve Y
from django import forms
from django.db import connections
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# ===== FIXED STATUS CONSTANTS =====
STATUS_PENDING = '0'      # Pending
STATUS_APPROVED = 'A'     # FIXED: Approved menggunakan 'A' bukan '1'
STATUS_REJECTED = '2'     # Rejected
STATUS_IN_PROGRESS = '3'  # In Progress
STATUS_COMPLETED = '4'    # Completed

APPROVE_NO = '0'          # Not Approved
APPROVE_YES = 'Y'         # FIXED: Approved menggunakan 'Y' bukan '1'
APPROVE_REJECTED = '2'    # Rejected

# wo_maintenance_app/forms.py - Tambahkan form ini buat filter tabel_main

class TabelMainFilterForm(forms.Form):
    """
    Form buat filter data di tabel_main khusus buat SITI FATIMAH
    Pake bahasa gaul dong biar asik!
    """
    
    # Filter tanggal
    tanggal_dari = forms.DateField(
        label='Tanggal Dari',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Pilih tanggal mulai'
        }),
        help_text='Tanggal awal pengajuan'
    )
    
    tanggal_sampai = forms.DateField(
        label='Tanggal Sampai', 
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Pilih tanggal akhir'
        }),
        help_text='Tanggal akhir pengajuan'
    )
    
    # Filter status
    STATUS_CHOICES = [
        ('', 'Semua Status'),
        ('0', '⏳ Pending'),
        ('1', '✅ Approved'),
        ('2', '❌ Rejected'),
        ('3', '🚀 In Progress'),
        ('4', '✅ Completed'),
        ('5', '⚠️ On Hold'),
    ]
    
    status = forms.ChoiceField(
        label='Status',
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Filter status pekerjaan
    STATUS_PEKERJAAN_CHOICES = [
        ('', 'Semua Status Pekerjaan'),
        ('0', '⏳ Belum Mulai'),
        ('1', '🚀 Sedang Dikerjakan'),
        ('2', '✅ Selesai'),
        ('3', '⚠️ Tertunda'),
        ('4', '❌ Dibatalkan'),
    ]
    
    status_pekerjaan = forms.ChoiceField(
        label='Status Pekerjaan',
        choices=STATUS_PEKERJAAN_CHOICES, 
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Filter line/section
    line_filter = forms.ChoiceField(
        label='Filter Line',
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    section_filter = forms.ChoiceField(
        label='Filter Section',
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Filter PIC
    pic_filter = forms.CharField(
        label='Filter PIC',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari berdasarkan PIC...'
        }),
        help_text='PIC Produksi atau Maintenance'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load choices dari database
        self.load_dynamic_choices()
    
    def load_dynamic_choices(self):
        """Load pilihan dinamis dari database - asik kan otomatis!"""
        try:
            from django.db import connections
            
            with connections['DB_Maintenance'].cursor() as cursor:
                # Load line choices
                cursor.execute("""
                    SELECT DISTINCT tm.id_line, tl.line
                    FROM tabel_main tm
                    LEFT JOIN tabel_line tl ON tm.id_line = tl.id_line
                    WHERE tl.line IS NOT NULL AND tl.line != ''
                    ORDER BY tl.line
                """)
                
                line_choices = [('', 'Semua Line')]
                for row in cursor.fetchall():
                    if row[0] and row[1]:
                        line_choices.append((str(row[0]), row[1]))
                
                self.fields['line_filter'].choices = line_choices
                
                # Load section choices
                cursor.execute("""
                    SELECT DISTINCT tm.id_section, tms.seksi
                    FROM tabel_main tm
                    LEFT JOIN tabel_msection tms ON tm.id_section = tms.id_section
                    WHERE tms.seksi IS NOT NULL AND tms.seksi != ''
                    ORDER BY tms.seksi
                """)
                
                section_choices = [('', 'Semua Section')]
                for row in cursor.fetchall():
                    if row[0] and row[1]:
                        section_choices.append((str(row[0]), row[1]))
                
                self.fields['section_filter'].choices = section_choices
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading dynamic choices buat tabel_main: {e}")
            
            # Fallback choices kalo error
            self.fields['line_filter'].choices = [('', 'Error loading lines')]
            self.fields['section_filter'].choices = [('', 'Error loading sections')]


# Export buat diimport di views
__all__ = ['TabelMainFilterForm']


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
    """Form untuk filter daftar pengajuan - FIXED dengan Status A"""
    
    # FIXED: Status choices dengan mapping yang benar
    STATUS_CHOICES = [
        ('', 'Semua Status'),
        ('0', 'Pending'),           # Pending tetap '0'
        ('A', 'Approved'),          # FIXED: Approved menggunakan 'A' 
        ('2', 'Rejected'),          # Rejected tetap '2'
        ('3', 'In Progress'),       # In Progress tetap '3'
        ('4', 'Completed'),         # Completed tetap '4'
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
    """Form untuk approval pengajuan - FIXED dengan Action Values"""
    
    # FIXED: Action choices dengan mapping yang benar
    ACTION_CHOICES = [
        ('1', 'Approve'),   # Action '1' akan mapping ke status 'A' dan approve 'Y'
        ('2', 'Reject'),    # Action '2' akan mapping ke status '2' dan approve '2'
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
    """Form untuk filter review pengajuan - ENHANCED dengan Status A"""
    
    # FIXED: Review status choices 
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

    def load_additional_section_choices(self):
        """Load additional section choices dari database"""
        try:
            current_choices = list(self.fields['section_filter'].choices)
            
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
                    
                    # Skip jika sudah ada di choices
                    existing_keys = [choice[0] for choice in current_choices]
                    
                    # Map section berdasarkan kata kunci yang belum ada
                    section_key = None
                    if 'IT' in section_name and 'it' not in existing_keys:
                        section_key = 'it'
                    elif 'ELEKTRIK' in section_name and 'elektrik' not in existing_keys:
                        section_key = 'elektrik'
                    elif 'UTILITY' in section_name and 'utility' not in existing_keys:
                        section_key = 'utility'
                    elif 'MEKANIK' in section_name and 'mekanik' not in existing_keys:
                        section_key = 'mekanik'
                    
                    if section_key and section_key not in existing_keys:
                        current_choices.append((section_key, f'🎯 {section_name}'))
                
                self.fields['section_filter'].choices = current_choices
                
        except Exception as e:
            logger.error(f"Error loading additional section choices: {e}")


# wo_maintenance_app/forms.py - FIXED ReviewForm dengan validation yang lebih fleksibel

# class ReviewForm(forms.Form):
#     """
#     FIXED: Form review dengan validation yang user-friendly
#     """
#     ACTION_CHOICES = [
#         ('', '-- Pilih Action --'),
#         ('process', 'Process (Final: A/Y)'),
#         ('reject', 'Reject'),
#     ]
    
#     # FIXED: Section choices yang konsisten dengan mapping di views
#     TARGET_SECTION_CHOICES = [
#         ('', '-- Pilih Section Tujuan (Optional) --'),
#         ('it', '💻 IT (Information Technology)'),
#         ('elektrik', '⚡ Elektrik (Electrical)'),
#         ('mekanik', '🔧 Mekanik (Mechanical)'),
#         ('utility', '🏭 Utility (Utilities)'),
#     ]
    
#     action = forms.ChoiceField(
#         choices=ACTION_CHOICES,
#         required=True,
#         widget=forms.Select(attrs={
#             'class': 'form-select',
#             'id': 'review-action-select'
#         }),
#         help_text='Pilih action yang akan dilakukan untuk pengajuan ini.'
#     )
    
#     target_section = forms.ChoiceField(
#         choices=TARGET_SECTION_CHOICES,
#         required=False,
#         widget=forms.Select(attrs={
#             'class': 'form-select',
#             'id': 'target-section-select'
#         }),
#         help_text='Pilih section tujuan jika ingin mengubah section pengajuan. Kosongkan jika tidak ingin mengubah.'
#     )
    
#     review_notes = forms.CharField(
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 4,
#             'placeholder': 'Masukkan catatan review minimal 5 karakter...'
#         }),
#         required=True,
#         help_text='Catatan review wajib diisi minimal 5 karakter.'
#     )
    
#     def clean_review_notes(self):
#         """
#         FIXED: Validation yang lebih fleksibel untuk review notes
#         """
#         review_notes = self.cleaned_data.get('review_notes', '').strip()
        
#         if not review_notes:
#             raise forms.ValidationError('Catatan review wajib diisi.')
        
#         if len(review_notes) < 5:
#             raise forms.ValidationError('Catatan review minimal 5 karakter.')
        
#         if len(review_notes) > 2000:
#             raise forms.ValidationError('Catatan review maksimal 2000 karakter.')
        
#         return review_notes
    
#     def clean_target_section(self):
#         """
#         FIXED: Validation untuk target section
#         """
#         target_section = self.cleaned_data.get('target_section', '').strip()
        
#         # Valid sections
#         valid_sections = ['', 'it', 'elektrik', 'mekanik', 'utility']
        
#         if target_section and target_section not in valid_sections:
#             raise forms.ValidationError(f'Section "{target_section}" tidak valid.')
        
#         return target_section
    
#     def clean(self):
#         """
#         FIXED: Cross-field validation yang lebih user-friendly
#         """
#         cleaned_data = super().clean()
#         action = cleaned_data.get('action')
#         review_notes = cleaned_data.get('review_notes', '').strip()
#         target_section = cleaned_data.get('target_section', '').strip()
        
#         # Basic validation sudah dilakukan di clean_review_notes
#         if not review_notes:
#             return cleaned_data
        
#         # FIXED: Validation yang lebih fleksibel berdasarkan action
#         if action == 'process':
#             if len(review_notes) < 5:
#                 raise forms.ValidationError('Untuk memproses pengajuan, catatan minimal 5 karakter.')
#         elif action == 'reject':
#             if len(review_notes) < 10:
#                 raise forms.ValidationError('Untuk menolak pengajuan, alasan penolakan minimal 10 karakter.')
        
#         # Validation untuk kombinasi action dan target_section
#         if action == 'reject' and target_section:
#             # Clear target_section jika action reject
#             cleaned_data['target_section'] = ''
        
#         return cleaned_data

# wo_maintenance_app/forms.py - UPDATE ReviewForm dengan Priority Level

class ReviewForm(forms.Form):
    """
    ENHANCED: Form untuk review pengajuan dengan mapping section yang benar dan Priority Level
    Section mapping: 4=Mekanik(M), 5=Elektrik(E), 6=Utility(U), 8=IT(I)
    """
    
    ACTION_CHOICES = [
        ('', '-- Pilih Action --'),
        ('process', '✅ Process (Final: A/Y)'),
        ('reject', '❌ Reject')
    ]
    
    # FIXED: Target section choices dengan mapping yang benar sesuai database
    TARGET_SECTION_CHOICES = [
        ('', '-- Pilih Section (Optional) --'),
        ('mekanik', '🔧 Mekanik (ID: 4 → Code: M)'),
        ('elektrik', '⚡ Elektrik (ID: 5 → Code: E)'),
        ('utility', '🏭 Utility (ID: 6 → Code: U)'),
        ('it', '💻 IT (ID: 8 → Code: I)')
    ]
    
    # NEW: Priority Level choices untuk user 007522
    PRIORITY_CHOICES = [
        ('', '-- Pilih Prioritas (Optional) --'),
        ('BI', 'BI - Basic Important'),
        ('AI', 'AI - Advanced Important'),
        ('AOL', 'AOL - Advanced Online'),
        ('AOI', 'AOI - Advanced Offline Important'),
        ('BOL', 'BOL - Basic Online'),
        ('BOI', 'BOI - Basic Offline Important')
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'reviewAction'
        }),
        help_text='Pilih action yang akan dilakukan untuk pengajuan ini'
    )
    
    # NEW: Priority level field
    priority_level = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'priorityLevel'
        }),
        help_text='Pilih prioritas pekerjaan (akan disimpan ke field PriMa di tabel_main)'
    )
    
    target_section = forms.ChoiceField(
        choices=TARGET_SECTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'targetSection'
        }),
        help_text='Pilih section target jika ingin mengubah section tujuan (mapping: 4=M, 5=E, 6=U, 8=I)'
    )
    
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Masukkan catatan review...',
            'id': 'reviewNotes'
        }),
        required=True,
        help_text='Catatan wajib diisi untuk semua action review'
    )
    
    def clean_priority_level(self):
        """
        Validasi priority_level
        """
        priority_level = self.cleaned_data.get('priority_level', '').strip()
        
        valid_priorities = ['BI', 'AI', 'AOL', 'AOI', 'BOL', 'BOI']
        
        if priority_level and priority_level not in valid_priorities:
            logger.warning(f"Invalid priority_level {priority_level}")
            raise ValidationError(f'Priority tidak valid. Pilihan yang tersedia: {", ".join(valid_priorities)}')
        
        return priority_level
    
    def clean_target_section(self):
        """
        FIXED: Validasi target_section dengan mapping yang benar
        """
        target_section = self.cleaned_data.get('target_section', '').strip()
        
        # Mapping section yang benar sesuai database
        valid_sections = ['mekanik', 'elektrik', 'utility', 'it']
        
        if target_section and target_section not in valid_sections:
            logger.warning(f"FIXED FORM: Invalid target_section {target_section}")
            raise ValidationError(f'Section tidak valid. Pilihan yang tersedia: {", ".join(valid_sections)}')
        
        return target_section
    
    def clean(self):
        """
        ENHANCED: Validasi form secara keseluruhan dengan priority level
        """
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        target_section = cleaned_data.get('target_section')
        priority_level = cleaned_data.get('priority_level')
        review_notes = cleaned_data.get('review_notes')
        
        # Validasi action
        if action == 'process':
            if not review_notes:
                raise ValidationError('Catatan review wajib diisi untuk action Process')
            
            # Log target section untuk debugging
            if target_section:
                section_mapping = {
                    'mekanik': 4,
                    'elektrik': 5, 
                    'utility': 6,
                    'it': 8
                }
                section_id = section_mapping.get(target_section)
                logger.info(f"ENHANCED FORM: Target section {target_section} mapped to ID {section_id}")
            
            # Log priority level untuk debugging
            if priority_level:
                logger.info(f"ENHANCED FORM: Priority level selected: {priority_level}")
        
        elif action == 'reject':
            if not review_notes:
                raise ValidationError('Alasan penolakan wajib diisi untuk action Reject')
            
            # Clear priority jika reject (optional)
            if priority_level:
                logger.info(f"ENHANCED FORM: Priority level cleared for reject action")
                cleaned_data['priority_level'] = ''
        
        return cleaned_data

class EnhancedReviewFilterForm(forms.Form):
    """
    ENHANCED: Filter form untuk review list dengan section filter
    """
    
    REVIEW_STATUS_CHOICES = [
        ('', 'Semua Status Review'),
        ('0', 'Pending Review'),
        ('1', 'Reviewed (Approved)'),
        ('2', 'Reviewed (Rejected)'),
    ]
    
    SECTION_FILTER_CHOICES = [
        ('', 'Semua Section'),
        ('it', 'IT'),
        ('elektrik', 'Elektrik'),
        ('mekanik', 'Mekanik'),
        ('utility', 'Utility')
    ]
    
    tanggal_dari = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Tanggal Dari',
        required=False
    )
    
    tanggal_sampai = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Tanggal Sampai',
        required=False
    )
    
    review_status = forms.ChoiceField(
        choices=REVIEW_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Status Review',
        required=False
    )
    
    target_section_filter = forms.ChoiceField(
        choices=SECTION_FILTER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Filter Section',
        required=False
    )
    
    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari berdasarkan History ID, Pengaju, atau Deskripsi...'
        }),
        label='Pencarian',
        max_length=100,
        required=False
    )


# BACKWARD COMPATIBILITY: Pastikan ReviewForm tetap bisa digunakan tanpa parameter
def get_review_form_class():
    """
    Factory function untuk mendapatkan ReviewForm class yang sesuai
    """
    return ReviewForm


# ENHANCED: Helper function untuk form initialization
def create_review_form(request_data=None, pengajuan=None, **kwargs):
    """
    Enhanced helper function untuk create ReviewForm dengan proper initialization
    
    Args:
        request_data: POST/GET data dari request
        pengajuan: Instance pengajuan yang sedang direview
        **kwargs: Additional arguments
    
    Returns:
        ReviewForm instance yang sudah diinisialisasi
    """
    form_kwargs = {}
    
    # Extract pengajuan info untuk form customization
    if pengajuan:
        form_kwargs['pengajuan_id'] = pengajuan.get('history_id')
        form_kwargs['current_section'] = pengajuan.get('section_tujuan')
    
    # Merge dengan kwargs lain
    form_kwargs.update(kwargs)
    
    # Create form instance
    if request_data:
        return ReviewForm(request_data, **form_kwargs)
    else:
        return ReviewForm(**form_kwargs)


# Export forms
__all__ = [
    'ReviewForm',
    'EnhancedReviewFilterForm', 
    'get_review_form_class',
    'create_review_form'
]

class EnhancedPengajuanFilterForm(forms.Form):
    """
    Enhanced Filter Form dengan SDBM assignment filter - FIXED Status
    """
    
    # FIXED: Status choices dengan mapping yang benar
    STATUS_CHOICES = [
        ('', 'Semua Status'),
        ('0', 'Pending'),           # Pending tetap '0'
        ('A', 'Approved'),          # FIXED: Approved menggunakan 'A'
        ('2', 'Rejected'),          # Rejected tetap '2'
        ('3', 'In Progress'),       # In Progress tetap '3'
        ('4', 'Completed'),         # Completed tetap '4'
    ]
    
    ACCESS_TYPE_CHOICES = [
        ('', 'Semua Akses'),
        ('hierarchy', 'Hierarchy (Bawahan)'),
        ('sdbm_assigned', 'SDBM Assignment'),
        ('all', 'Semua yang Dapat Diakses')
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
        label='Status Pengajuan',
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    access_type = forms.ChoiceField(
        label='Tipe Akses',
        choices=ACCESS_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Filter berdasarkan cara akses pengajuan (hierarchy vs SDBM assignment)'
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
    
    # Enhanced filter untuk SDBM
    assigned_section = forms.ChoiceField(
        label='Assigned Section',
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Filter pengajuan berdasarkan section assignment SDBM'
    )
    
    def __init__(self, *args, **kwargs):
        user_hierarchy = kwargs.pop('user_hierarchy', None)
        super().__init__(*args, **kwargs)
        
        # Load SDBM section choices untuk filter
        self.load_assigned_section_choices(user_hierarchy)
    
    def load_assigned_section_choices(self, user_hierarchy):
        """
        Load section choices berdasarkan SDBM assignments user
        """
        try:
            choices = [('', 'Semua Section')]
            
            if user_hierarchy:
                from wo_maintenance_app.utils import get_assigned_pengajuan_for_sdbm_user, get_sdbm_section_mapping
                
                # Get user assignments
                employee_number = user_hierarchy.get('employee_number')
                assignments = get_assigned_pengajuan_for_sdbm_user(employee_number)
                
                # Get unique sections dari assignments
                assigned_sections = set()
                for assignment in assignments:
                    if isinstance(assignment, dict) and assignment.get('target_section'):
                        assigned_sections.add(assignment['target_section'])
                
                # Get section mapping untuk display names
                section_mapping = get_sdbm_section_mapping()
                
                for section_key in assigned_sections:
                    section_info = section_mapping.get(section_key, {})
                    display_name = section_info.get('display_name', section_key.title())
                    choices.append((section_key, display_name))
            
            self.fields['assigned_section'].choices = choices
            
        except Exception as e:
            logger.error(f"Error loading assigned section choices: {e}")
            self.fields['assigned_section'].choices = [('', 'Semua Section')]


class SupervisorAccessFilterForm(forms.Form):
    """
    Form untuk filter pengajuan berdasarkan level supervisor dan section
    """
    
    SUPERVISOR_LEVEL_CHOICES = [
        ('', 'Semua Level'),
        ('assistant_supervisor', 'Assistant Supervisor'),
        ('supervisor', 'Supervisor'),
        ('senior_supervisor', 'Senior Supervisor'),
        ('manager', 'Manager'),
        ('general_manager', 'General Manager'),
        ('director', 'Director'),
    ]
    
    supervisor_level = forms.ChoiceField(
        label='Level Minimum',
        choices=SUPERVISOR_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Filter berdasarkan level minimum supervisor yang dapat mengakses'
    )
    
    target_section = forms.ChoiceField(
        label='Target Section',
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
        }),
        help_text='Filter berdasarkan target section untuk assignment'
    )
    
    show_siti_access = forms.BooleanField(
        label='Tampilkan Akses SITI FATIMAH',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Tampilkan pengajuan yang dapat diakses oleh SITI FATIMAH (007522)'
    )


# Helper function untuk mapping status
def map_form_status_to_db(form_status):
    """
    Map form status values ke database values
    
    Args:
        form_status (str): Status dari form (legacy values)
        
    Returns:
        str: Status untuk database (actual values)
    """
    status_mapping = {
        '0': STATUS_PENDING,     # '0' -> '0' 
        '1': STATUS_APPROVED,    # '1' -> 'A'  (FIXED)
        '2': STATUS_REJECTED,    # '2' -> '2'
        '3': STATUS_IN_PROGRESS, # '3' -> '3'
        '4': STATUS_COMPLETED,   # '4' -> '4'
    }
    
    return status_mapping.get(form_status, form_status)


def map_form_approve_to_db(form_approve):
    """
    Map form approve values ke database values
    
    Args:
        form_approve (str): Approve dari form (legacy values)
        
    Returns:
        str: Approve untuk database (actual values)
    """
    approve_mapping = {
        '0': APPROVE_NO,         # '0' -> '0'
        '1': APPROVE_YES,        # '1' -> 'Y'  (FIXED)
        '2': APPROVE_REJECTED,   # '2' -> '2'
    }
    
    return approve_mapping.get(form_approve, form_approve)


def get_status_display_name(status_value):
    """
    Get display name untuk status value
    
    Args:
        status_value (str): Status value dari database
        
    Returns:
        str: Display name untuk status
    """
    status_display = {
        '0': 'Pending',
        'A': 'Approved',         # FIXED
        '2': 'Rejected',
        '3': 'In Progress',
        '4': 'Completed'
    }
    
    return status_display.get(status_value, 'Unknown')


def get_approve_display_name(approve_value):
    """
    Get display name untuk approve value
    
    Args:
        approve_value (str): Approve value dari database
        
    Returns:
        str: Display name untuk approve
    """
    approve_display = {
        '0': 'Not Approved',
        'Y': 'Approved',         # FIXED
        '2': 'Rejected'
    }
    
    return approve_display.get(approve_value, 'Unknown')


# Export constants untuk digunakan di views dan templates
__all__ = [
    'PengajuanMaintenanceForm',
    'PengajuanFilterForm', 
    'ApprovalForm',
    'ReviewFilterForm',
    'ReviewForm',
    'EnhancedPengajuanFilterForm',
    'SupervisorAccessFilterForm',
    'STATUS_PENDING',
    'STATUS_APPROVED',
    'STATUS_REJECTED', 
    'STATUS_IN_PROGRESS',
    'STATUS_COMPLETED',
    'APPROVE_NO',
    'APPROVE_YES',
    'APPROVE_REJECTED',
    'map_form_status_to_db',
    'map_form_approve_to_db',
    'get_status_display_name',
    'get_approve_display_name'
]

# class HistoryMaintenanceForm(forms.Form):
#     """
#     Form buat edit data history maintenance di tabel_main
#     Form yang asik dan user-friendly buat ngatur data history
#     """
    
#     # Analisis masalah
#     penyebab = forms.CharField(
#         label='Penyebab Masalah',
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'placeholder': 'Deskripsikan penyebab utama masalah yang terjadi...'
#         }),
#         help_text='Jelaskan apa yang menyebabkan masalah ini terjadi'
#     )
    
#     akar_masalah = forms.CharField(
#         label='Akar Masalah',
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'placeholder': 'Analisa akar masalah yang sebenarnya...'
#         }),
#         help_text='Root cause analysis - akar masalah yang mendasari'
#     )
    
#     # Tindakan yang diambil
#     tindakan_perbaikan = forms.CharField(
#         label='Tindakan Perbaikan',
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'placeholder': 'Jelaskan tindakan perbaikan yang sudah/akan dilakukan...'
#         }),
#         help_text='Tindakan corrective action yang dilakukan'
#     )
    
#     tindakan_pencegahan = forms.CharField(
#         label='Tindakan Pencegahan',
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'placeholder': 'Jelaskan tindakan preventive untuk mencegah masalah serupa...'
#         }),
#         help_text='Tindakan preventive action untuk mencegah masalah berulang'
#     )
    
#     # Status pekerjaan
#     STATUS_PEKERJAAN_CHOICES = [
#         ('0', 'Open - Belum Selesai'),
#         ('1', 'Close - Sudah Selesai'),
#     ]
    
#     status_pekerjaan = forms.ChoiceField(
#         label='Status Pekerjaan',
#         choices=STATUS_PEKERJAAN_CHOICES,
#         widget=forms.RadioSelect(attrs={
#             'class': 'form-check-input'
#         }),
#         help_text='Status penyelesaian pekerjaan maintenance'
#     )
    
#     # PIC (Person In Charge)
#     pic_produksi = forms.CharField(
#         label='PIC Produksi',
#         max_length=500,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Nama PIC dari sisi produksi...'
#         }),
#         help_text='Person In Charge dari departemen produksi'
#     )
    
#     pic_maintenance = forms.CharField(
#         label='PIC Maintenance',
#         max_length=500,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Nama PIC dari sisi maintenance...'
#         }),
#         help_text='Person In Charge dari departemen maintenance'
#     )
    
#     # Status general
#     STATUS_CHOICES = [
#         ('0', 'Open - Masih Aktif'),
#         ('1', 'Close - Sudah Selesai'),
#     ]
    
#     status = forms.ChoiceField(
#         label='Status Umum',
#         choices=STATUS_CHOICES,
#         widget=forms.RadioSelect(attrs={
#             'class': 'form-check-input'
#         }),
#         help_text='Status umum dari pengajuan maintenance'
#     )
    
#     # Tanggal pekerjaan mulai dan selesai
#     tgl_wp_dari = forms.DateTimeField(
#         label='Tanggal Mulai Work',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal dan waktu mulai pekerjaan'
#     )
    
#     tgl_wp_sampai = forms.DateTimeField(
#         label='Tanggal Selesai Work',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal dan waktu selesai pekerjaan'
#     )
    
#     # Lead time
#     tgl_lt_dari = forms.DateTimeField(
#         label='Lead Time Mulai',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal mulai lead time'
#     )
    
#     tgl_lt_sampai = forms.DateTimeField(
#         label='Lead Time Selesai',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal selesai lead time'
#     )
    
#     # Downtime
#     tgl_dt_dari = forms.DateTimeField(
#         label='Downtime Mulai',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal mulai downtime'
#     )
    
#     tgl_dt_sampai = forms.DateTimeField(
#         label='Downtime Selesai',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal selesai downtime'
#     )
    
#     alasan_dt = forms.CharField(
#         label='Alasan Downtime',
#         required=False,
#         max_length=240,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Jelaskan alasan terjadinya downtime...'
#         }),
#         help_text='Alasan mengapa terjadi downtime'
#     )
    
#     # Estimasi dan selesai
#     tgl_estimasidt = forms.DateTimeField(
#         label='Estimasi Selesai',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Estimasi tanggal dan waktu selesai'
#     )
    
#     tgl_selesai = forms.DateTimeField(
#         label='Tanggal Selesai Aktual',
#         required=False,
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'class': 'form-control'
#         }),
#         help_text='Tanggal dan waktu selesai yang sebenarnya'
#     )
    
#     # Additional fields
#     alasan_delay = forms.CharField(
#         label='Alasan Delay (jika ada)',
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 2,
#             'placeholder': 'Jelaskan alasan jika ada delay...'
#         }),
#         help_text='Alasan jika terjadi keterlambatan'
#     )
    
#     masalah = forms.CharField(
#         label='Detail Masalah',
#         required=False,
#         max_length=500,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Detail tambahan tentang masalah...'
#         }),
#         help_text='Detail tambahan masalah (maksimal 500 karakter)'
#     )
    
#     def __init__(self, *args, **kwargs):
#         self.history_data = kwargs.pop('history_data', None)
#         super().__init__(*args, **kwargs)
        
#         # Pre-populate form jika ada data history
#         if self.history_data:
#             self.populate_from_history()

class HistoryMaintenanceForm(forms.Form):
    """Form untuk edit history maintenance - UPDATED: Hapus Status Umum"""
    
    # UPDATED: Hanya Status Pekerjaan yang ditampilkan
    STATUS_PEKERJAAN_CHOICES = [
        ('O', 'Open'),
        ('C', 'Close'),
    ]
    
    # Analysis fields
    penyebab = forms.CharField(
        label='Penyebab Masalah',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Jelaskan penyebab masalah...'
        }),
        help_text='Identifikasi penyebab masalah yang terjadi'
    )
    
    akar_masalah = forms.CharField(
        label='Akar Masalah',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Jelaskan akar masalah...'
        }),
        help_text='Analisis mendalam tentang akar masalah'
    )
    
    # Action fields
    tindakan_perbaikan = forms.CharField(
        label='Tindakan Perbaikan',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Jelaskan tindakan perbaikan yang dilakukan...'
        }),
        help_text='Detail tindakan perbaikan yang telah dilakukan'
    )
    
    tindakan_pencegahan = forms.CharField(
        label='Tindakan Pencegahan',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Jelaskan tindakan pencegahan...'
        }),
        help_text='Tindakan untuk mencegah masalah serupa di masa depan'
    )
    
    # PIC fields
    pic_produksi = forms.CharField(
        label='PIC Produksi',
        required=True,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama PIC dari produksi...'
        }),
        help_text='Person In Charge dari sisi produksi'
    )
    
    pic_maintenance = forms.CharField(
        label='PIC Maintenance',
        required=True,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama PIC dari maintenance...'
        }),
        help_text='Person In Charge dari sisi maintenance'
    )
    
    # UPDATED: Hanya Status Pekerjaan field, Status Umum dihapus
    status_pekerjaan = forms.ChoiceField(
        label='Status Pekerjaan',
        choices=STATUS_PEKERJAAN_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        help_text='Status pekerjaan maintenance (O=Open, C=Close)'
    )
    
    # Datetime fields (unchanged)
    tgl_wp_dari = forms.DateTimeField(
        label='Waktu Pekerjaan Dari',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Waktu mulai pekerjaan'
    )
    
    tgl_wp_sampai = forms.DateTimeField(
        label='Waktu Pekerjaan Sampai',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Waktu selesai pekerjaan'
    )
    
    tgl_lt_dari = forms.DateTimeField(
        label='Lead Time Dari',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Lead time mulai'
    )
    
    tgl_lt_sampai = forms.DateTimeField(
        label='Lead Time Sampai',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Lead time selesai'
    )
    
    tgl_dt_dari = forms.DateTimeField(
        label='Downtime Dari',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Downtime mulai'
    )
    
    tgl_dt_sampai = forms.DateTimeField(
        label='Downtime Sampai',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Downtime selesai'
    )
    
    alasan_dt = forms.CharField(
        label='Alasan Downtime',
        required=False,
        max_length=240,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Alasan terjadinya downtime...'
        }),
        help_text='Penjelasan alasan terjadinya downtime'
    )
    
    tgl_estimasidt = forms.DateTimeField(
        label='Estimasi Selesai',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Estimasi waktu selesai'
    )
    
    tgl_selesai = forms.DateTimeField(
        label='Tanggal Selesai',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Tanggal aktual selesai'
    )
    
    alasan_delay = forms.CharField(
        label='Alasan Delay',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Alasan jika terjadi delay...'
        }),
        help_text='Penjelasan jika terjadi keterlambatan'
    )
    
    masalah = forms.CharField(
        label='Masalah Tambahan',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Masalah tambahan yang ditemukan...'
        }),
        help_text='Masalah tambahan yang ditemukan selama proses'
    )
    
    def __init__(self, *args, **kwargs):
        history_data = kwargs.pop('history_data', {})
        super().__init__(*args, **kwargs)
        
        # Pre-populate fields dengan data yang ada
        if history_data:
            for field_name, field in self.fields.items():
                if field_name in history_data and history_data[field_name]:
                    self.initial[field_name] = history_data[field_name]

    def clean_pic_produksi(self):
        """Validasi PIC produksi"""
        pic_produksi = self.cleaned_data.get('pic_produksi', '').strip()
        if not pic_produksi:
            pic_produksi = '-'  # Default value sesuai DB constraint
        return pic_produksi
    
    def clean_pic_maintenance(self):
        """Validasi PIC maintenance"""
        pic_maintenance = self.cleaned_data.get('pic_maintenance', '').strip()
        if not pic_maintenance:
            pic_maintenance = '-'  # Default value sesuai DB constraint
        return pic_maintenance
    
    def clean(self):
        """Custom validation untuk form"""
        cleaned_data = super().clean()
        
        # Validasi tanggal work
        tgl_wp_dari = cleaned_data.get('tgl_wp_dari')
        tgl_wp_sampai = cleaned_data.get('tgl_wp_sampai')
        
        if tgl_wp_dari and tgl_wp_sampai:
            if tgl_wp_dari > tgl_wp_sampai:
                raise forms.ValidationError({
                    'tgl_wp_sampai': 'Tanggal selesai work tidak boleh lebih awal dari tanggal mulai'
                })
        
        # Validasi lead time
        tgl_lt_dari = cleaned_data.get('tgl_lt_dari')
        tgl_lt_sampai = cleaned_data.get('tgl_lt_sampai')
        
        if tgl_lt_dari and tgl_lt_sampai:
            if tgl_lt_dari > tgl_lt_sampai:
                raise forms.ValidationError({
                    'tgl_lt_sampai': 'Tanggal selesai lead time tidak boleh lebih awal dari tanggal mulai'
                })
        
        # Validasi downtime
        tgl_dt_dari = cleaned_data.get('tgl_dt_dari')
        tgl_dt_sampai = cleaned_data.get('tgl_dt_sampai')
        
        if tgl_dt_dari and tgl_dt_sampai:
            if tgl_dt_dari > tgl_dt_sampai:
                raise forms.ValidationError({
                    'tgl_dt_sampai': 'Tanggal selesai downtime tidak boleh lebih awal dari tanggal mulai'
                })
        
        # Validasi estimasi vs actual
        tgl_estimasi = cleaned_data.get('tgl_estimasidt')
        tgl_selesai = cleaned_data.get('tgl_selesai')
        
        if tgl_estimasi and tgl_selesai:
            if tgl_selesai > tgl_estimasi:
                # Jika actual lebih lama dari estimasi, alasan_delay harus diisi
                alasan_delay = cleaned_data.get('alasan_delay', '').strip()
                if not alasan_delay:
                    cleaned_data['alasan_delay'] = 'Penyelesaian melebihi estimasi'
        
        return cleaned_data


# class HistoryFilterForm(forms.Form):
#     """
#     Form filter buat history pengajuan maintenance
#     Bikin searching dan filtering jadi lebih asik
#     """
    
#     STATUS_CHOICES = [
#         ('', 'Semua Status'),
#         ('0', 'Open'),
#         ('1', 'Close'),
#     ]
    
#     STATUS_PEKERJAAN_CHOICES = [
#         ('', 'Semua Status Pekerjaan'),
#         ('0', 'Open'),
#         ('1', 'Close'),
#     ]
    
#     # Filter tanggal
#     tanggal_dari = forms.DateField(
#         label='Tanggal Dari',
#         required=False,
#         widget=forms.DateInput(attrs={
#             'type': 'date',
#             'class': 'form-control'
#         })
#     )
    
#     tanggal_sampai = forms.DateField(
#         label='Tanggal Sampai',
#         required=False,
#         widget=forms.DateInput(attrs={
#             'type': 'date',
#             'class': 'form-control'
#         })
#     )
    
#     # Filter status
#     status = forms.ChoiceField(
#         label='Status Umum',
#         choices=STATUS_CHOICES,
#         required=False,
#         widget=forms.Select(attrs={
#             'class': 'form-control'
#         })
#     )
    
#     status_pekerjaan = forms.ChoiceField(
#         label='Status Pekerjaan',
#         choices=STATUS_PEKERJAAN_CHOICES,
#         required=False,
#         widget=forms.Select(attrs={
#             'class': 'form-control'
#         })
#     )
    
#     # Search fields
#     history_id = forms.CharField(
#         label='History ID',
#         required=False,
#         max_length=15,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Cari History ID...'
#         })
#     )
    
#     pengaju = forms.CharField(
#         label='Pengaju',
#         required=False,
#         max_length=100,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Cari nama pengaju...'
#         })
#     )
    
#     pic_produksi = forms.CharField(
#         label='PIC Produksi',
#         required=False,
#         max_length=100,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Cari PIC Produksi...'
#         })
#     )
    
#     pic_maintenance = forms.CharField(
#         label='PIC Maintenance',
#         required=False,
#         max_length=100,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Cari PIC Maintenance...'
#         })
#     )
    
#     # Filter berdasarkan section
#     section_filter = forms.ChoiceField(
#         label='Filter Section',
#         choices=[],  # Will be populated in __init__
#         required=False,
#         widget=forms.Select(attrs={
#             'class': 'form-control'
#         })
#     )
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Load section choices dari database
#         self.load_section_choices()
    
#     def load_section_choices(self):
#         """Load pilihan section dari database"""
#         try:
#             choices = [('', 'Semua Section')]
            
#             with connections['DB_Maintenance'].cursor() as cursor:
#                 cursor.execute("""
#                     SELECT DISTINCT tm.id_section, ms.seksi
#                     FROM tabel_main tm
#                     LEFT JOIN tabel_msection ms ON tm.id_section = ms.id_section
#                     WHERE ms.seksi IS NOT NULL AND ms.seksi != ''
#                     ORDER BY ms.seksi
#                 """)
                
#                 for row in cursor.fetchall():
#                     if row[0] and row[1]:
#                         choices.append((str(int(float(row[0]))), row[1]))
            
#             self.fields['section_filter'].choices = choices
            
#         except Exception as e:
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.error(f"Error loading section choices for history: {e}")
#             self.fields['section_filter'].choices = [('', 'Semua Section')]

class HistoryFilterForm(forms.Form):
    """Form untuk filter history pengajuan - UPDATED: Hapus Status Umum Filter"""
    
    # UPDATED: Hanya Status Pekerjaan filter, Status Umum dihapus
    STATUS_PEKERJAAN_CHOICES = [
        ('', 'Semua Status Pekerjaan'),
        ('O', 'Open'),
        ('C', 'Close'),
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
    
    # UPDATED: Hanya status_pekerjaan field, status umum dihapus
    status_pekerjaan = forms.ChoiceField(
        label='Status Pekerjaan',
        choices=STATUS_PEKERJAAN_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
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
    
    pengaju = forms.CharField(
        label='Pengaju',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari nama pengaju...'
        })
    )
    
    pic_produksi = forms.CharField(
        label='PIC Produksi',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari PIC Produksi...'
        })
    )
    
    pic_maintenance = forms.CharField(
        label='PIC Maintenance',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari PIC Maintenance...'
        })
    )
    
    section_filter = forms.ChoiceField(
        label='Section Filter',
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_section_choices()
    
    def load_section_choices(self):
        """Load pilihan section dari database"""
        try:
            choices = [('', 'Semua Section')]
            
            with connections['DB_Maintenance'].cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT id_section, seksi 
                    FROM tabel_msection 
                    WHERE (status = 'A' OR status IS NULL) AND seksi IS NOT NULL
                    ORDER BY seksi
                """)
                
                for row in cursor.fetchall():
                    section_id = int(float(row[0]))
                    section_name = str(row[1]).strip()
                    choices.append((str(section_id), section_name))
            
            self.fields['section_filter'].choices = choices
            
        except Exception as e:
            logger.error(f"Error loading section choices for history filter: {e}")
            self.fields['section_filter'].choices = [('', 'Error loading sections')]

# UPDATED: Helper function untuk update history maintenance
def update_history_maintenance(history_id, form_data, user):
    """
    Update data history maintenance - UPDATED: Auto-set status umum ke 'A'
    
    Args:
        history_id: ID history yang akan diupdate
        form_data: Data dari form
        user: User yang melakukan update
    
    Returns:
        dict: Result dengan success status dan message
    """
    try:
        with connections['DB_Maintenance'].cursor() as cursor:
            # UPDATED: Status umum otomatis di-set ke 'A', hanya status_pekerjaan yang bisa diubah
            status_pekerjaan = form_data.get('status_pekerjaan', 'O')
            
            # Ensure valid values
            if status_pekerjaan not in ['O', 'C']:
                status_pekerjaan = 'O'  # Default ke Open
            
            # Build update query dengan semua fields
            update_fields = []
            update_params = []
            
            # Text fields
            text_fields = [
                'penyebab', 'akar_masalah', 'tindakan_perbaikan', 
                'tindakan_pencegahan', 'pic_produksi', 'pic_maintenance',
                'alasan_dt', 'alasan_delay', 'masalah'
            ]
            
            for field in text_fields:
                if field in form_data:
                    value = form_data[field]
                    if value:  # Only update if not empty
                        update_fields.append(f"{field} = %s")
                        update_params.append(value)
            
            # Datetime fields
            datetime_fields = [
                'tgl_wp_dari', 'tgl_wp_sampai', 'tgl_lt_dari', 'tgl_lt_sampai',
                'tgl_dt_dari', 'tgl_dt_sampai', 'tgl_estimasidt', 'tgl_selesai'
            ]
            
            for field in datetime_fields:
                if field in form_data and form_data[field]:
                    update_fields.append(f"{field} = %s")
                    update_params.append(form_data[field])
            
            # UPDATED: Status fields - auto set status umum ke 'A', hanya status_pekerjaan yang user bisa ubah
            update_fields.extend([
                "status = %s",              # Auto-set ke 'A'
                "status_pekerjaan = %s",    # User controlled
                "usert_edit = %s",
                "tgl_edit = GETDATE()"
            ])
            update_params.extend([
                'A',                        # UPDATED: Auto-set status umum ke 'A'
                status_pekerjaan,           # User controlled status pekerjaan
                user.username
            ])
            
            # Build final query
            update_query = f"""
                UPDATE tabel_main 
                SET {', '.join(update_fields)}
                WHERE history_id = %s
            """
            update_params.append(history_id)
            
            # Execute update
            cursor.execute(update_query, update_params)
            
            if cursor.rowcount > 0:
                logger.info(f"Successfully updated history {history_id} by {user.username} (status auto-set to A)")
                return {
                    'success': True,
                    'message': f'Data history {history_id} berhasil diperbarui!'
                }
            else:
                return {
                    'success': False,
                    'message': f'History {history_id} tidak ditemukan atau tidak ada perubahan.'
                }
            
    except Exception as e:
        logger.error(f"Error updating history {history_id}: {e}")
        return {
            'success': False,
            'message': f'Terjadi kesalahan saat mengupdate data: {str(e)}'
        }


# Export untuk digunakan di views
__all__ = [
    'HistoryMaintenanceForm',
    'HistoryFilterForm', 
    'update_history_maintenance'
]