import sys

import psutil


def is_api_process(proc):
    cmdline = " ".join(proc.info["cmdline"] or []).lower()
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


def kill_process_on_port(port):
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port != port:
                    continue
                if not is_api_process(proc):
                    print(f"WARNING: port {port} is in use by {proc.info['name']} (pid {proc.info['pid']}) - skipping.")
                    return
                target = proc.parent() if proc.parent() and "fastapi" in " ".join(proc.parent().cmdline()).lower() else proc
                print(f"Stopping API on port {port} (pid {target.pid})...")
                target_proc = psutil.Process(target.pid)
                for child in target_proc.children(recursive=True):
                    child.kill()
                target_proc.kill()
                return
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error):
            continue
    print(f"No process found on port {port}.")


if __name__ == "__main__":
    kill_process_on_port(int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
