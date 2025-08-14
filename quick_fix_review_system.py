# quick_fix_review_system.py
# Script untuk quick fix masalah review system SITI FATIMAH

import os
import sys
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starter_kit.settings')
django.setup()

from django.db import connections
import logging

logger = logging.getLogger(__name__)

def quick_fix_review_system():
    """
    Quick fix untuk masalah review system SITI FATIMAH
    """
    print("🔧 Starting Quick Fix for Review System...")
    
    fixes_applied = []
    errors = []
    
    # Fix 1: Ensure review tables and columns exist
    try:
        print("📋 Step 1: Ensuring review tables exist...")
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Add review columns if missing
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_status')
                BEGIN
                    ALTER TABLE tabel_pengajuan ADD review_status varchar(1) NULL DEFAULT '0'
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'reviewed_by')
                BEGIN
                    ALTER TABLE tabel_pengajuan ADD reviewed_by varchar(50) NULL
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_date')
                BEGIN
                    ALTER TABLE tabel_pengajuan ADD review_date datetime NULL
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'review_notes')
                BEGIN
                    ALTER TABLE tabel_pengajuan ADD review_notes varchar(max) NULL
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME = 'final_section_id')
                BEGIN
                    ALTER TABLE tabel_pengajuan ADD final_section_id float NULL
                END
            """)
            
            # Create assignment table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_pengajuan_assignment' AND xtype='U')
                BEGIN
                    CREATE TABLE [dbo].[tabel_pengajuan_assignment](
                        [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                        [history_id] [varchar](15) NULL,
                        [assigned_to_employee] [varchar](50) NULL,
                        [assigned_by_employee] [varchar](50) NULL,
                        [assignment_date] [datetime] NULL,
                        [is_active] [bit] NULL DEFAULT 1,
                        [notes] [varchar](max) NULL,
                        [assignment_type] [varchar](50) NULL DEFAULT 'MANUAL'
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
            # Create review log table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tabel_review_log' AND xtype='U')
                BEGIN
                    CREATE TABLE [dbo].[tabel_review_log](
                        [id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                        [history_id] [varchar](15) NULL,
                        [reviewer_employee] [varchar](50) NULL,
                        [action] [varchar](10) NULL,
                        [target_section] [varchar](50) NULL,
                        [review_notes] [varchar](max) NULL,
                        [priority_level] [varchar](20) NULL,
                        [review_date] [datetime] NULL
                    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
                END
            """)
            
        fixes_applied.append("✅ Review tables and columns created/verified")
        print("   ✅ Review tables and columns verified")
        
    except Exception as e:
        error_msg = f"❌ Error creating review tables: {e}"
        errors.append(error_msg)
        print(f"   {error_msg}")
    
    # Fix 2: Initialize approved pengajuan for review
    try:
        print("📋 Step 2: Initializing approved pengajuan for review...")
        
        with connections['DB_Maintenance'].cursor() as cursor:
            cursor.execute("""
                UPDATE tabel_pengajuan 
                SET review_status = '0'
                WHERE status = 'A' AND approve = 'Y' 
                    AND (review_status IS NULL OR review_status = '')
            """)
            
            updated_count = cursor.rowcount
            
            # Get counts for reporting
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = 'A' AND approve = 'Y'
            """)
            total_approved = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COUNT(*) FROM tabel_pengajuan 
                WHERE status = 'A' AND approve = 'Y' 
                    AND (review_status IS NULL OR review_status = '0')
            """)
            pending_review = cursor.fetchone()[0] or 0
            
        fixes_applied.append(f"✅ Initialized {updated_count} pengajuan for review")
        print(f"   ✅ Found {total_approved} approved pengajuan")
        print(f"   ✅ {pending_review} pengajuan ready for review")
        
    except Exception as e:
        error_msg = f"❌ Error initializing review data: {e}"
        errors.append(error_msg)
        print(f"   {error_msg}")
    
    # Fix 3: Create quick fix views patch
    try:
        print("📋 Step 3: Creating views patch file...")
        
        patch_content = '''# QUICK FIX PATCH for wo_maintenance_app/views.py
# Add these functions to fix the review system

def is_reviewer_fixed(request):
    """FIXED: Check if user is SITI FATIMAH using request object"""
    if not request.user.is_authenticated:
        return False
    
    # Primary check: username
    if request.user.username == '007522':
        return True
    
    # Session check
    try:
        employee_data = request.session.get('employee_data')
        if employee_data and employee_data.get('employee_number') == '007522':
            return True
    except:
        pass
    
    return False

def reviewer_required_fixed(view_func):
    """FIXED: Decorator dengan better error handling"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Silakan login terlebih dahulu.')
            return redirect('login')
        
        if not is_reviewer_fixed(request):
            messages.error(request, 'Akses ditolak. Halaman review hanya untuk SITI FATIMAH.')
            
            # FIXED: Better redirect handling for POST requests
            if request.method == 'POST' and 'nomor_pengajuan' in kwargs:
                return redirect('wo_maintenance_app:review_pengajuan_detail', 
                               nomor_pengajuan=kwargs['nomor_pengajuan'])
            return redirect('wo_maintenance_app:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

# USAGE: Replace @reviewer_required with @reviewer_required_fixed
# Replace is_reviewer(request.user) with is_reviewer_fixed(request)
'''
        
        patch_file = Path('quick_fix_views_patch.py')
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(patch_content)
        
        fixes_applied.append(f"✅ Created patch file: {patch_file}")
        print(f"   ✅ Patch file created: {patch_file}")
        
    except Exception as e:
        error_msg = f"❌ Error creating patch file: {e}"
        errors.append(error_msg)
        print(f"   {error_msg}")
    
    # Fix 4: Check SDBM connection
    try:
        print("📋 Step 4: Testing SDBM connection...")
        
        with connections['SDBM'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE employee_number = '007522'")
            siti_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM [hrbp].[employees] WHERE is_active = 1")
            active_employees = cursor.fetchone()[0]
        
        fixes_applied.append(f"✅ SDBM connection OK - {active_employees} active employees")
        print(f"   ✅ SDBM connection successful")
        print(f"   ✅ Found SITI FATIMAH in SDBM: {'Yes' if siti_count > 0 else 'No'}")
        
    except Exception as e:
        error_msg = f"⚠️ SDBM connection issue: {e}"
        errors.append(error_msg)
        print(f"   {error_msg}")
    
    # Fix 5: Test review system status
    try:
        print("📋 Step 5: Testing review system status...")
        
        with connections['DB_Maintenance'].cursor() as cursor:
            # Check if review columns exist
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tabel_pengajuan' AND COLUMN_NAME IN 
                ('review_status', 'reviewed_by', 'review_date', 'review_notes', 'final_section_id')
            """)
            review_columns = cursor.fetchone()[0]
            
            # Check assignment table
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'tabel_pengajuan_assignment'
            """)
            assignment_table = cursor.fetchone()[0]
            
        status = "✅ READY" if review_columns == 5 and assignment_table == 1 else "❌ INCOMPLETE"
        fixes_applied.append(f"{status} Review system status check")
        print(f"   {status} Review columns: {review_columns}/5")
        print(f"   {status} Assignment table: {'EXISTS' if assignment_table == 1 else 'MISSING'}")
        
    except Exception as e:
        error_msg = f"❌ Error checking system status: {e}"
        errors.append(error_msg)
        print(f"   {error_msg}")
    
    # Summary
    print("\n" + "="*60)
    print("🎯 QUICK FIX SUMMARY")
    print("="*60)
    
    if fixes_applied:
        print("✅ FIXES APPLIED:")
        for fix in fixes_applied:
            print(f"   {fix}")
    
    if errors:
        print("\n❌ ERRORS ENCOUNTERED:")
        for error in errors:
            print(f"   {error}")
    
    print(f"\n📊 RESULTS: {len(fixes_applied)} fixes applied, {len(errors)} errors")
    
    # Manual steps
    print("\n📝 MANUAL STEPS REQUIRED:")
    print("   1. Replace @reviewer_required with @reviewer_required_fixed in views.py")
    print("   2. Replace is_reviewer(request.user) with is_reviewer_fixed(request)")
    print("   3. Add the fixed functions from quick_fix_views_patch.py")
    print("   4. Restart Django server")
    print("   5. Test review flow with SITI FATIMAH (007522)")
    
    return len(fixes_applied), len(errors)

if __name__ == "__main__":
    try:
        fixes, errors = quick_fix_review_system()
        
        if errors == 0:
            print("\n🎉 QUICK FIX COMPLETED SUCCESSFULLY!")
            print("   Review system should now work properly for SITI FATIMAH")
            sys.exit(0)
        else:
            print(f"\n⚠️ QUICK FIX COMPLETED WITH {errors} ERRORS")
            print("   Please check the errors above and fix manually")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)