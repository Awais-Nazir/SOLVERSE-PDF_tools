[Setup]
AppId={{707E5943-BA2E-4120-9EE5-3B3DE4112D8B}}
AppName=PDF Tools
AppVersion=1.0.1
AppVerName=PDF Tools v1.0.1

VersionInfoVersion=1.0.0.0
VersionInfoCompany=Muhammad Awais Nazir
VersionInfoDescription=PDF Merge & Split Tools for Windows
VersionInfoCopyright=© 2025 Muhammad Awais Nazir

DefaultDirName={pf}\PDF Tools
DefaultGroupName=PDF Tools
UninstallDisplayIcon={app}\logo.ico
OutputDir=.
OutputBaseFilename=PDF_Tools_Setup_v1.0.1.3
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
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: ""; ValueData: "Split PDFs"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\logo.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF\command"; ValueType: string; ValueName: ""; ValueData: """{app}\split_pdf.exe"" ""%1"""; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"


