

Page Custom muiExtraPages_Create

!include "FileFunc.nsh"

var IntroText
var InstallationLink
var ExampleImg
var ExampleImgCtl
var PARENTDIR

Function muiExtraPages_Create
    Push $0

    !insertmacro MUI_HEADER_TEXT_PAGE \
        "${PRODUCT_NAME}" \
        "Installation Successfully Complete"

    ${GetParent} "$INSTDIR" $PARENTDIR

    nsDialogs::Create /NOUNLOAD 1018
    ${NSD_CreateLabel} 10u 10u 280u 40u "Click the link below to open the installation folder:"
    Pop $IntroText

    ${NSD_CreateLink} 10u 55u 200u 10u $PARENTDIR
    Pop $InstallationLink
    ${NSD_OnClick} $InstallationLink LaunchLinkOne

    nsDialogs::CreateControl STATIC ${WS_VISIBLE}|${WS_CHILD}|${WS_CLIPSIBLINGS}|${SS_BITMAP}|${SS_REALSIZECONTROL} 0 10u 90u 280u 40u ""
    Pop $ExampleImgCtl
    StrCpy $0 $PLUGINSDIR\openbb_win.png
    System::Call 'user32::LoadImage(i 0, t r0, i ${IMAGE_BITMAP}, i 0, i 0, i ${LR_LOADFROMFILE}|${LR_LOADTRANSPARENT}|${LR_LOADMAP3DCOLORS}) i.s'
    Pop $ExampleImg
    SendMessage $ExampleImgCtl ${STM_SETIMAGE} ${IMAGE_BITMAP} $ExampleImg

    nsDialogs::Show

    System::Call 'gdi32:DeleteObject(i $ExampleImg)'

    Pop $0
FunctionEnd

!define MUI_FINISHPAGE_TEXT "Select a resource to open.$\r$\n$\r$\n"
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "OpenBB Platform Documentation"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLinkTwo"
!define MUI_PAGE_CUSTOMFUNCTION_SHOW MyFinishShow
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE MyFinishLeave

var CheckboxLinkThree
var CheckboxLinkFour

Function LaunchLinkOne
    ExecShell "open" "$PARENTDIR"
FunctionEnd

Function LaunchLinkTwo
    ExecShell "open" "https://docs.openbb.co/platform"
FunctionEnd

Function MyFinishShow
    ${NSD_CreateCheckbox} 120u 110u 100% 10u "OpenBB CLI Documentation"
    Pop $CheckboxLinkThree
    ${NSD_Check} $CheckboxLinkThree
    SetCtlColors $CheckboxLinkThree "" "ffffff"

    ${NSD_CreateCheckbox} 120u 130u 100% 10u "OpenBB Pro Documentation"
    Pop $CheckboxLinkFour
    ${NSD_Check} $CheckboxLinkFour
    SetCtlColors $CheckboxLinkFour "" "ffffff"
FunctionEnd

Function MyFinishLeave
    ${NSD_GetState} $CheckboxLinkThree $0
    ${If} $0 <> 0
        ExecShell "open" "https://docs.openbb.co/cli"
    ${EndIf}

    ${NSD_GetState} $CheckboxLinkFour $0
    ${If} $0 <> 0
        ExecShell "open" "https://docs.openbb.co/pro"
    ${EndIf}
FunctionEnd

!insertmacro MUI_PAGE_FINISH