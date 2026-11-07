# build.py
import subprocess
import shutil
import os
from pathlib import Path

# Configuration
BUILD_CONFIGS = [
    {
        "name": "merge_app",
        "script": "./src/merge_app.py",
        "version_file": "./version_info-merge.txt",
        "dest_folder": "merge_pdfs",
    },
    {
        "name": "merge_launcher",
        "script": "./src/merge_launcher.py",
        "version_file": "./version_info-merge.txt",
        "dest_folder": "merge_pdfs",
    },
    {
        "name": "split_app",
        "script": "./src/split_app.py",
        "version_file": "./version_info-split.txt",  # adjust if different
        "dest_folder": "split_pdf",
    },
    {
        "name": "split_launcher",
        "script": "./src/split_launcher.py",
        "version_file": "./version_info-split.txt",  # adjust if different
        "dest_folder": "split_pdf",
    },
]

INSTALLER_DIR = Path("./installer-exe")
DIST_DIR = Path("./dist")
BUILD_DIR = Path("./build")


def clean_pyinstaller_cache():
    """Clean PyInstaller build artifacts and cache"""
    print("🧹 Cleaning PyInstaller cache and build artifacts...")

    # Remove dist folder
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("   ✅ Removed dist/")

    # Remove build folder
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print("   ✅ Removed build/")

    # Remove all .spec files in root directory
    spec_files = list(Path(".").glob("*.spec"))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"   ✅ Removed {spec_file.name}")

    if not spec_files:
        print("   ℹ️  No .spec files found")

    print("✅ PyInstaller cache cleaned\n")


def clean_installer_directory():
    """Clean installer-exe directory"""
    print("🧹 Cleaning installer directory...")
    if INSTALLER_DIR.exists():
        shutil.rmtree(INSTALLER_DIR)
        print("   ✅ Removed installer-exe/")
    INSTALLER_DIR.mkdir(parents=True)
    print("✅ Installer directory ready\n")


def build_exe(config):
    """Build a single .exe with PyInstaller"""
    print(f"🔨 Building {config['name']}...")

    cmd = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--version-file",
        config["version_file"],
        config["script"],
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Build failed for {config['name']}")
        print(result.stderr)
        return False

    print(f"✅ {config['name']} built successfully\n")
    return True


def copy_contents_to_installer_dir(config):
    """Copy contents (exe + _internal) from dist folder to installer directory"""
    src = DIST_DIR / config["name"]
    dest = INSTALLER_DIR / config["dest_folder"]

    if not src.exists():
        print(f"⚠️  Source not found: {src}")
        return False

    # Create destination if it doesn't exist
    dest.mkdir(parents=True, exist_ok=True)

    print(f"📦 Copying contents of {config['name']} to {dest}...")

    # Copy all contents from src to dest (flatten structure)
    for item in src.iterdir():
        dest_path = dest / item.name

        if item.is_dir():
            # For directories (like _internal), copy tree and overwrite
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(item, dest_path)
            print(f"   📁 Copied directory: {item.name}")
        else:
            # For files (like .exe), copy and overwrite
            shutil.copy2(item, dest_path)
            print(f"   📄 Copied file: {item.name}")

    print(f"✅ Contents copied to installer directory\n")
    return True


def compile_installer():
    """Run Inno Setup compiler"""
    inno_script = Path(
        "inno-compiler-files/installer_dir.iss"
    )  # adjust path to your .iss file

    if not inno_script.exists():
        print("⚠️  Inno Setup script not found, skipping compilation")
        return

    print("\n🔧 Compiling installer with Inno Setup...")

    # Adjust path to your ISCC.exe location
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

    result = subprocess.run(
        [iscc_path, str(inno_script)], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Installer compiled successfully!")
    else:
        print("❌ Installer compilation failed")
        print(result.stderr)


def main():
    print("=" * 60)
    print("SOLVERSE PDF TOOLS - BUILD AUTOMATION")
    print("=" * 60 + "\n")

    # Step 1: Clean PyInstaller cache (build, dist, .spec files)
    clean_pyinstaller_cache()

    # Step 2: Clean installer directory
    clean_installer_directory()

    # Step 3: Build all .exe files
    print("=" * 60)
    print("BUILDING EXECUTABLES")
    print("=" * 60 + "\n")

    for config in BUILD_CONFIGS:
        if not build_exe(config):
            print("\n❌ Build process failed. Stopping.")
            return 1

    # Step 4: Copy contents to installer directory
    print("=" * 60)
    print("ORGANIZING FOR INNO SETUP")
    print("=" * 60 + "\n")

    for config in BUILD_CONFIGS:
        if not copy_contents_to_installer_dir(config):
            print("\n⚠️  Copy process had issues.")
            return 1

    print("=" * 60)
    print("✅ BUILD COMPLETE!")
    print("=" * 60)
    print(f"\n📂 Installer files ready at: {INSTALLER_DIR.absolute()}")
    print(f"   📁 merge_pdfs: {(INSTALLER_DIR / 'merge_pdfs').absolute()}")
    print(f"   📁 split_pdf: {(INSTALLER_DIR / 'split_pdf').absolute()}")
    print("\n🚀 Next step: Run Inno Setup compiler")
    compile_installer()
    print("COMPILATION COMPLETE")

    return 0


if __name__ == "__main__":
    exit(main())
