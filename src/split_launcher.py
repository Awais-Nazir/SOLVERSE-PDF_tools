import subprocess
import sys
import os

def main():
    base_dir = os.path.dirname(sys.executable)
    app_path = os.path.join(base_dir, "split_app.exe")

    args = sys.argv[1:]

    subprocess.Popen(
        [app_path] + args,
        close_fds=True
    )

if __name__ == "__main__":
    main()
