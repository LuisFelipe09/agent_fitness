"""
Database migration script to add plan context fields.

This script adds goal and target_activity_level columns to workout_plans
and nutrition_plans tables to capture what each plan was designed for.

This allows plans to preserve their original purpose even if the user's
profile goal/activity level changes later.

Run this before using the updated plan features.
"""

import sqlite3
import shutil
from datetime import datetime
import os

DB_PATH = "fitness_agent.db"
BACKUP_PATH = f"fitness_agent_backup_plan_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def backup_database():
    """Create a backup of the current database"""
    if os.path.exists(DB_PATH):
        print(f"Creating backup: {BACKUP_PATH}")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created successfully")
    else:
        print(f"⚠️  No existing database found at {DB_PATH}")


def migrate_database():
    """Add goal and target_activity_level columns to plan tables"""
    print(f"\nMigrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # === WORKOUT PLANS TABLE ===
        print("\n📋 Migrating workout_plans table...")
        cursor.execute("PRAGMA table_info(workout_plans)")
        workout_columns = [col[1] for col in cursor.fetchall()]
        
        # Add goal column
        if 'goal' not in workout_columns:
            print("  Adding 'goal' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN goal TEXT
            ''')
            print("  ✅ Added 'goal'")
        else:
            print("  ⏭️  'goal' already exists")
        
        # Add target_activity_level column
        if 'target_activity_level' not in workout_columns:
            print("  Adding 'target_activity_level' column...")
            cursor.execute('''
                ALTER TABLE workout_plans
                ADD COLUMN target_activity_level TEXT
            ''')
            print("  ✅ Added 'target_activity_level'")
        else:
            print("  ⏭️  'target_activity_level' already exists")
        
        # === NUTRITION PLANS TABLE ===
        print("\n🍎 Migrating nutrition_plans table...")
        cursor.execute("PRAGMA table_info(nutrition_plans)")
        nutrition_columns = [col[1] for col in cursor.fetchall()]
        
        # Add goal column
        if 'goal' not in nutrition_columns:
            print("  Adding 'goal' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN goal TEXT
            ''')
            print("  ✅ Added 'goal'")
        else:
            print("  ⏭️  'goal' already exists")
        
        # Add target_activity_level column
        if 'target_activity_level' not in nutrition_columns:
            print("  Adding 'target_activity_level' column...")
            cursor.execute('''
                ALTER TABLE nutrition_plans
                ADD COLUMN target_activity_level TEXT
            ''')
            print("  ✅ Added 'target_activity_level'")
        else:
            print("  ⏭️  'target_activity_level' already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        print("\nRestoring from backup...")
        conn.close()
        if os.path.exists(BACKUP_PATH):
            shutil.copy2(BACKUP_PATH, DB_PATH)
            print("✅ Database restored from backup")
        raise
    
    finally:
        conn.close()


def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check workout_plans table
    cursor.execute("PRAGMA table_info(workout_plans)")
    workout_columns = [col[1] for col in cursor.fetchall()]
    
    # Check nutrition_plans table
    cursor.execute("PRAGMA table_info(nutrition_plans)")
    nutrition_columns = [col[1] for col in cursor.fetchall()]
    
    conn.close()
    
    required_fields = ['goal', 'target_activity_level']
    workout_ok = all(field in workout_columns for field in required_fields)
    nutrition_ok = all(field in nutrition_columns for field in required_fields)
    
    if workout_ok and nutrition_ok:
        print("✅ All new columns verified in both tables")
        return True
    else:
        if not workout_ok:
            print(f"❌ Missing columns in workout_plans: {[f for f in required_fields if f not in workout_columns]}")
        if not nutrition_ok:
            print(f"❌ Missing columns in nutrition_plans: {[f for f in required_fields if f not in nutrition_columns]}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PLAN CONTEXT MIGRATION")
    print("=" * 60)
    print("\nThis migration adds 'goal' and 'target_activity_level' fields")
    print("to workout_plans and nutrition_plans tables.")
    print("\nThis allows plans to capture what they were optimized for,")
    print("even if the user's profile goal/activity level changes later.")
    
    backup_database()
    migrate_database()
    verify_migration()
    
    print("\n" + "=" * 60)
    print("Migration complete! You can now use the updated plan models.")
    print("=" * 60)
