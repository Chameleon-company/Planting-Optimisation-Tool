import subprocess
import time
import sys
import os
import http.client

# Colors for terminal output
BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def run_module(module_name):
    """Runs a python module using uv."""
    print(f"{GREEN} Running {module_name}...{NC}")
    subprocess.run(["uv", "run", "python", "-m", module_name], check=True)


def wait_for_api(url="127.0.0.1", port=8080, timeout=15):
    """Checks if API is up without using external tools."""
    print(f"Waiting for API to respond on port {port}...")
    for i in range(timeout):
        try:
            conn = http.client.HTTPConnection(url, port)
            conn.request("GET", "/")
            response = conn.getresponse()
            if response.status == 200:
                print(f"{GREEN}API is up!{NC}")
                return True
        except Exception:
            pass
        time.sleep(1)
        print(".", end="", flush=True)
    return False


def main():
    print(f"{BLUE}===================================================={NC}")
    print(f"{BLUE} Starting Database Initialization{NC}")
    print(f"{BLUE}===================================================={NC}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["NO_COLOR"] = "1"
    env["TERM"] = "dumb"

    with open("api_log.txt", "w", encoding="utf-8") as log_file:
        api_proc = subprocess.Popen(
            [
                "uv",
                "run",
                "python",
                "-m",
                "uvicorn",
                "src.main:app",
                "--port",
                "8080",
                "--host",
                "127.0.0.1",
            ],
            stdout=log_file,
            stderr=log_file,
            text=True,
            env=env,
            start_new_session=True,
        )

    try:
        if not wait_for_api():
            print(f"\n{RED}Error: API failed to start. Check api_log.txt{NC}")
            api_proc.terminate()
            sys.exit(1)

        run_module("src.scripts.import_species")
        run_module("src.scripts.import_farms")
        run_module("src.scripts.import_boundaries")
        run_module("src.scripts.import_species_parameters")

    except subprocess.CalledProcessError as e:
        print(f"{RED}Ingestion failed during: {e}{NC}")
        sys.exit(1)
    finally:
        print(
            f"\n{BLUE}Shutting down background API handle (PID: {api_proc.pid})...{NC}"
        )
        api_proc.terminate()
        api_proc.wait()

    print(f"{BLUE}===================================================={NC}")
    print(f"{GREEN} SUCCESS: Database is fully populated{NC}")
    print(f"{BLUE}===================================================={NC}")


if __name__ == "__main__":
    main()
