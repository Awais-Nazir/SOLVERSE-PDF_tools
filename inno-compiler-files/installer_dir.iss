[Setup]
AppId={{707E5943-BA2E-4120-9EE5-3B3DE4112D8B}}
AppName=PDF Tools
AppVersion=2.0.0
AppVerName=PDF Tools v2.0.0
VersionInfoVersion=2.0.0.0
VersionInfoCompany=Muhammad Awais Nazir
VersionInfoDescription=PDF Merge & Split Tools for Windows
VersionInfoCopyright=© 2025 Muhammad Awais Nazir
DefaultDirName={pf}\PDF Tools
DefaultGroupName=PDF Tools
UninstallDisplayIcon={app}\installer_icon.ico
OutputDir=.
OutputBaseFilename=PDF_Tools_Setup_v2.0.0
WizardStyle=modern
DisableWelcomePage=no
DisableProgramGroupPage=yes
AllowNoIcons=yes
SetupIconFile=installer_icon.ico
WizardImageFile=wizard_small.bmp
WizardSmallImageFile=installer_icon.bmp

[Messages]
WelcomeLabel1=Welcome to the PDF Tools Setup Wizard
WelcomeLabel2=This wizard will install PDF Tools on your computer.%n%nYou can merge and split PDF files directly from the Windows context menu.

[Files]
; ===== Merge PDF Tool (onedir) =====
Source: "..\installer-exe\merge_pdfs\*"; DestDir: "{app}\merge_pdf"; Flags: recursesubdirs createallsubdirs
; ===== Split PDF Tool (onedir) =====
Source: "..\installer-exe\split_pdf\*"; DestDir: "{app}\split_pdf"; Flags: recursesubdirs createallsubdirs
; Installer icon
Source: "installer_icon.ico"; DestDir: "{app}"

[Registry]
; ── Merge PDFs Context Menu ────────────────────────────────────────────────
;
; KEY FIXES vs previous version:
;   1. MultiSelectModel=Player  → tells Windows to launch the app ONCE with
;      ALL selected files, instead of once per file (Document model default).
;   2. %* in the command        → passes all selected file paths in one launch.
;      Previously "%1" "%2" only ever forwarded two files and still triggered
;      two separate launches because MultiSelectModel was missing.
;
; Delete the old key first so stale values ("%1" "%2" command) don't persist.
; The deletekey flag on the parent achieves this before writing new values.
; ──────────────────────────────────────────────────────────────────────────

; Delete old key entirely before writing (clears any stale command from prev install)
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; Flags: deletekey uninsdeletekey

; Re-create with correct values
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: ""; ValueData: "Merge PDFs"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"

; %* passes ALL selected PDF paths to a single launcher instance
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs\command"; ValueType: string; ValueName: ""; ValueData: """{app}\merge_pdf\merge_launcher.exe"" %*"; Flags: uninsdeletekey

; ── Split PDF Context Menu ────────────────────────────────────────────────
; Split always operates on one file — %1 and no MultiSelectModel needed.
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; Flags: deletekey uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: ""; ValueData: "Split PDF"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF\command"; ValueType: string; ValueName: ""; ValueData: """{app}\split_pdf\split_launcher.exe"" ""%1"""; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
