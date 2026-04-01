import os
import signal
import sys

import psutil


def kill_process_on_port(port):
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port != port:
                    continue
                cmdline = " ".join(proc.info["cmdline"] or []).lower()
                if "uvicorn" not in cmdline and "fastapi" not in cmdline:
                    print(f"WARNING: port {port} is in use by {proc.info['name']} (pid {proc.info['pid']}) - skipping.")
                    return
                print(f"Stopping API on port {port} (pid {proc.info['pid']})...")
                os.kill(proc.info["pid"], signal.SIGTERM if os.name == "nt" else signal.SIGKILL)
                return
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error):
            continue
    print(f"No process found on port {port}.")


if __name__ == "__main__":
    kill_process_on_port(int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
