[Setup]
AppName=PDF Tools
AppVersion=1.0
DefaultDirName={pf}\PDF Tools
DefaultGroupName=PDF Tools
UninstallDisplayIcon={app}\merge_pdfs.exe
OutputDir=.
OutputBaseFilename=PDF_Tools_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "merge_pdfs.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "split_pdf.exe"; DestDir: "{app}"; Flags: ignoreversion
; Optional icon
Source: "logo.ico"; DestDir: "{app}"

[Registry]
; ===== Merge PDFs Context Menu =====
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: ""; ValueData: "Merge PDFs"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\logo.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs\command"; ValueType: string; ValueName: ""; ValueData: """{app}\merge_pdfs.exe"" ""%1"" ""%2"""; Flags: uninsdeletekey

; ===== Split PDF Context Menu =====
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: ""; ValueData: "Split PDF"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\logo.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF\command"; ValueType: string; ValueName: ""; ValueData: """{app}\split_pdf.exe"" ""%1"""; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"


