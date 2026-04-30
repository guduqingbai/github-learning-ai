Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
currentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
cmdLine = "cmd /c cd /d """ & currentPath & """ && python -m ai_knowledge_crawler"
WshShell.Run cmdLine, 0, False
WScript.Echo "AI知识爬虫已在后台启动"
