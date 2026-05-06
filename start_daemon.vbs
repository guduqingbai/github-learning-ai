' 启动星期八自主思考守护进程（无窗口后台运行）
' ⚠️ 安全警告：本脚本创建无窗口后台常驻进程，可通过 Windows 计划任务实现开机自启。
' 使用 `taskkill /F /IM pythonw.exe` 停止所有后台进程。
' 由 Windows 计划任务调用，保证持久化运行

Dim fso, shell, scriptDir, pythonw, scriptPath, flagFile
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' 脚本所在目录作为项目根目录
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Python 路径（假设 pythonw 在 PATH 中，或者与项目同盘）
pythonw = "pythonw"

' 守护进程脚本路径（相对于脚本目录）
scriptPath = scriptDir & "\thinking_daemon.py"

' 运行标志文件（防重复启动）
flagFile = scriptDir & "\data\daemon_running.flag"

' 检查是否已经在运行
Dim flagExists
flagExists = fso.FileExists(flagFile)

If flagExists Then
    Dim processList, isRunning
    isRunning = False
    processList = shell.Exec("tasklist /FI ""IMAGENAME eq pythonw.exe"" /NH").StdOut.ReadAll
    If InStr(processList, "pythonw.exe") > 0 Then
        isRunning = True
    End If

    If isRunning Then
        WScript.Quit 0
    End If
End If

' 创建标志文件
Dim outFile
Set outFile = fso.CreateTextFile(flagFile, True)
outFile.WriteLine("running")
outFile.Close

' 启动 pythonw 无窗口运行
shell.Run chr(34) & pythonw & chr(34) & " " & chr(34) & scriptPath & chr(34), 0, False
