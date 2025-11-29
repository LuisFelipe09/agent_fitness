"""
Database migration script to add authentication columns to users table.

This script adds:
- password_hash column (for web/JWT authentication)
- email column (for user identification and password reset)

Supports both SQLite (development) and PostgreSQL (production).

Run with:
    python migrations/migrate_auth_columns.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_settings
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL


def get_engine():
    """Create database engine based on environment"""
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        return create_engine(DATABASE_URL)


def column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database():
    """Add authentication columns to users table"""
    print("=" * 70)
    print("Authentication Columns Migration")
    print("=" * 70)
    print(f"\nDatabase URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if columns exist
                password_hash_exists = column_exists(engine, 'users', 'password_hash')
                email_exists = column_exists(engine, 'users', 'email')
                
                print("\nCurrent schema status:")
                print(f"  - password_hash column: {'✅ EXISTS' if password_hash_exists else '❌ MISSING'}")
                print(f"  - email column: {'✅ EXISTS' if email_exists else '❌ MISSING'}")
                
                # Add password_hash column if it doesn't exist
                if not password_hash_exists:
                    print("\n📝 Adding 'password_hash' column...")
                    if DATABASE_URL.startswith("sqlite"):
                        conn.execute(text("""
                            ALTER TABLE users
                            ADD COLUMN password_hash VARCHAR
                        """))
                    else:
                        conn.execute(text("""
                            ALTER TABLE users
                            ADD COLUMN password_hash VARCHAR
                        """))
                    print("  ✅ Added 'password_hash' column")
                else:
                    print("\n  ⏭️  'password_hash' column already exists")
                
                # Add email column if it doesn't exist
                if not email_exists:
                    print("\n📝 Adding 'email' column...")
                    # SQLite doesn't support adding UNIQUE constraint directly
                    conn.execute(text("""
                        ALTER TABLE users
                        ADD COLUMN email VARCHAR
                    """))
                    
                    # Create unique index on email for both SQLite and PostgreSQL
                    try:
                        conn.execute(text("""
                            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users (email)
                        """))
                        print("  ✅ Added 'email' column with unique constraint")
                    except Exception as e:
                        print(f"  ✅ Added 'email' column")
                        print(f"  ⚠️  Could not create unique index: {e}")
                else:
                    print("\n  ⏭️  'email' column already exists")
                
                # Commit transaction
                trans.commit()
                
                print("\n✅ Migration completed successfully!")
                
                # Verify migration
                print("\n🔍 Verifying migration...")
                inspector = inspect(engine)
                columns = {col['name'] for col in inspector.get_columns('users')}
                
                if 'password_hash' in columns and 'email' in columns:
                    print("  ✅ All authentication columns present")
                    print("\nUpdated users table columns:")
                    for col in inspector.get_columns('users'):
                        print(f"  - {col['name']}: {col['type']}")
                else:
                    print("  ❌ Verification failed!")
                    
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Migration failed: {e}")
                print("\nPlease check your database connection and permissions.")
                raise
                
    except Exception as e:
        print(f"\n❌ Could not connect to database: {e}")
        raise
    finally:
        engine.dispose()
    
    print("\n" + "=" * 70)
    print("Migration complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        migrate_database()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        sys.exit(1)
