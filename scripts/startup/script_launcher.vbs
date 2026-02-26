Option Explicit
Dim fso, scriptDir, root, pyw
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
root = fso.GetAbsolutePathName(fso.BuildPath(scriptDir, "..\.."))
pyw = fso.BuildPath(root, ".venv\Scripts\pythonw.exe")
If Not fso.FileExists(pyw) Then pyw = fso.BuildPath(root, "venv\Scripts\pythonw.exe")
If Not fso.FileExists(pyw) Then
  MsgBox "錯誤：找不到虛擬環境(.venv/venv)。請在專案根目錄執行：uv venv && uv pip install -e .", 16, "Script Launcher"
  WScript.Quit 1
End If

Dim shell, cmd
Set shell = CreateObject("WScript.Shell")
Dim q
q = Chr(34)
cmd = q & pyw & q & " " & q & fso.BuildPath(root, "script_launcher.py") & q
shell.Run cmd, 0, False
