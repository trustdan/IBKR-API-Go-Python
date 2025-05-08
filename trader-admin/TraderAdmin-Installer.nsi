; TraderAdmin NSIS Installer Script
; Author: IBKR Auto Trader Team

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"
!include "WinVer.nsh"

; Define application name and other constants
!define APPNAME "TraderAdmin"
!define COMPANYNAME "IBKR Auto Trader"
!define DESCRIPTION "Configuration management GUI for IBKR Auto Trader"
!define VERSION "1.0.0"
!define INSTALLDIR "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"
!define REGKEY "Software\${COMPANYNAME}\${APPNAME}"

; Set installer attributes
Name "${APPNAME}"
OutFile "${APPNAME}-Setup-${VERSION}.exe"
InstallDir "${INSTALLDIR}"
InstallDirRegKey HKLM "${REGKEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; Show version info
VIProductVersion "${VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "${APPNAME}"
VIAddVersionKey /LANG=1033 "CompanyName" "${COMPANYNAME}"
VIAddVersionKey /LANG=1033 "FileDescription" "${DESCRIPTION}"
VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "© ${COMPANYNAME}"

; Initialize variables for system checks
Var Dialog
Var DockerCheckLabel
Var KubeCheckLabel
Var TWSCheckLabel
Var DockerStatus
Var KubeStatus
Var TWSStatus
Var InstallAllowed

; Modern UI configuration
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\win.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\win.bmp"
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
Page custom SystemChecksPage SystemChecksPageLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; System Checks Page
Function SystemChecksPage
    !insertmacro MUI_HEADER_TEXT "System Requirements Check" "Verifying Docker, Kubernetes, and TWS availability"

    nsDialogs::Create 1018
    Pop $Dialog

    ${If} $Dialog == error
        Abort
    ${EndIf}

    ${NSD_CreateLabel} 0 0 100% 20u "Checking system requirements..."
    Pop $0

    ${NSD_CreateLabel} 10 30 100% 20u "Docker Desktop:"
    Pop $0
    ${NSD_CreateLabel} 120 30 100% 20u "Checking..."
    Pop $DockerCheckLabel

    ${NSD_CreateLabel} 10 50 100% 20u "Kubernetes:"
    Pop $0
    ${NSD_CreateLabel} 120 50 100% 20u "Checking..."
    Pop $KubeCheckLabel

    ${NSD_CreateLabel} 10 70 100% 20u "Trader Workstation:"
    Pop $0
    ${NSD_CreateLabel} 120 70 100% 20u "Checking..."
    Pop $TWSCheckLabel

    ${NSD_CreateLabel} 0 100 100% 40u "Note: Docker Desktop with Kubernetes and Interactive Brokers Trader Workstation are required for the full functionality of TraderAdmin."
    Pop $0

    nsDialogs::Show

    ; Check Docker status
    StrCpy $DockerStatus "Not Available"
    StrCpy $KubeStatus "Not Available"
    StrCpy $TWSStatus "Not Available"
    StrCpy $InstallAllowed "0"

    ; Run checks in the background
    ExecWait 'powershell.exe -command "try { docker ps >$null 2>&1; if ($?) { exit 0 } else { exit 1 } } catch { exit 1 }"' $0
    ${If} $0 == 0
        StrCpy $DockerStatus "Available"
        ${NSD_SetText} $DockerCheckLabel "Available ✓"
    ${Else}
        ${NSD_SetText} $DockerCheckLabel "Not Available ⚠"
    ${EndIf}

    ; Check Kubernetes status
    ExecWait 'powershell.exe -command "try { kubectl get nodes >$null 2>&1; if ($?) { exit 0 } else { exit 1 } } catch { exit 1 }"' $0
    ${If} $0 == 0
        StrCpy $KubeStatus "Available"
        ${NSD_SetText} $KubeCheckLabel "Available ✓"
    ${Else}
        ${NSD_SetText} $KubeCheckLabel "Not Available ⚠"
    ${EndIf}

    ; Check TWS/IB Gateway (check for process)
    ExecWait 'powershell.exe -command "if (Get-Process -Name Trader* -ErrorAction SilentlyContinue) { exit 0 } elseif (Get-Process -Name IB* -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"' $0
    ${If} $0 == 0
        StrCpy $TWSStatus "Running"
        ${NSD_SetText} $TWSCheckLabel "Running ✓"
    ${Else}
        ${NSD_SetText} $TWSCheckLabel "Not Running ⚠"
    ${EndIf}

    ; If at least Docker is available, allow installation
    ${If} $DockerStatus == "Available"
        StrCpy $InstallAllowed "1"
    ${EndIf}
