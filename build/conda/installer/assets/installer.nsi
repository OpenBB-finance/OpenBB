;--------------------------------
; Includes

  !include "MUI2.nsh"
  !include "logiclib.nsh"


#if enable_debugging is True
# Special logging build needed for ENABLE_LOGGING
# See https://nsis.sourceforge.io/Special_Builds
!define ENABLE_LOGGING=True
#endif

# Comes from https://nsis.sourceforge.io/Logging:Enable_Logs_Quickly
!define LogSet "!insertmacro LogSetMacro"
!macro LogSetMacro SETTING
  !ifdef ENABLE_LOGGING
    LogSet ${SETTING}
  !endif
!macroend

!define LogText "!insertmacro LogTextMacro"
!macro LogTextMacro INPUT_TEXT
  !ifdef ENABLE_LOGGING
    LogText ${INPUT_TEXT}
  !endif
!macroend

;--------------------------------
; Custom defines
  !define NAME "OpenBB Platform"
  !define COMPANY "OpenBB"
  !define VERSION "1.0.0"
  !define SLUG "${NAME} v${VERSION}"

;--------------------------------
; General
  Name "${NAME}"
  InstallDir "${PROFILE}\OpenBB"
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
  !define UninstId "OpenBBPlatform" ; You might want to use a GUID here

;--------------------------------
; Pages

  ; Installer pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "assets\installer_license.txt"
;  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  ; Uninstaller pages
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

  ; Set UI language
  !insertmacro MUI_LANGUAGE "English"


 ; Var /GLOBAL installerPath





; StrContains
; This function does a case sensitive searches for an occurrence of a substring in a string.
; It returns the substring if it is found.
; Otherwise it returns null("").
; Written by kenglish_hi
; Adapted from StrReplace written by dandaman32


Var STR_HAYSTACK
Var STR_NEEDLE
Var STR_CONTAINS_VAR_1
Var STR_CONTAINS_VAR_2
Var STR_CONTAINS_VAR_3
Var STR_CONTAINS_VAR_4
Var STR_RETURN_VAR

Function StrContains
  Exch $STR_NEEDLE
  Exch 1
  Exch $STR_HAYSTACK
  ; Uncomment to debug
  ;MessageBox MB_OK 'STR_NEEDLE = $STR_NEEDLE STR_HAYSTACK = $STR_HAYSTACK '
    StrCpy $STR_RETURN_VAR ""
    StrCpy $STR_CONTAINS_VAR_1 -1
    StrLen $STR_CONTAINS_VAR_2 $STR_NEEDLE
    StrLen $STR_CONTAINS_VAR_4 $STR_HAYSTACK
    loop:
      IntOp $STR_CONTAINS_VAR_1 $STR_CONTAINS_VAR_1 + 1
      StrCpy $STR_CONTAINS_VAR_3 $STR_HAYSTACK $STR_CONTAINS_VAR_2 $STR_CONTAINS_VAR_1
      StrCmp $STR_CONTAINS_VAR_3 $STR_NEEDLE found
      StrCmp $STR_CONTAINS_VAR_1 $STR_CONTAINS_VAR_4 done
      Goto loop
    found:
      StrCpy $STR_RETURN_VAR $STR_NEEDLE
      Goto done
    done:
   Pop $STR_NEEDLE ;Prevent "invalid opcode" errors and keep the
   Exch $STR_RETURN_VAR
FunctionEnd

!macro _StrContainsConstructor OUT NEEDLE HAYSTACK
  Push `${HAYSTACK}`
  Push `${NEEDLE}`
  Call StrContains
  Pop `${OUT}`
!macroend

!define StrContains '!insertmacro "_StrContainsConstructor"'


;-------------------------------
; Uninstall Previous Version if exists

!macro UninstallExisting exitcode uninstcommand
Push `${uninstcommand}`
Call UninstallExisting
Pop ${exitcode}
!macroend
Function UninstallExisting
Exch $1 ; uninstcommand
Push $2 ; Uninstaller
Push $3 ; Len
StrCpy $3 ""
StrCpy $2 $1 1
StrCmp $2 '"' qloop sloop
sloop:
	StrCpy $2 $1 1 $3
	IntOp $3 $3 + 1
	StrCmp $2 "" +2
	StrCmp $2 ' ' 0 sloop
	IntOp $3 $3 - 1
	Goto run
