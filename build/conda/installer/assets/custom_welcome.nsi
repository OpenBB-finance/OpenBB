# Below is an example of creating multiple pages after the welcome page of the installer.
#
# This file contains code that is inserted where the @CUSTOM_WELCOME_FILE@ is located
# in the main.nsi.tmpl. The main mechanism for extra pages occurs with the
# "Page Custom muiExtraPagesAfterWelcome_Create" line, which
# references the function "muiExtraPagesAfterWelcome_Create" for page creation.

!define MUI_PAGE_CUSTOMFUNCTION_PRE SkipPageIfUACInnerInstance
!insertmacro MUI_PAGE_WELCOME

Page Custom muiExtraPagesAfterWelcome_Create

var IntroAfterWelcomeText
var InstallationAfterWelcomeLink
var ExampleAfterWelcomeImg
var ExampleImgAfterWelcomeCtl

Function muiExtraPagesAfterWelcome_Create
    Push $0

    !insertmacro MUI_HEADER_TEXT_PAGE \
        "${PRODUCT_NAME}" \
        "Welcome to OpenBB Platform Installer"

    nsDialogs::Create /NOUNLOAD 1018
    ${NSD_CreateLabel} 10u 10u 280u 120u "Welcome to the OpenBB Platform Installer.$\r$\n$\r$\nThis application will install the latest version of the OpenBB Platform on your computer as a self-contained, Python 3.12, Conda environment.$\r$\n$\r$\nIn order to install you need access to the Internet.$\r$\n$\r$\nInstallation requires between 1-2 GB of storage space, with a minimum of 4GB RAM.$\r$\n$\r$\nWhen a non-default installation path is chosen, it requires a depth of two - i.e, User/MyUserAccount/OpenBB/conda, where OpenBB is the target folder, and conda is the name of the folder where Conda and the installed environments live. The path, including username, should not contain any spaces."
    Pop $IntroAfterWelcomeText

    nsDialogs::CreateControl STATIC ${WS_VISIBLE}|${WS_CHILD}|${WS_CLIPSIBLINGS}|${SS_BITMAP}|${SS_REALSIZECONTROL} 0 10u 90u 280u 40u ""
    Pop $ExampleImgAfterWelcomeCtl
    StrCpy $0 $PLUGINSDIR\openbb_win.png
    System::Call 'user32::LoadImage(i 0, t r0, i ${IMAGE_BITMAP}, i 0, i 0, i ${LR_LOADFROMFILE}|${LR_LOADTRANSPARENT}|${LR_LOADMAP3DCOLORS}) i.s'
    Pop $ExampleAfterWelcomeImg
    SendMessage $ExampleImgAfterWelcomeCtl ${STM_SETIMAGE} ${IMAGE_BITMAP} $ExampleAfterWelcomeImg

    nsDialogs::Show

    System::Call 'gdi32:DeleteObject(i $ExampleAfterWelcomeImg)'

    Pop $0
FunctionEnd