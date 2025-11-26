"""
Database migration script to add traceability and state fields to plans.

This script adds:
- created_by, modified_by, modified_at columns
- state column (draft, approved, active, completed)

Run this before using the updated plan features.
"""

import sqlite3
import shutil
from datetime import datetime
import os

DB_PATH = "fitness_agent.db"
BACKUP_PATH = f"fitness_agent_backup_traceability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def backup_database():
    """Create a backup of the current database"""
    if os.path.exists(DB_PATH):
        print(f"Creating backup: {BACKUP_PATH}")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created successfully")
    else:
        print(f"⚠️  No existing database found at {DB_PATH}")


def migrate_database():
    """Add traceability and state columns to plan tables"""
    print(f"\nMigrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # === WORKOUT PLANS TABLE ===
        print("\n📋 Migrating workout_plans table...")
        cursor.execute("PRAGMA table_info(workout_plans)")
        workout_columns = [col[1] for col in cursor.fetchall()]
        
        # Add created_by column
        if 'created_by' not in workout_columns:
            print("  Adding 'created_by' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN created_by TEXT
            ''')
            print("  ✅ Added 'created_by'")
        else:
            print("  ⏭️  'created_by' already exists")
        
        # Add modified_at column
        if 'modified_at' not in workout_columns:
            print("  Adding 'modified_at' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN modified_at TEXT
            ''')
            print("  ✅ Added 'modified_at'")
        else:
            print("  ⏭️  'modified_at' already exists")
        
        # Add modified_by column
        if 'modified_by' not in workout_columns:
            print("  Adding 'modified_by' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN modified_by TEXT
            ''')
            print("  ✅ Added 'modified_by'")
        else:
            print("  ⏭️  'modified_by' already exists")
        
        # Add state column
        if 'state' not in workout_columns:
            print("  Adding 'state' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN state TEXT DEFAULT 'draft'
            ''')
            # Update existing plans to draft state
            cursor.execute('''
                UPDATE workout_plans
                SET state = 'draft'
                WHERE state IS NULL
            ''')
            print("  ✅ Added 'state' column")
        else:
            print("  ⏭️  'state' already exists")
        
        # === NUTRITION PLANS TABLE ===
        print("\n🥗 Migrating nutrition_plans table...")
        cursor.execute("PRAGMA table_info(nutrition_plans)")
        nutrition_columns = [col[1] for col in cursor.fetchall()]
        
        # Add created_by column
        if 'created_by' not in nutrition_columns:
            print("  Adding 'created_by' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN created_by TEXT
            ''')
            print("  ✅ Added 'created_by'")
        else:
            print("  ⏭️  'created_by' already exists")
        
        # Add modified_at column
        if 'modified_at' not in nutrition_columns:
            print("  Adding 'modified_at' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN modified_at TEXT
            ''')
            print("  ✅ Added 'modified_at'")
        else:
            print("  ⏭️  'modified_at' already exists")
        
        # Add modified_by column
        if 'modified_by' not in nutrition_columns:
            print("  Adding 'modified_by' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN modified_by TEXT
            ''')
            print("  ✅ Added 'modified_by'")
        else:
            print("  ⏭️  'modified_by' already exists")
        
        # Add state column
        if 'state' not in nutrition_columns:
            print("  Adding 'state' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN state TEXT DEFAULT 'draft'
            ''')
            # Update existing plans to draft state
            cursor.execute('''
                UPDATE nutrition_plans
                SET state = 'draft'
                WHERE state IS NULL
            ''')
            print("  ✅ Added 'state' column")
        else:
            print("  ⏭️  'state' already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show updated schemas
        print("\n📊 Updated workout_plans schema:")
        cursor.execute("PRAGMA table_info(workout_plans)")
        for col in cursor.fetchall():
            print(f"  - {col[1]}: {col[2]}")
        
        print("\n📊 Updated nutrition_plans schema:")
        cursor.execute("PRAGMA table_info(nutrition_plans)")
        for col in cursor.fetchall():
            print(f"  - {col[1]}: {col[2]}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        print(f"You can restore from backup: {BACKUP_PATH}")
        raise
    finally:
        conn.close()


def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Count plans
        cursor.execute("SELECT COUNT(*) FROM workout_plans")
        workout_count = cursor.fetchone()[0]
        print(f"✅ Found {workout_count} workout plans")
        
        cursor.execute("SELECT COUNT(*) FROM nutrition_plans")
        nutrition_count = cursor.fetchone()[0]
        print(f"✅ Found {nutrition_count} nutrition plans")
        
        # Sample data
        if workout_count > 0:
            cursor.execute("""
                SELECT id, user_id, created_by, modified_by, state 
                FROM workout_plans 
                LIMIT 3
            """)
            print("\n📋 Sample workout plans:")
            for row in cursor.fetchall():
                print(f"  - Plan {row[0]}: user={row[1]}, created_by={row[2]}, modified_by={row[3]}, state={row[4]}")
        
        if nutrition_count > 0:
            cursor.execute("""
                SELECT id, user_id, created_by, modified_by, state 
                FROM nutrition_plans 
                LIMIT 3
            """)
            print("\n🥗 Sample nutrition plans:")
            for row in cursor.fetchall():
                print(f"  - Plan {row[0]}: user={row[1]}, created_by={row[2]}, modified_by={row[3]}, state={row[4]}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Plan Traceability & State Migration Script")
    print("=" * 70)
    
    # Step 1: Backup
    backup_database()
    
    # Step 2: Migrate
    migrate_database()
    
    # Step 3: Verify
    verify_migration()
    
    print("\n" + "=" * 70)
    print("Migration complete!")
    print(f"Backup saved to: {BACKUP_PATH}")
    print("=" * 70)
    print("\n💡 Now you can:")
    print("  - Track who created/modified plans")
    print("  - See plan states (draft, approved, active, completed)")
    print("  - Clients create plans, trainers approve/modify them")
