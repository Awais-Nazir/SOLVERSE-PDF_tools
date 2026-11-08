#if !FileExists("..\installer-exe\merge_pdfs\_internal\_tcl_data\init.tcl") || !FileExists("..\installer-exe\merge_pdfs\_internal\_tk_data\tk.tcl")
  #error Merge app is missing its Tcl/Tk runtime. Rebuild the installer payload first.
#endif
#if !FileExists("..\installer-exe\split_pdf\_internal\_tcl_data\init.tcl") || !FileExists("..\installer-exe\split_pdf\_internal\_tk_data\tk.tcl")
  #error Split app is missing its Tcl/Tk runtime. Rebuild the installer payload first.
#endif

[Setup]
AppId={{707E5943-BA2E-4120-9EE5-3B3DE4112D8B}}
AppName=PDF Tools
ChangesAssociations=yes
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
Source: "..\installer-exe\merge_pdfs\*"; DestDir: "{app}\merge_pdf"; Flags: ignoreversion recursesubdirs createallsubdirs
; ===== Split PDF Tool (onedir) =====
Source: "..\installer-exe\split_pdf\*"; DestDir: "{app}\split_pdf"; Flags: ignoreversion recursesubdirs createallsubdirs
; Installer icon
Source: "installer_icon.ico"; DestDir: "{app}"

[Registry]
; Explorer activates DropTarget with one IDataObject containing this selection.
; Remove the old command subkey on upgrade so it cannot launch once per file.
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; Flags: deletekey uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: ""; ValueData: "Merge PDFs"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs\DropTarget"; ValueType: string; ValueName: "CLSID"; ValueData: "{{C25FF893-9205-476D-8249-930868447218}"

; Local server runs outside Explorer. Register the COM class in both registry views.
#define MergeClass "CLSID\{{C25FF893-9205-476D-8249-930868447218}"
Root: HKCR; Subkey: "{#MergeClass}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "{#MergeClass}\LocalServer32"; ValueType: string; ValueName: ""; ValueData: """{app}\merge_pdf\merge_launcher.exe"""
Root: HKCR; Subkey: "{#MergeClass}\PythonCOM"; ValueType: string; ValueName: ""; ValueData: "__main__.MergeDropTarget"
Root: HKCR64; Subkey: "{#MergeClass}"; Flags: uninsdeletekey; Check: IsWin64
Root: HKCR64; Subkey: "{#MergeClass}\LocalServer32"; ValueType: string; ValueName: ""; ValueData: """{app}\merge_pdf\merge_launcher.exe"""; Check: IsWin64
Root: HKCR64; Subkey: "{#MergeClass}\PythonCOM"; ValueType: string; ValueName: ""; ValueData: "__main__.MergeDropTarget"; Check: IsWin64

; ── Split PDF Context Menu ────────────────────────────────────────────────
; Split always operates on one file — %1 and no MultiSelectModel needed.
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; Flags: deletekey uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: ""; ValueData: "Split PDF"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF\command"; ValueType: string; ValueName: ""; ValueData: """{app}\split_pdf\split_launcher.exe"" ""%1"""; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
