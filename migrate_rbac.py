"""
Database migration script to add role-based access control fields.

This script:
1. Backs up the current database
2. Adds roles column (default ["client"])
3. Adds trainer_id and nutritionist_id columns
4. Updates existing users with default CLIENT role

Run this script before starting the application with the new RBAC system.
"""

import sqlite3
import shutil
from datetime import datetime
import os

DB_PATH = "fitness_agent.db"
BACKUP_PATH = f"fitness_agent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def backup_database():
    """Create a backup of the current database"""
    if os.path.exists(DB_PATH):
        print(f"Creating backup: {BACKUP_PATH}")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created successfully")
    else:
        print(f"⚠️  No existing database found at {DB_PATH}")


def migrate_database():
    """Add RBAC columns to existing database"""
    print(f"\nMigrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add roles column if it doesn't exist
        if 'roles' not in columns:
            print("Adding 'roles' column...")
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN roles TEXT DEFAULT '["client"]'
            ''')
            
            # Update existing users with default client role
            cursor.execute('''
                UPDATE users 
                SET roles = '["client"]'
                WHERE roles IS NULL
            ''')
            print("✅ Added 'roles' column")
        else:
            print("⏭️  'roles' column already exists")
        
        # Add trainer_id column if it doesn't exist
        if 'trainer_id' not in columns:
            print("Adding 'trainer_id' column...")
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN trainer_id TEXT
            ''')
            print("✅ Added 'trainer_id' column")
        else:
            print("⏭️  'trainer_id' column already exists")
        
        # Add nutritionist_id column if it doesn't exist
        if 'nutritionist_id' not in columns:
            print("Adding 'nutritionist_id' column...")
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN nutritionist_id TEXT
            ''')
            print("✅ Added 'nutritionist_id' column")
        else:
            print("⏭️  'nutritionist_id' column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(users)")
        print("\nUpdated users table schema:")
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
    print("\nVerifying migration...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Found {user_count} users in database")
        
        # Check for roles
        cursor.execute("SELECT id, username, roles FROM users LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            print("\nSample user data:")
            for user_id, username, roles in users:
                print(f"  - {username} ({user_id}): roles = {roles}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("RBAC Database Migration Script")
    print("=" * 60)
    
    # Step 1: Backup
    backup_database()
    
    # Step 2: Migrate
    migrate_database()
    
    # Step 3: Verify
    verify_migration()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print(f"Backup saved to: {BACKUP_PATH}")
    print("=" * 60)
