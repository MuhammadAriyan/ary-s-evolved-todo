"""Drop foreign key constraint from tasks table."""
import psycopg2
from app.config import settings

def drop_foreign_key():
    """Drop the tasks_user_id_fkey constraint."""
    try:
        # Connect to database
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()

        # Drop the foreign key constraint
        print("Dropping foreign key constraint 'tasks_user_id_fkey'...")
        cursor.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;")

        conn.commit()
        print("✅ Foreign key constraint dropped successfully!")

        # Verify the constraint is gone
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'tasks' AND constraint_type = 'FOREIGN KEY';
        """)
        remaining_fks = cursor.fetchall()

        if remaining_fks:
            print(f"⚠️ Remaining foreign key constraints: {remaining_fks}")
        else:
            print("✅ No foreign key constraints remain on tasks table")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    drop_foreign_key()
