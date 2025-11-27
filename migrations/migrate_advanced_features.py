"""
Database migration script to add advanced features tables.

This script adds:
- plan_versions table
- plan_comments table
- notifications table

Run this before using the advanced features.
"""

import sqlite3
import shutil
from datetime import datetime
import os

DB_PATH = "fitness_agent.db"
BACKUP_PATH = f"fitness_agent_backup_advanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def backup_database():
    """Create a backup of the current database"""
    if os.path.exists(DB_PATH):
        print(f"Creating backup: {BACKUP_PATH}")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created successfully")
    else:
        print(f"⚠️  No existing database found at {DB_PATH}")


def migrate_database():
    """Create new tables for advanced features"""
    print(f"\nMigrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # === PLAN VERSIONS TABLE ===
        print("\n📚 Creating plan_versions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_versions (
                id VARCHAR PRIMARY KEY,
                plan_id VARCHAR NOT NULL,
                plan_type VARCHAR NOT NULL,
                version_number INTEGER NOT NULL,
                created_by VARCHAR NOT NULL,
                created_at DATETIME NOT NULL,
                changes_summary TEXT,
                data_snapshot JSON NOT NULL,
                state_at_version VARCHAR NOT NULL
            )
        ''')
        # Add index manually if needed, though usually handled by ORM/DB
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_versions_plan_id ON plan_versions (plan_id)")
        print("  ✅ Created plan_versions table")
        
        # === PLAN COMMENTS TABLE ===
        print("\n💬 Creating plan_comments table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_comments (
                id VARCHAR PRIMARY KEY,
                plan_id VARCHAR NOT NULL,
                plan_type VARCHAR NOT NULL,
                author_id VARCHAR NOT NULL,
                author_role VARCHAR NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                edited_at DATETIME,
                is_internal BOOLEAN DEFAULT 0
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_comments_plan_id ON plan_comments (plan_id)")
        print("  ✅ Created plan_comments table")
        
        # === NOTIFICATIONS TABLE ===
        print("\n🔔 Creating notifications table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                related_entity_type VARCHAR,
                related_entity_id VARCHAR,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME NOT NULL,
                read_at DATETIME
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications (is_read)")
        print("  ✅ Created notifications table")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
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
        tables = ["plan_versions", "plan_comments", "notifications"]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' NOT found")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Advanced Features Database Migration Script")
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
