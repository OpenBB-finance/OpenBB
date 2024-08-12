Set objShell = CreateObject("WScript.Shell")
sdesktopPath = objShell.SpecialFolders("Desktop")
shortcutFolder = sdesktopPath & "\OpenBB Shortcuts"

Set objFSO = CreateObject("Scripting.FileSystemObject")
If Not objFSO.FolderExists(shortcutFolder) Then
    objFSO.CreateFolder(shortcutFolder)
End If

prefixPath = objShell.ExpandEnvironmentStrings("%PREFIX%")
userProfilePath = objShell.ExpandEnvironmentStrings("%USERPROFILE%")

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

CreateShortcut "OpenBB CLI", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB API", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB Notebook", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB IPython", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB Updater", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB CMD", "C:\Windows\System32\cmd.exe", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB User Settings", userProfilePath & "\.openbb_platform", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "OpenBB User Data", userProfilePath & "\OpenBBUserData", prefixPath & "\assets\openbb_icon.ico"
CreateShortcut "Uninstall", prefixPath & "\Uninstall-OpenBB.exe", prefixPath & "\assets\openbb_icon.ico"

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB Notebook.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate " & prefixPath & "\envs\obb && cd " & userProfilePath & " && jupyter-notebook"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB IPython.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate " & prefixPath & "\envs\obb && ipython -c ""from openbb import obb;obb"" -i"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB API.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate " & prefixPath & "\envs\obb && openbb-api --login"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save


Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB Updater.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate " & prefixPath & "\envs\obb && poetry lock && poetry install && python -c ""import openbb; openbb.build()"" && echo OpenBB has been updated. Press any key to exit. && pause >nul && exit"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB CMD.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate base"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save

Set objShortcut = objShell.CreateShortcut(shortcutFolder & "\OpenBB CLI.lnk")
objShortcut.Arguments = "/k PATH " & prefixPath & ";" & prefixPath & "\Scripts;" & prefixPath & "\Library\bin;%PATH% && source activate " & prefixPath & "\envs\obb && openbb"
objShortcut.WorkingDirectory = prefixPath
objShortcut.Save