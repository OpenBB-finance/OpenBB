Set objShell = CreateObject("WScript.Shell")
sdesktopPath = objShell.SpecialFolders("Desktop")

Set fso = CreateObject("Scripting.FileSystemObject")
prefixPath = objShell.ExpandEnvironmentStrings("%PREFIX%")
userProfilePath = objShell.ExpandEnvironmentStrings("%USERPROFILE%")
currentPath = fso.GetAbsolutePathName(prefixPath)
parentFolder = fso.GetParentFolderName(currentPath)
shortcutFolder = parentFolder

Set objFSO = CreateObject("Scripting.FileSystemObject")
If Not objFSO.FolderExists(shortcutFolder) Then
    objFSO.CreateFolder(shortcutFolder)
End If

If prefixPath = "%PREFIX%" Or userProfilePath = "%USERPROFILE%" Then
    WScript.Echo "Environment variables %PREFIX% or %USERPROFILE% are not set correctly."
    WScript.Quit 1
End If

Sub CreateShortcut(name, targetPath, iconPath)
    Set objShell = CreateObject("WScript.Shell")
    Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\" & name & ".lnk")
    objShortcut.TargetPath = objShell.ExpandEnvironmentStrings(targetPath)
    objShortcut.IconLocation = objShell.ExpandEnvironmentStrings(iconPath)
    objShortcut.Description = name
    objShortcut.Save
End Sub

CreateShortcut "openbb-cli", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "openbb-api", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "openbb-notebook", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "openbb-ipython", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "Update", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "CMD", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "Environments", prefixPath & "\envs", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "Settings", userProfilePath & "\.openbb_platform", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBBUserData", userProfilePath & "\OpenBBUserData", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "Uninstall", prefixPath & "\Uninstall-OpenBB.exe", prefixPath & "\assets\openbb_icon.ico"

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\openbb-notebook.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate " & prefixPath & "\envs\obb && cd " & shortcutFolder & " && jupyter-notebook && exit"
objShortcut.WorkingDirectory = shortcutFolder
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\openbb-ipython.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate " & prefixPath & "\envs\obb && ipython -c ""from openbb import obb;obb"" -i"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\openbb-api.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate " & prefixPath & "\envs\obb && call openbb-api --login  && exit"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save


Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\Update.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate " & prefixPath & "\envs\obb && call openbb-update && exit"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\CMD.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate base && echo Conda base environment is active. Use this shell to create new environments. && echo To activate the OpenBB environment, run 'conda activate obb'."
objShortcut.WorkingDirectory = shortcutFolder
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\openbb-cli.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && activate " & prefixPath & "\envs\obb && call openbb && exit"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save