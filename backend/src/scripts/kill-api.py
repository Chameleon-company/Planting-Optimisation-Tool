import os
import signal
import psutil


def kill_process_on_port(port):
    found = False
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            connections = proc.net_connections(kind="inet")
            for conn in connections:
                if conn.laddr.port == port:
                    print(
                        f"Stopping API process {proc.info['pid']} ({proc.info['name']}) on port {port}..."
                    )
                    if os.name == "nt":  # Windows
                        os.kill(proc.info["pid"], signal.SIGTERM)
                    else:  # Linux/WSL
                        os.kill(proc.info["pid"], signal.SIGKILL)
                    found = True
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error):
            continue

    if not found:
        print(f"No process found running on port {port}.")


if __name__ == "__main__":
    kill_process_on_port(8080)
