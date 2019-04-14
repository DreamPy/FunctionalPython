# coding: utf-8

import paramiko
import re
from time import sleep
import warnings
import os

warnings.filterwarnings("ignore")


# 定义一个类，表示一台远端linux主机
class Linux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password, timeout=30):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.try_times = 3
        self.transport = None
        self.chan = None
        self.ssh = None
        self.ftp = None

    # 调用该方法连接远程主机
    def connect(self):
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                self.transport = paramiko.Transport(sock=(self.ip, 22))
                self.transport.connect(username=self.username, password=self.password)
                self.chan = self.transport.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print(u'连接%s成功' % self.ip)
                # 接收到的网络数据解码为str
                print(self.chan.recv(65535).decode('utf-8'))
                self.ssh = paramiko.SSHClient()
                self.ssh._transport = self.transport
                self.ssh.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                self.ftp = self.ssh.open_sftp()
                return
            # 这里不对可能的异常如socket.error, socket.timeout细化，直接一网打尽
            except Exception as e:
                if self.try_times != 0:
                    print(u'连接%s失败，进行重试' % self.ip)
                    self.try_times -= 1
                else:
                    print(u'重试3次失败，结束程序')
                    exit(1)

    # 断开连接
    def close(self):
        self.ssh.close()
        self.chan.close()
        self.transport.close()

    # 发送要执行的命令
    def raw_send(self, cmd):
        cmd += '\r'
        # 通过命令执行提示符来判断命令是否执行完成
        p = re.compile(r':~$')

        result = ''
        # 发送要执行的命令
        self.chan.send(cmd)
        # 回显很长的命令可能执行较久，通过循环分批次取回回显
        while True:
            sleep(0.5)
            ret = self.chan.recv(65535)
            ret = ret.decode('utf-8')
            yield ret

    def exec(self, cmd):
        return self.ssh.exec_command(cmd, get_pty=True)

    def get(self, remote_file, local_file, override=True):
        if override:
            os.remove(local_file)
        return self.ftp.get(remote_file, local_file)

    def put(self, local_file, remote_file):
        return self.ftp.put(local_file, remote_file)

    def gets(self, remote_dir, local_path, override=True):
        pass


if __name__ == '__main__':
    host = Linux('192.168.100.131', 'lixu', '1')
    host.connect()
    stdin, stdout, stderr = host.exec('ls -R grakn|awk \'{print i$0}\' i=`pwd`\'/\'')

    ls = stdout.read().decode('utf-8')
    print(ls.split('\r\n'))
    # print(stderr.read())
