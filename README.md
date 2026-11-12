# Solverse PDF Tools

A small Windows app for merging and splitting PDFs from the File Explorer right-click menu. It runs on your PC, needs no account or internet connection, and does not upload your files or send telemetry.

Website and download: [pdf-tools.awaisnazir.tech](https://pdf-tools.awaisnazir.tech)
Latest release: v2.0.0 (about 35 MB installer)

## What it does

**Merge.** Select two to six PDFs in File Explorer, right-click and choose Merge PDFs. The files open in one window where you can drag rows into the order you want, or add more files up to the six-file limit. Click Merge PDFs and choose where to save the result.

**Split.** Right-click a single PDF, choose Split PDF and set how many pages each part should have.

On Windows 11 the commands may be under "Show more options".

## Install

1. Download `PDF_Tools_Setup_v2.0.0.exe` from the [website](https://pdf-tools.awaisnazir.tech/download/) or the [latest release](https://github.com/Awais-Nazir/SOLVERSE-PDF_tools/releases/latest).
2. Run the installer and follow the wizard. You don't need Python.

The installer isn't code signed yet, so Windows SmartScreen may show an "unrecognized app" warning. Each release lists a SHA256 checksum you can compare against before running it. There's a [step-by-step guide](https://pdf-tools.awaisnazir.tech/guides/windows-smartscreen-checksum/) for that.

## Limits

- Merge takes two to six files at a time.
- Password-protected PDFs aren't supported. Unlock them first.
- Windows 10 or 11, 64-bit.

## Uninstall

Open Settings, then Apps, then Installed apps, find Solverse PDF Tools and choose Uninstall. This also removes the File Explorer menu entries.

## Built with

Python, Tkinter, PyPDF2, PyInstaller and Inno Setup.

## License

The source is available under a custom non-commercial license. It's free for personal, educational and other non-commercial use. Commercial use needs permission from the author. See [LICENSE](LICENSE).
