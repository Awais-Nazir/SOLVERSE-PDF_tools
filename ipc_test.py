import time
from ipc_single_instance import (
    send_files_to_existing_instance,
    start_ipc_server
)

def on_files_received(files):
    print("📥 Received files:", files)


print("🚀 Starting IPC server...")
start_ipc_server(on_files_received)

print("🕒 Server running. Waiting for incoming messages...\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Server stopped.")
