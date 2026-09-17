Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Matheus\PycharmProjects\PythonProject\testes_oficiais\scripts e playbook - ansible\minerador_vagas"
WshShell.Run """C:\Users\Matheus\AppData\Local\Programs\Python\Python312\python.exe"" scheduler.py", 0, False