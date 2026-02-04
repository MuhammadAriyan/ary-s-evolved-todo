#!/usr/bin/env python3
"""
Create Better Auth tables in Neon DB
"""
import psycopg2
from psycopg2 import sql

# Neon DB connection string
DATABASE_URL = "postgresql://neondb_owner:npg_0KDmVR2YcuvT@ep-autumn-lake-a8rjwnlv-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def create_better_auth_tables():
    """Create all Better Auth required tables with proper camelCase columns"""

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        # Drop existing tables if they exist
        print("Dropping existing tables if they exist...")
        cur.execute('DROP TABLE IF EXISTS "verification" CASCADE;')
        cur.execute('DROP TABLE IF EXISTS "account" CASCADE;')
        cur.execute('DROP TABLE IF EXISTS "session" CASCADE;')
        cur.execute('DROP TABLE IF EXISTS "user" CASCADE;')

        # Create user table
        print("Creating user table...")
        cur.execute('''
            CREATE TABLE "user" (
                "id" TEXT PRIMARY KEY,
                "email" TEXT UNIQUE NOT NULL,
                "emailVerified" BOOLEAN DEFAULT FALSE,
                "name" TEXT,
                "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "image" TEXT
            );
        ''')

        # Create session table
        print("Creating session table...")
        cur.execute('''
            CREATE TABLE "session" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL,
                "expiresAt" TIMESTAMP NOT NULL,
                "token" TEXT UNIQUE NOT NULL,
                "ipAddress" TEXT,
                "userAgent" TEXT,
                "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
            );
        ''')

        # Create account table
        print("Creating account table...")
        cur.execute('''
            CREATE TABLE "account" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL,
                "accountId" TEXT NOT NULL,
                "providerId" TEXT NOT NULL,
                "accessToken" TEXT,
                "refreshToken" TEXT,
                "idToken" TEXT,
                "expiresAt" TIMESTAMP,
                "password" TEXT,
                "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE,
                UNIQUE("providerId", "accountId")
            );
        ''')

        # Create verification table
        print("Creating verification table...")
        cur.execute('''
            CREATE TABLE "verification" (
                "id" TEXT PRIMARY KEY,
                "identifier" TEXT NOT NULL,
                "value" TEXT NOT NULL,
                "expiresAt" TIMESTAMP NOT NULL,
                "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Create indexes
        print("Creating indexes...")
        cur.execute('CREATE INDEX "idx_session_userId" ON "session"("userId");')
        cur.execute('CREATE INDEX "idx_session_token" ON "session"("token");')
        cur.execute('CREATE INDEX "idx_account_userId" ON "account"("userId");')
        cur.execute('CREATE INDEX "idx_verification_identifier" ON "verification"("identifier");')

        # Commit changes
        conn.commit()
        print("\n✅ Successfully created all Better Auth tables in Neon DB!")

        # Verify tables were created
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('user', 'session', 'account', 'verification')
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        print(f"\nCreated tables: {[t[0] for t in tables]}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_better_auth_tables()
