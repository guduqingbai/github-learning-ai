' 启动星期八自主思考守护进程（无窗口后台运行）
' 由 Windows 计划任务调用，保证持久化运行

Dim shell, pythonw, scriptPath, flagFile
Set shell = CreateObject("WScript.Shell")

' Python 路径
pythonw = "C:\Users\吴文豪\AppData\Local\Programs\Python\Python312\pythonw.exe"

' 守护进程脚本路径
scriptPath = "C:\Users\吴文豪\claude-code-projects\github-learning\thinking_daemon.py"

' 运行标志文件（防重复启动）
flagFile = "C:\Users\吴文豪\claude-code-projects\github-learning\daemon_running.flag"

' 检查是否已经在运行
Dim fso, flagExists
Set fso = CreateObject("Scripting.FileSystemObject")
flagExists = fso.FileExists(flagFile)

If flagExists Then
    ' 检查进程是否存在
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
