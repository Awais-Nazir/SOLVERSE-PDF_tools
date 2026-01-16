[Setup]
AppId={{707E5943-BA2E-4120-9EE5-3B3DE4112D8B}}
AppName=PDF Tools
AppVersion=1.1.0
AppVerName=PDF Tools v1.1.0

VersionInfoVersion=1.1.0.0
VersionInfoCompany=Muhammad Awais Nazir
VersionInfoDescription=PDF Merge & Split Tools for Windows
VersionInfoCopyright=© 2025 Muhammad Awais Nazir

DefaultDirName={pf}\PDF Tools
DefaultGroupName=PDF Tools
UninstallDisplayIcon={app}\installer_icon.ico
OutputDir=.
OutputBaseFilename=PDF_Tools_Setup_v1.1.0.0
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
Source: "merge_pdfs\*"; DestDir: "{app}\merge_pdf"; Flags: recursesubdirs createallsubdirs

; ===== Split PDF Tool (onedir) =====
Source: "split_pdf\*"; DestDir: "{app}\split_pdf"; Flags: recursesubdirs createallsubdirs

; Installer icon
Source: "installer_icon.ico"; DestDir: "{app}"


[Registry]
; ===== Merge PDFs Context Menu =====
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: ""; ValueData: "Merge PDFs"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergePDFs\command"; ValueType: string; ValueName: ""; ValueData: """{app}\merge_pdf\merge_pdfs.exe"" ""%1"" ""%2"""; Flags: uninsdeletekey

; ===== Split PDF Context Menu =====
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: ""; ValueData: "Split PDF"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\installer_icon.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\SplitPDF\command"; ValueType: string; ValueName: ""; ValueData: """{app}\split_pdf\split_pdf.exe"" ""%1"""; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}"


