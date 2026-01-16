import subprocess
import sys
import os

def main():
    # Folder where the launcher EXE lives
    base_dir = os.path.dirname(sys.executable)

    # Path to the real merge app
    app_path = os.path.join(base_dir, "merge_app.exe")

    # Forward selected PDF arguments
    args = sys.argv[1:]

    # Launch the real app (non-blocking, fast)
    subprocess.Popen(
        [app_path] + args,
        close_fds=True
    )

if __name__ == "__main__":
    main()
