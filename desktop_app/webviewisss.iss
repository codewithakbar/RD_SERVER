[Setup]
AppName=WebViewApp
AppVersion=1.0
DefaultDirName={pf}\WebViewApp
DefaultGroupName=WebViewApp
OutputBaseFilename=WebViewAppInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\webview_app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "create_startup_shortcut.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WebViewApp"; Filename: "{app}\webview_app.exe"
Name: "{group}\{cm:UninstallProgram,WebViewApp}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\webview_app.exe"; Description: "{cm:LaunchProgram,WebViewApp}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\create_startup_shortcut.py"; Description: "Create Startup Shortcut"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
