# coding:utf-8
"""
@DateTime: 	2017-09-24 14:26:31
@Version: 	1.0
@Author: 	Unnamed_Max
"""
import socket
import struct
import operator
import time
import os
import csv

import AES

# 实现下载功能
def download(sock):
    # 从服务端接收文件列表
    filelist = sock.recv(1024).decode()
    if operator.eq(filelist, ''):
        print('没有可以下载的文件')
    print(filelist)
    # 从用户中输入接收文件名，并发送给服务端
    filename = input('请输入要下载的文件名:\n')
    sock.send(filename.encode())
    # 获取包大小，并解压
    FILEINFO_SIZE = struct.calcsize('128sI')
    try:
        fhead = sock.recv(1024)
        fhead = sock.recv(FILEINFO_SIZE)
        filename, filesize = struct.unpack('128sI', fhead)
        # 接收文件
        with open('new_' + filename.decode().strip('\00'), 'wb') as f:
            ressize = filesize
            while True:
                if ressize > 1024:
                    filedata = sock.recv(1024)
                else:
                    filedata = sock.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize < 0:
                    break
        print('文件传输成功!')
    except Exception as e:
        print(e)
        print('文件传输失败!')


# 实现上传功能
def index_upload(sock, key):
    # 获取文件路径，并将文件信息打包发送给服务端
    path = input('请输入要上传的索引表：')
    filename = os.path.basename(path)
    # 将文件基本信息（文件名和文件大小）打包传送，pack中第一个参数指定了数据格式，最后pack会将数据都转换为字节流形式返回
    fhead = struct.pack('128sI128s', filename.encode(), os.stat(path).st_size, bytes('NULL', encoding='utf-8'))
    sock.send(fhead)
    # 传送文件
    with open(path, 'rb') as f:  # 'rb'表示以字节流的形式读出
        while True:
            filedata = f.read(1024)
            if not filedata:
                break
            sock.send(filedata)
    print('索引文件传输结束\n')


def file_upload(sock, key):
    path = input('请输入要上传的文件路径：')
    fn = os.path.basename(path)
    en_fn = AES.encrypt(fn, key)
    with open('D:\\Fuzzy Keywords Search\\plaintext_index.csv', 'r') as f:
        re = csv.DictReader(f)
        for item in re:
            if item['Title'] == fn:
                fid = item['FID']
    en_fid = AES.encrypt(fid, key)
    fhead = struct.pack('128sI128s', en_fn.encode(), os.stat(path).st_size, en_fid.encode())
    sock.send(fhead)
    # 传送文件
    with open(path, 'r') as f:
        fc = f.read()
        en_fc = AES.encrypt(fc, key)
        sock.send(en_fc.encode())
    print('文件:{}传输成功'.format(fn))

def handle(sock, key):
    while True:
        order = input()
        if operator.eq(order, '1'):
            sock.send(order.encode())
            download(sock)
        elif operator.eq(order, '2'):
            sock.send(order.encode())
            index_upload(sock, key)
        elif operator.eq(order, '3'):
            sock.send(order.encode())
            file_upload(sock, key)
            # with open(path, 'r') as f:
            #     reader = csv.DictReader(f)
            #     for item in reader:
            #         adr = item['Path']
            #         fn = item['Title']
            #         en_fn = AES.encrypt(fn, key)
            #         fid = item['FID']
            #         en_fid = AES.encrypt(fid, key)
            #         sock.send('3'.encode())
            #         file_upload(adr, fn, en_fn, en_fid, sock, key)
        elif operator.eq(order, '4'):
            print('正在关闭连接...')
            time.sleep(0.5)
            sock.send(order.encode())
            break
        else:
            print('命令错误,请重新输入！')
            continue
        line = sock.recv(1024)
        print(line.decode())


if __name__ == '__main__':
    # 建立socket并连接8002端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8002))
    line = sock.recv(1024)
    print(line.decode())
    key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'
    order = input()
    handle(sock, key)
    sock.close()