qloop:
	StrCmp $3 "" 0 +2
	StrCpy $1 $1 "" 1 ; Remove initial quote
	IntOp $3 $3 + 1
	StrCpy $2 $1 1 $3
	StrCmp $2 "" +2
	StrCmp $2 '"' 0 qloop
run:
	StrCpy $2 $1 $3 ; Path to uninstaller
	StrCpy $1 161 ; ERROR_BAD_PATHNAME
	GetFullPathName $3 "$2\.." ; $InstDir
	IfFileExists "$2" 0 +4
	ExecWait '"$2" /S _?=$3' $1 ; This assumes the existing uninstaller is a NSIS uninstaller, other uninstallers don't support /S nor _?=
	IntCmp $1 0 "" +2 +2 ; Don't delete the installer if it was aborted
	Delete "$2" ; Delete the uninstaller
	RMDir "$3" ; Try to delete $InstDir
	RMDir "$3\.." ; (Optional) Try to delete the parent of $InstDir
Pop $3
Pop $2
Exch $1 ; exitcode
FunctionEnd


Function .onInit
ReadRegStr $0 HKCU "Software\Software\Microsoft\Windows\CurrentVersion\Uninstall\${UninstId}" "UninstallString"
${If} $0 != ""
${AndIf} ${Cmd} `MessageBox MB_YESNO|MB_ICONQUESTION "It is highly recommended to uninstall the previous version of OpenBB Terminal - Please click Yes to proceed (Note - You will not lose your custom settings) - Or you can uninstall manually. " /SD IDYES IDYES`
	!insertmacro UninstallExisting $0 $0
	${If} $0 <> 0
		MessageBox MB_YESNO|MB_ICONSTOP "Failed to uninstall, continue anyway?" /SD IDYES IDYES +2
			Abort
	${EndIf}
${EndIf}
FunctionEnd

;--------------------------------
; Section - Install App

  Section "-hidden app"
    SectionIn RO
	${StrContains} $0 "\OpenBB" "$INSTDIR"
  ; Making sure here if user manually removes \openbb from their path that it still installs there
  ; so we dont have issues with uninstaller later.
	StrCmp $0 "" notfound
	  ; MessageBox MB_OK 'Found string $0  $INSTDIR'
	  SetOutPath "$INSTDIR"
	  Goto done
	notfound:
		; MessageBox MB_OK "$INSTDIR is 'bla'"
		SetOutPath "$INSTDIR\OpenBB"
		StrCpy $InstDir "$INSTDIR\OpenBB"
		; MessageBox MB_OK 'Did not find string   "$INSTDIR\OpenBB"  "$installerPath"'
	done:

    ; File /r "app\*.*"
    WriteRegStr HKCU "Software\${NAME}" "" $INSTDIR
    WriteUninstaller "$INSTDIR\Uninstall.exe"
	WriteRegStr HKCU "Software\Software\Microsoft\Windows\CurrentVersion\Uninstall\${UninstId}" "OpenBBPlatform" "OpenBB"
	WriteRegStr HKCU "Software\Software\Microsoft\Windows\CurrentVersion\Uninstall\${UninstId}" "UninstallString" '"$InstDir\Uninstall.exe"'
	WriteRegStr HKCU "Software\Software\Microsoft\Windows\CurrentVersion\Uninstall\${UninstId}" "QuietUninstallString" '"$InstDir\Uninstall.exe" /S'
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

  ;Delete Reg Key
  DeleteRegKey HKCU "Software\Software\Microsoft\Windows\CurrentVersion\Uninstall\${UninstId}"

  ;Delete Uninstall
  Delete "$INSTDIR\Uninstall.exe"


  ;Delete Folder
  RMDir /r "$INSTDIR"
  ${RMDirUP} "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\${NAME}"

SectionEnd