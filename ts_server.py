# coding:utf-8
'''
	@DateTime: 	2017-09-24 12:25:13
	@Version: 	1.0
	@Author: 	Unname_Max
'''
import threading
import socket
import time
import operator
import os
import struct
import csv
import random
import string

# 实现下载功能
def download(connect):
    # 获取文件目录
    files = os.listdir()
    # 用于传输文件目录的字符串
    liststr = ''
    # 将所有文件名传入字符串中
    for i in files:
        liststr += i + '\n'
    # 如果文件列表为空，将不继续执行下载任务
    if operator.eq(liststr, ''):
        connect.send(''.encode())
    # 如果文件列表不为空，开始下载任务
    else:
        # 向客户端传送文件列表
        connect.send(liststr.encode())
        while True:
            # 获取客户端要下载的文件名，如果不存在就继续输入
            filename = connect.recv(100).decode()
            if filename not in files:
                connect.send('文件不存在！'.encode())
            else:
                connect.send('开始文件传输！'.encode())
                break
        # 将文件信息打包发送给客服端
        fhead = struct.pack('128sI', filename.encode(), os.stat(filename).st_size)
        connect.send(fhead)
        # 传送文件信息
        with open(filename, 'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                connect.send(filedata)
        # 存储到日志中
        print('%s\n下载文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n下载文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('files')


# 实现上传功能
def upload(connect):
    FILEINFO_SIZE = struct.calcsize('128sI128s')
    try:
        # 获取打包好的文件信息，并解包
        fhead = connect.recv(FILEINFO_SIZE)
        filename, filesize, fid = struct.unpack('128sI128s', fhead)
        filename = filename.decode().strip('\00')
        fid = fid.decode().strip('\00')
        # 文件名必须去掉\00，否则会报错，此处为接收文件
        if filename == 'encrypted_index.csv':
            local_name = 'encrypted_index.csv'
        else:
            local_name = ''.join(random.sample(string.ascii_letters + string.digits, 16)) + '.txt'  # 生成十六位的随机字符串做文件名
            store_adr = 'D:\\Fuzzy Keywords Search\\Sever\\' + local_name
        with open(local_name, 'wb') as f:
            ressize = filesize
            while True:
                if ressize > 1024:
                    filedata = connect.recv(1024)
                else:
                    filedata = connect.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize < 0:
                    break
        # 存储到日志
        print('%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), local_name))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), local_name))
        os.chdir('Sever')
        # 文件信息存储到服务器文件索引表
        if filename != 'encrypted_index.csv':
            fieldname = ['Local_FID', 'FID', 'Title', 'Path']
            if not os.path.isfile('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv'):
                with open('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldname)
                    writer.writeheader()
            with open('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv', 'a', newline='') as f:
                wr = csv.DictWriter(f, fieldnames=fieldname)
                wr.writerow({'Local_FID': local_name, 'FID': fid, 'Title': filename, 'Path': store_adr})
    except Exception as e:
        print('%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), local_name))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n传输文件:\n%s\n失败\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), local_name))
        os.chdir('Sever')


def handle(connect, address):
    print('%s:%s is connectting...' % (address))
    while True:
        order = connect.recv(100).decode()
        if operator.eq(order, '1'):
            download(connect)
        elif operator.eq(order, '2'):
            upload(connect)
        elif operator.eq(order, '3'):
            upload(connect)
        elif operator.eq(order, '4'):
            connect.close()
            break
        connect.send('''
1、 下载文件
2、 上传索引表
3、 上传文件
4、 退出
			'''.encode())


if __name__ == '__main__':
    if not os.path.exists('Sever'):
        os.mkdir('Sever')
    # 工作目录换到Sever文件夹
    os.chdir('Sever')
    # 建立socket链接，并监听8002端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 8002))
    sock.listen(100)
    while True:
        connect, address = sock.accept()
        connect.send('''欢迎使用文件管理服务器，您已经成功连接，请选择您要选用的选项：
1、 下载文件
2、 上传索引表
3、 上传文件
4、 退出
			'''.encode())
        t = threading.Thread(target=handle, args=(connect, address))
        t.setDaemon(True)
        t.start()
