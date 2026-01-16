# Changelog

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
