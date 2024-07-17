Set objShell = CreateObject("WScript.Shell")
sDesktopPath = objShell.SpecialFolders("Desktop")

' Create shortcut for openbb-cli
Set objShortcut = objShell.CreateShortcut(sDesktopPath & "\openbb-cli.lnk")
objShortcut.TargetPath = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\Scripts\openbb-cli.exe"
objShortcut.IconLocation = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\assets\openbb.ico"
objShortcut.Description = "OpenBB CLI launcher"
objShortcut.Save

' Create shortcut for openbb-api
Set objShortcut = objShell.CreateShortcut(sDesktopPath & "\openbb-api.lnk")
objShortcut.TargetPath = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\Scripts\openbb-api.exe"
objShortcut.IconLocation = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\assets\openbb.ico"
objShortcut.Description = "OpenBB API launcher"
objShortcut.Save
