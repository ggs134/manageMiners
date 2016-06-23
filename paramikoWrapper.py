#!/usr/bin/python

from StringIO import StringIO
import paramiko

class SSHClient:
    "A wrapper of paramiko.SSHClient"
    TIMEOUT = 4

    def __init__(self, host, port, username, password, key=None, passphrase=None):
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key is not None:
            key = paramiko.RSAKey.from_private_key(StringIO(key), password=passphrase)
        self.client.connect(host, port, username=username, password=password, pkey=key, timeout=self.TIMEOUT)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(self, command, sudo=False):
        feed_password = False
        if sudo and self.username != "root":
            command = "sudo -S -p '' %s" % command
            feed_password = self.password is not None and len(self.password) > 0
        stdin, stdout, stderr = self.client.exec_command(command)
        if feed_password:
            stdin.write(self.password + "\n")
            stdin.flush()
        return {'out': stdout.readlines(),
                'err': stderr.readlines(),
                'retval': stdout.channel.recv_exit_status()}

if __name__ == '__main__':
    clientList = []
    resList = []
    for i in range(1,9):
        if i == 2:
            continue
        clientList.append(SSHCli("onther.iptime.org",50000+i,"miner"+str(i),"wjdtnsgud1!"))

    for cli in clientList:
        resList.append(cli.execute("tail -1 ethminer.err.log")["out"][0].strip("\n"))
        cli.close()

    print len(resList)
    for i in resList:
        print i

    # cli = SSHCli("onther.iptime.org",50001,"miner1","wjdtnsgud1!")
    # cli.execute("xinit")
    # cli.execute("aticonfig --od-enable", sudo=True)
    #res = cli.execute("aticonfig --list-adapters", sudo=True)
    # res = cli.execute("aticonfig --odgt --adapter=all", sudo=True)
    # res = cli.execute
    # print res["out"]
