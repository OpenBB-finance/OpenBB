use framework "Foundation"
use framework "AppKit"
use scripting additions

-- Get script location
tell application "Finder"
    set current_path to POSIX path of (container of (path to me) as alias)
end tell

-- Set OpenBB Terminal launcher icon in folder relative to script location
set sourcePath to current_path & "../../images/openbb.icns"
set destPath to current_path & "../../DMG/OpenBB Terminal/.OpenBB/OpenBBTerminal"
set imageData to (current application's NSImage's alloc()'s initWithContentsOfFile:sourcePath)
(current application's NSWorkspace's sharedWorkspace()'s setIcon:imageData forFile:destPath options:2)

-- Set OpenBB pywry icon relative to script location
set sourcePath to current_path & "../../images/openbb.icns"
set destPath to current_path & "../../DMG/OpenBB Terminal/.OpenBB/pywry"
set imageData to (current application's NSImage's alloc()'s initWithContentsOfFile:sourcePath)
(current application's NSWorkspace's sharedWorkspace()'s setIcon:imageData forFile:destPath options:2)
