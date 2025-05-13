; TraderAdmin Windows Installer Script
; Created for Plan 7: Deployment Preparation, Packaging & Windows Installer

!include "MUI2.nsh"

; General Configuration
Name "TraderAdmin"
OutFile "TraderAdmin_Setup.exe"
Unicode True

; Default installation directory
InstallDir "$PROGRAMFILES64\TraderAdmin"

; Request application privileges for Windows
RequestExecutionLevel admin

; Variables
Var StartMenuFolder

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME

; License page - only include if license file exists
!ifdef LICENSE_FILE
  !insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!else
  ; Check if license file exists
  !tempfile TEMPFILE
  !system 'IF EXIST "..\LICENSE" ECHO !define LICENSE_FILE "..\LICENSE" > "${TEMPFILE}"'
  !include "${TEMPFILE}"
  !delfile "${TEMPFILE}"

  ; Include license page if license file exists
  !ifdef LICENSE_FILE
    !insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
  !endif
!endif

!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Folder Selection
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\TraderAdmin"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"

    ; Add files to install
    File "..\build\bin\TraderAdmin.exe"

    ; Create config directory if needed
    CreateDirectory "$INSTDIR\config"

    ; Check and handle optional files
    !tempfile TEMPLICENSE
    !system 'IF EXIST "..\LICENSE" ECHO !define LICENSE_EXISTS 1 > "${TEMPLICENSE}"'
    !include "${TEMPLICENSE}"
    !delfile "${TEMPLICENSE}"
    !ifdef LICENSE_EXISTS
      File "..\LICENSE"
    !endif

    !tempfile TEMPCONFIG
    !system 'IF EXIST "..\config.yaml.example" ECHO !define CONFIG_EXISTS 1 > "${TEMPCONFIG}"'
    !include "${TEMPCONFIG}"
    !delfile "${TEMPCONFIG}"
    !ifdef CONFIG_EXISTS
      File "..\config.yaml.example"
    !endif

    !tempfile TEMPREADME
    !system 'IF EXIST "..\README.md" ECHO !define README_EXISTS 1 > "${TEMPREADME}"'
    !include "${TEMPREADME}"
    !delfile "${TEMPREADME}"
    !ifdef README_EXISTS
      File "..\README.md"
    !endif

    !tempfile TEMPCONFIG2
    !system 'IF EXIST "..\CONFIGURATION.md" ECHO !define CONFIGMD_EXISTS 1 > "${TEMPCONFIG2}"'
    !include "${TEMPCONFIG2}"
    !delfile "${TEMPCONFIG2}"
    !ifdef CONFIGMD_EXISTS
      File "..\CONFIGURATION.md"
    !endif

    ; Write the uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Start Menu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
        CreateShortcut "$SMPROGRAMS\$StartMenuFolder\TraderAdmin.lnk" "$INSTDIR\TraderAdmin.exe"
        CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END

    ; Desktop shortcut
    CreateShortcut "$DESKTOP\TraderAdmin.lnk" "$INSTDIR\TraderAdmin.exe"

    ; Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "DisplayName" "TraderAdmin - Trading Platform"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "DisplayIcon" "$INSTDIR\TraderAdmin.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "Publisher" "Your Organization"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "URLInfoAbout" "https://github.com/yourusername/IBKR-trader"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin" "NoRepair" 1
SectionEnd

; Uninstaller
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\TraderAdmin.exe"
    Delete "$INSTDIR\config.yaml.example"
    Delete "$INSTDIR\config.toml.example"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\CONFIGURATION.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\Uninstall.exe"

    ; Remove directories
    RMDir /r "$INSTDIR\config"
    RMDir "$INSTDIR"

    ; Remove Start Menu items
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\TraderAdmin.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"

    ; Remove Desktop shortcut
    Delete "$DESKTOP\TraderAdmin.lnk"

    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TraderAdmin"
    DeleteRegKey HKLM "Software\TraderAdmin"
SectionEnd