FunctionEnd

Function SystemChecksPageLeave
    ${If} $InstallAllowed == "0"
        MessageBox MB_YESNO|MB_ICONEXCLAMATION "Docker Desktop is not running. TraderAdmin requires Docker Desktop to function properly. Do you want to continue anyway?" IDYES continue IDNO cancel
        cancel:
            Abort
        continue:
    ${EndIf}

    ; Warn about Kubernetes if not available
    ${If} $KubeStatus == "Not Available"
    ${AndIf} $InstallAllowed == "1"
        MessageBox MB_OK|MB_ICONINFORMATION "Kubernetes is not available. Please enable Kubernetes in Docker Desktop settings for full functionality."
    ${EndIf}

    ; Warn about TWS if not running
    ${If} $TWSStatus == "Not Running"
        MessageBox MB_OK|MB_ICONINFORMATION "Interactive Brokers Trader Workstation or Gateway is not currently running. You will need to start it before using TraderAdmin."
    ${EndIf}
FunctionEnd

Section "Install"
    SetOutPath "$INSTDIR"

    ; Add application files
    File /r "TraderAdmin\*.*"

    ; Copy the executable to the root install directory for easier shortcut creation
    SetOutPath "$INSTDIR"
    File "TraderAdmin\build\bin\TraderAdmin.exe"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortcut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\TraderAdmin.exe" "" "$INSTDIR\TraderAdmin.exe" 0

    ; Create desktop shortcut
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\TraderAdmin.exe" "" "$INSTDIR\TraderAdmin.exe" 0

    ; Write registry keys for uninstaller
    WriteRegStr HKLM "${REGKEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${REGKEY}" "Version" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\TraderAdmin.exe"

    ; Write Estimated Size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"

    ; Create application config directory
    CreateDirectory "$INSTDIR\config"

    ; Copy default config if available
    IfFileExists "python\config\config.toml" 0 +2
    CopyFiles "python\config\config.toml" "$INSTDIR\config\config.toml"
SectionEnd

Section "Uninstall"
    ; Ask about keeping configuration
    MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to keep your configuration files? Click Yes to keep configuration, No to remove all data." IDYES KeepConfig

    ; Delete configuration files if not keeping
    RMDir /r "$INSTDIR\config"

    KeepConfig:
    ; Remove application files
    RMDir /r "$INSTDIR\frontend"
    RMDir /r "$INSTDIR\build"
    Delete "$INSTDIR\TraderAdmin.exe"
    Delete "$INSTDIR\wails.json"
    Delete "$INSTDIR\*.dll"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"

    ; Remove Start Menu shortcuts
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"

    ; Remove Desktop shortcut
    Delete "$DESKTOP\${APPNAME}.lnk"

    ; Remove uninstaller
    Delete "$INSTDIR\Uninstall.exe"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "${REGKEY}"

    ; Remove install dir if empty
    RMDir "$INSTDIR"
    RMDir "$PROGRAMFILES64\${COMPANYNAME}"
SectionEnd

; Add a custom function to check Docker, Kubernetes status at startup
Function .onInit
    ; Ensure Windows 10 or newer
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK|MB_ICONEXCLAMATION "This application requires Windows 10 or newer."
        Abort
    ${EndIf}
FunctionEnd
