import socket
import json
import threading
import logging

HOST = "127.0.0.1"
PORT = 65432


def log_ipc(msg):
    logging.info(f"[IPC] {msg}")


def send_files_to_existing_instance(files):
    """
    Returns True if an existing instance is running
    and files were successfully sent.
    """
    log_ipc(f"Attempting to forward files to existing instance: {files}")

    try:
        with socket.create_connection((HOST, PORT), timeout=0.3) as sock:
            payload = json.dumps({"files": files})
            sock.sendall(payload.encode("utf-8"))
            log_ipc("Files sent successfully to IPC server")
        return True

    except ConnectionRefusedError:
        log_ipc("Connection refused — no IPC server running")
    except socket.timeout:
        log_ipc("Connection timeout — IPC server not responding")
    except OSError as e:
        log_ipc(f"OS error during IPC send: {e}")

    return False


def start_ipc_server(on_files_received):
    """
    Starts IPC server and calls on_files_received(list)
    when new files arrive.
    """
    log_ipc("Attempting to start IPC server...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except OSError as e:
        log_ipc(f"Failed to bind IPC server (likely already running): {e}")
        raise

    server.listen()
    log_ipc(f"IPC server started successfully on {HOST}:{PORT}")

    def listen():
        log_ipc("IPC listener thread started — waiting for connections")

        while True:
            try:
                conn, addr = server.accept()
                log_ipc(f"IPC client connected from {addr}")

                with conn:
                    data = conn.recv(8192)

                    if not data:
                        log_ipc("Received empty IPC payload — ignoring")
                        continue

                    log_ipc(f"Received raw IPC data: {data!r}")

                    try:
                        payload = json.loads(data.decode("utf-8"))
                        files = payload.get("files", [])

                        log_ipc(f"Decoded IPC files: {files}")

                        if files:
                            on_files_received(files)
                            log_ipc("IPC files passed to application handler")
                        else:
                            log_ipc("IPC payload contained no files")

                    except json.JSONDecodeError as e:
                        log_ipc(f"Invalid IPC JSON payload: {e}")

            except Exception as e:
                log_ipc(f"Unhandled IPC server error: {e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

    return server
