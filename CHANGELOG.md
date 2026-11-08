# Changelog

## v2.0.0

- Fixed [issue #2](https://github.com/Awais-Nazir/SOLVERSE-PDF_tools/issues/2): selecting two to six PDFs in File Explorer and choosing **Merge PDFs** opens one window containing the entire selection.
- Review and reorder files before merging. Selections above six show a limit message.
- Packaged the Tcl/Tk runtime with both apps and applied the PDF Tools icon to their windows and executables.

## v1.1.0
- Major startup performance improvements using PyInstaller `--onedir`
- Added tiny launcher executables for instant context-menu response
- Background worker threads to keep UI responsive during operations
- Determinate, stage-based progress bars for merge and split tools
- Lazy imports for heavy PDF libraries to reduce initial load time
- Improved logging and graceful shutdown handling
- UX polish and internal codebase cleanup

## v1.0.1
- Improved installer upgrade behavior
- Prevented duplicate Windows context menu entries on reinstall
- Ensured registry keys are properly cleaned on uninstall
- Minor stability and reliability improvements

## v1.0.0
- Initial release
- PDF merge via context menu
- PDF split via context menu
- Windows installer with auto cleanup

## [v1.2.0] - 2026-04-16

### Fixed
- Fixed blurry UI on Windows HiDPI displays (Thanks @YinkaiYu!)

### Contributors
- @YinkaiYu - HiDPI display fix
