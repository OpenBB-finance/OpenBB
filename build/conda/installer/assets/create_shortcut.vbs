Set objShell = CreateObject("WScript.Shell")
sDesktopPath = objShell.SpecialFolders("Desktop")

Set objShortcut = objShell.CreateShortcut(sDesktopPath & "\openbb.lnk")

objShortcut.TargetPath = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\Scripts\openbb.exe"
objShortcut.IconLocation = objShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\openbb\assets\openbb.ico"
objShortcut.Description = "OpenBB launcher"
objShortcut.Save
