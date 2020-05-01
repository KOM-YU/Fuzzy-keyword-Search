from socket import *
import random
import string
import csv
import os
import struct
from pybloom_live import BloomFilter
from bitarray import bitarray


def search(client_socket):
    while True:
        # 接受检索的关键字及陷门集合
        exact_kw = client_socket.recv(1024).decode('utf-8')
        if exact_kw == 'exit':
            break
        trapdoor_string = client_socket.recv(1024*1024).decode("utf-8")
        trapdoor_list = trapdoor_string.split(' ')

        # 进行关键字检索
        print("检索中......")
        results = []
        with open('D:\\Fuzzy Keywords Search\\Sever\\encrypted_index.csv', 'r') as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item['Keyword'] == exact_kw:
                    print('关键字检索成功...')
                    results.append(item['FIDS'])
                    break
                else:
                    ba = bitarray(item['BloomFilter'])
                    fliter = BloomFilter(capacity=100)
                    fliter.bitarray = ba
                    flag = False
                    for i in trapdoor_list:
                        if i in fliter:
                            flag = True
                    if flag:
                        results.append(item['FIDS'])

        if not results:
            print('检索失败')
            client_socket.send('wrong'.encode())
            continue
        else:
            results_string = ' '.join(results)
            client_socket.send(results_string.encode())
            print('关键字检索成功...')


def download(client_socket):
    # 根据客户端提交的需要下载的文件编号，将相应密文文件返还给客户端
    while True:
        print('正在等待接受需要下载的文件编号...')
        fids = client_socket.recv(1024 * 1024).decode()
        while not fids:
            fids = client_socket.recv(1024 * 1024).decode()
        if fids == 'exit':
            print('客户端取消下载文件...')
            break
        # 对接收到的文件编号进行处理
        fids_list = fids.split(' ')
        # 根据文件编号查询服务器本地索引表，返回相应检索结果
        title_path = {}
        with open("D:\\Fuzzy Keywords Search\\Sever\\file_index.csv", 'r') as f:
            re = csv.DictReader(f)
            for item in re:
                if item['FID'] in fids_list:
                    title_path[item['Title']] = item['Path']
        print(title_path)
        # 传送密文文件到客户端
        i = 0
        for title, path in title_path.items():
            i = i + 1
            print("第{}个文件传输中...".format(i))
            fhead = struct.pack('1024sI', title.encode(), os.stat(path).st_size)
            client_socket.send(fhead)
            with open(path, 'rb') as f:
                con = f.read()
                client_socket.send(con)
            print("第{}个文件传输完毕...".format(i))
        print('所有文件传输完毕...')


def file_upload(client_socket):
    print("用户正在上传文件中...")
    FILEINFO_SIZE = struct.calcsize('128sI128s')
    while True:
        fhead = client_socket.recv(FILEINFO_SIZE)
        file_name, filesize, fid = struct.unpack('128sI128s', fhead)
        file_name = file_name.decode().strip('\00')
        fid = fid.decode().strip('\00')
        if file_name == "exit":
            print("用户返回选择页面")
            break
        print("----------")
        local_name = ''.join(random.sample(string.ascii_letters + string.digits, 16)) + '.txt'
        store_path = 'D:\\Fuzzy Keywords Search\\Sever\\' + local_name
        with open(store_path, "wb") as f:
            ressize = filesize
            while True:
                if ressize > 1024:
                    filedata = client_socket.recv(1024)
                else:
                    filedata = client_socket.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize < 0:
                    break
        fieldname = ['Local_FID', 'FID', 'Title', 'Path']
        if not os.path.isfile('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv'):
            with open('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldname)
                writer.writeheader()
        with open('D:\\Fuzzy Keywords Search\\Sever\\file_index.csv', 'a', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=fieldname)
            wr.writerow({'Local_FID': local_name, 'FID': fid, 'Title': file_name, 'Path': store_path})
        print("文件%s上传成功..." % file_name)


def index_upload(client_socket):
    print("用户正在上传文件中...")
    FILEINFO_SIZE = struct.calcsize('128sI')
    fhead = client_socket.recv(FILEINFO_SIZE)
    filename, filesize = struct.unpack('128sI', fhead)
    filename = filename.decode().strip('\x00')
    path = 'D:\\Fuzzy Keywords Search\\Sever\\{}'.format(filename)
    with open(path, 'wb') as f:
        ressize = filesize
        while True:
            if ressize > 1024:
                filedata = client_socket.recv(1024)
            else:
                filedata = client_socket.recv(ressize)
                f.write(filedata)
                break
            if not filedata:
                break
            f.write(filedata)
            ressize = ressize - len(filedata)
            if ressize < 0:
                break
    print("文件%s上传成功..." % filename)


def main():
    tcp_server_socket = socket(AF_INET, SOCK_STREAM)
    tcp_server_socket.bind(('', 8002))
    tcp_server_socket.listen(128)
    while True:
        client_socket, client_addr = tcp_server_socket.accept()
        print("%s客户端链接成功..." % str(client_addr))
        while True:
            select_num = client_socket.recv(1024).decode("utf-8")
            if select_num == "1":
                search(client_socket)
            elif select_num == "2":
                download(client_socket)
            elif select_num == "3":
                file_upload(client_socket)
            elif select_num == "4":
                index_upload(client_socket)
            elif select_num == "5":
                print("客户端断开了链接")
                break
        client_socket.close()

    # tcp_server_socket.close()


if __name__ == '__main__':
    main()

