import http.client
import os
import subprocess
import sys
import time

import psutil

# Colors for terminal output
BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def run_module(module_name):
    """Runs a python module using uv."""
    print(f"{GREEN} Running {module_name}...{NC}")
    subprocess.run(["uv", "run", "python", "-m", module_name], check=True)


def is_api_process(proc):
    cmdline = " ".join(proc.cmdline() or []).lower()
    if "uvicorn" in cmdline or "fastapi" in cmdline:
        return True
    try:
        parent = proc.parent()
        if parent:
            parent_cmdline = " ".join(parent.cmdline() or []).lower()
            return "uvicorn" in parent_cmdline or "fastapi" in parent_cmdline
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return False


def handle_port(port):
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port != port:
                    continue
                if not is_api_process(proc):
                    print(f"{RED}Error: port {port} is in use by another process ({proc.info['name']}).{NC}")
                    print(f"{RED}Run 'just populate <port>' with a free port. Set API_PORT=<port> in your .env to avoid passing the flag each time.{NC}")
                    sys.exit(1)
                target = proc.parent() if proc.parent() and "fastapi" in " ".join(proc.parent().cmdline()).lower() else proc
                print(f"Stopping API on port {port} (pid {target.pid})...")
                target_proc = psutil.Process(target.pid)
                for child in target_proc.children(recursive=True):
                    child.kill()
                target_proc.kill()
                time.sleep(1)
                return
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error):
            continue


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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv("API_PORT", "8080"))
    os.environ["API_PORT"] = str(port)

    handle_port(port)

    print(f"{BLUE}===================================================={NC}")
    print(f"{BLUE} Starting Database Initialization{NC}")
    print(f"{BLUE}===================================================={NC}")

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["NO_COLOR"] = "1"
    env["TERM"] = "dumb"
    env["RATELIMIT_ENABLED"] = "false"

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
                str(port),
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
        if not wait_for_api(port=port):
            print(f"\n{RED}Error: API failed to start. Check api_log.txt{NC}")
            api_proc.terminate()
            sys.exit(1)

        run_module("src.scripts.import_species")
        run_module("src.scripts.import_farms")
        run_module("src.scripts.import_boundaries")
        run_module("src.scripts.import_species_parameters")
        run_module("src.scripts.import_dem")
        run_module("src.scripts.import_species_exclusion_rules")
        run_module("src.scripts.import_species_dependencies")

    except subprocess.CalledProcessError as e:
        print(f"{RED}Ingestion failed during: {e}{NC}")
        sys.exit(1)
    finally:
        print(f"\n{BLUE}Shutting down background API handle (PID: {api_proc.pid})...{NC}")
        api_proc.terminate()
        api_proc.wait()

    print(f"{BLUE}===================================================={NC}")
    print(f"{GREEN} SUCCESS: Database is fully populated{NC}")
    print(f"{BLUE}===================================================={NC}")


if __name__ == "__main__":
    main()
