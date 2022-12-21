;--------------------------------
; Includes

  !include "MUI2.nsh"
  !include "logiclib.nsh"


;--------------------------------
; Custom defines
  !define NAME "OpenBB Terminal"
  !define COMPANY "OpenBB"
  !define APPFILE "OpenBBTerminal.exe"
  !define VERSION "2.1.0"
  !define SLUG "${NAME} v${VERSION}"

;--------------------------------
; General
  Name "${NAME}"
  OutFile "${NAME} Setup.exe"
  InstallDir $PROFILE\OpenBB
  RequestExecutionLevel user

;--------------------------------
; UI

  !define MUI_ICON "assets\openbb_icon.ico"
  !define MUI_UNICON "assets\openbb_icon.ico"
  !define MUI_HEADERIMAGE
  !define MUI_WELCOMEFINISHPAGE_BITMAP "assets\installer_vertical2.bmp"
  !define MUI_HEADERIMAGE_BITMAP "assets\installer_horizontal.bmp"
  !define MUI_ABORTWARNING
  !define MUI_WELCOMEPAGE_TITLE "${SLUG} Setup"

;--------------------------------
; Pages

  ; Installer pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "license.txt"
;  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  ; Uninstaller pages
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

  ; Set UI language
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Section - Install App

  Section "-hidden app"
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "app\*.*"
    WriteRegStr HKCU "Software\${NAME}" "" $INSTDIR
    WriteUninstaller "$INSTDIR\Uninstall.exe"
  SectionEnd


;--------------------------------
; Section - Shortcut

  Section "Desktop Shortcut" DeskShort
    CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${APPFILE}"
	CreateDirectory '$SMPROGRAMS\${Company}\${NAME}'
    CreateShortCut '$SMPROGRAMS\${Company}\${NAME}\${NAME}.lnk' '$INSTDIR\${APPFILE}' "" '$INSTDIR\${APPFILE}' 0
    CreateShortCut '$SMPROGRAMS\${Company}\${NAME}\Uninstall ${NAME}.lnk' '$INSTDIR\Uninstall.exe' "" '$INSTDIR\Uninstall.exe' 0
  SectionEnd


;--------------------------------
; Remove empty parent directories

  Function un.RMDirUP
    !define RMDirUP '!insertmacro RMDirUPCall'

    !macro RMDirUPCall _PATH
          push '${_PATH}'
          Call un.RMDirUP
    !macroend

    ; $0 - current folder
    ClearErrors

    Exch $0
    ;DetailPrint "ASDF - $0\.."
    RMDir "$0\.."

    IfErrors Skip
    ${RMDirUP} "$0\.."
    Skip:

    Pop $0

  FunctionEnd

;--------------------------------
; Section - Uninstaller

Section "Uninstall"

  ;Delete Shortcut
  Delete "$DESKTOP\${NAME}.lnk"

  ;Delete Directory
  Delete '$SMPROGRAMS\${Company}\${NAME}'

  ;Delete Uninstall
  Delete "$INSTDIR\Uninstall.exe"

  ;Delete Folder
  RMDir /r "$INSTDIR"
  ${RMDirUP} "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\${NAME}"

SectionEnd
