import paramiko
import time

with paramiko.client.SSHClient() as client:
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    client.connect("192.168.56.123", 22, "zzy", "123456qwer")
    with client.invoke_shell() as shell:
        shell.send("screen-length disable\n")
        shell.send("show current-configuration\n")
        time.sleep(2)
        output = shell.recv(65535).decode('utf-8')
        print(output)
