#!/usr/bin/env python3
"""
Postgres-native migration to add:
1) bookings.license_document_url (TEXT)
2) cars.documents (JSONB)

Uses DATABASE_URL to connect. Safe to run multiple times (IF NOT EXISTS).

Usage:
  - Dry run (default):
      python scripts/pg_migrate_dl_and_documents.py
  - Apply changes:
      python scripts/pg_migrate_dl_and_documents.py --apply

Requires: psycopg (v3) package. Install with: pip install "psycopg[binary]"
"""

import os
import sys
import argparse


DDL_STATEMENTS = [
    # Add license document URL to bookings
    """
    ALTER TABLE IF EXISTS bookings
    ADD COLUMN IF NOT EXISTS license_document_url TEXT;
    """,
    # Add documents JSONB to cars
    """
    ALTER TABLE IF EXISTS cars
    ADD COLUMN IF NOT EXISTS documents JSONB;
    """,
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Execute DDL against DATABASE_URL")
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not args.apply:
        print("-- Dry run --\n")
        print("Planned DDL statements:")
        for stmt in DDL_STATEMENTS:
            print(stmt.strip(), end="\n\n")
        if database_url:
            print("DATABASE_URL is set; re-run with --apply to execute.")
        else:
            print("DATABASE_URL is not set. Set it and re-run with --apply to execute against your Postgres.")
        return 0

    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        return 1

    try:
        import psycopg
    except Exception as e:
        print("ERROR: psycopg is not installed. Install with: pip install 'psycopg[binary]'", file=sys.stderr)
        return 1

    print("Connecting to Postgres...")
    with psycopg.connect(database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            for stmt in DDL_STATEMENTS:
                ddl = stmt.strip()
                print(f"Executing: {ddl}")
                cur.execute(ddl)

        # Verify columns exist
        with conn.cursor() as cur:
            print("\nVerifying columns...")
            cur.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'bookings' AND column_name = 'license_document_url'
                """
            )
            bookings_col = cur.fetchone()
            print("bookings.license_document_url:", bookings_col or "NOT FOUND")

            cur.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'cars' AND column_name = 'documents'
                """
            )
            cars_col = cur.fetchone()
            print("cars.documents:", cars_col or "NOT FOUND")

    print("\n✓ Migration completed and verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

