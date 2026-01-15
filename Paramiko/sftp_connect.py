import paramiko

tran = paramiko.Transport(('192.168.56.123', 22))
tran.connect(username='zzy', password='123456qwer')
sftp = paramiko.SFTPClient.from_transport(tran)

sftp.get('/startup.cfg', 'startup.cfg')
sftp.put('startup.cfg', '/test.cfg')

tran.close()