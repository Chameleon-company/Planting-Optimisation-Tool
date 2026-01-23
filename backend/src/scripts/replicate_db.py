import os
import subprocess
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

CONTAINER_NAME = os.getenv("CONTAINER_NAME", "pot_postgres_db")
SOURCE_DB = os.getenv("POSTGRES_DB", "POT_db")
TEST_DB = "pot_test_db"
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")


def run_docker_psql(command, database="postgres"):
    docker_cmd = [
        "docker",
        "exec",
        "-i",
        CONTAINER_NAME,
        "psql",
        "-U",
        POSTGRES_USER,
        "-d",
        database,
        "-c",
        command,
    ]
    return subprocess.run(docker_cmd, capture_output=True, text=True, check=True)


def main():
    try:
        print(f"--- Synchronizing Test Database: {TEST_DB} ---")

        term_sql = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB}';"
        subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                CONTAINER_NAME,
                "psql",
                "-U",
                POSTGRES_USER,
                "-c",
                term_sql,
            ],
            capture_output=True,
        )

        run_docker_psql(f"DROP DATABASE IF EXISTS {TEST_DB};")
        run_docker_psql(f'CREATE DATABASE {TEST_DB} WITH TEMPLATE "{SOURCE_DB}";')

        sync_sql = """
        DO $$ 
        DECLARE r RECORD; 
        BEGIN 
            FOR r IN (SELECT table_name, column_name FROM information_schema.columns 
                      WHERE column_default LIKE 'nextval%' AND table_schema = 'public') 
            LOOP 
                EXECUTE 'SELECT setval(pg_get_serial_sequence(' || quote_literal(r.table_name) || ', ' || 
                        quote_literal(r.column_name) || '), COALESCE(MAX(' || quote_ident(r.column_name) || '), 1)) FROM ' || quote_ident(r.table_name); 
            END LOOP; 
        END $$;
        """
        run_docker_psql(sync_sql, database=TEST_DB)
        print("--- Database Replicated Successfully ---")

        print("--- Launching Pytest Suite ---")

        current_env = os.environ.copy()
        test_url = current_env.get("TEST_DATABASE_URL")
        if not test_url:
            test_url = f"postgresql://{POSTGRES_USER}@localhost:5432/{TEST_DB}"

        current_env["DATABASE_URL"] = test_url

        result = subprocess.run(["uv", "run", "pytest"], env=current_env, check=False)

        sys.exit(result.returncode)

    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error during DB replication:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
