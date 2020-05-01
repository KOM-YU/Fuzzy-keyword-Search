from socket import *
import struct
import os
import sys


import AES
from query import *

def hello_page():
    print("-----欢迎进入系统-----")
    print("     1  文件检索      ")
    print("     2  文件下载      ")
    print("     3  文件加密上传      ")
    print("     4  索引表上传      ")
    print("     5  退出         ")
    print("--------------------")


def search(tcp_client_socket, key):
    while True:
        # 输入关键字，构建陷门集合，并将两者进行传输
        kw = input("请输入搜索关键字（输入exit退出）：")
        if kw == 'exit':
            tcp_client_socket.send(kw.encode())
            break
        else:
            en_kw = AES.encrypt(kw, key)
            tcp_client_socket.send(en_kw.encode())
        trapdoor_set = build_trapdoor(kw, key)
        trapdoor_string = ' '.join(trapdoor_set)
        tcp_client_socket.send(trapdoor_string.encode())

        # 对接收的检索结果进行处理
        consequence_string = tcp_client_socket.recv(1024*1024).decode()
        if consequence_string == 'wrong':
            print('检索失败...')
            continue
        else:
            consequence = consequence_string.split(' ')
            consequence_list = []
            for i in consequence:
                i = AES.decrypt(i, key)
                i = i.split('\x00')[0]
                i = i.split('|')
                for k in i:
                    if k != 'NULL':
                        consequence_list.append(k)
            if consequence_list:               # 对列表进行去重
                temp_list = []                 # 定义一个临时空列表，用于保存临时数据。
                for i in consequence_list:     # 遍历原列表，判断如果元素不在临时列表，就追加进去，如果在，就不加。
                    if i not in temp_list:
                        temp_list.append(i)
                print('检索结果为：')
                print(temp_list)


def download(tcp_client_socket, key):
    # 输入要下载的文件编号并传输给服务器
    while True:
        fd_list = []
        while True:
            fd = input('请输入要下载的文件编号：\n(输入end则结束输入，输入exit则退出文件下载。输入为空默认为取消下载。)\n')
            if fd == 'end':
                break
            elif fd == 'exit':
                fd_list.append('exit')
                break
            fd_list.append(AES.encrypt(fd, key))
        if 'exit' in fd_list:
            tcp_client_socket.send('exit'.encode())
            break
        if not fd_list:
            tcp_client_socket.send('exit'.encode())
            break
        fd_list_string = ' '.join(fd_list)
        tcp_client_socket.send(fd_list_string.encode())

        # 从服务器下载文件并对文件进行解密存储
        print("...预计共接收{}个文件...\n".format(len(fd_list)))
        for i in range(len(fd_list)):
            i = i + 1
            print("第{}个文件接收中...".format(i))
            FILEINFO_SIZE = struct.calcsize('1024sI')
            fhead = tcp_client_socket.recv(FILEINFO_SIZE)
            fn, fsize = struct.unpack('1024sI', fhead)
            fn = fn.decode().strip('\00')
            de_fn = AES.decrypt(fn, key)
            de_fn = de_fn.strip(b'\x00'.decode())  # 解密出来的字符串末尾有看不见的空字符，编码成字节流时就会发现
            store_path = r'D:\Fuzzy Keywords Search\Download\download_{}'.format(de_fn)
            filedata = tcp_client_socket.recv(fsize).decode()
            de_filedata = AES.decrypt(filedata, key)
            with open(store_path, 'w') as f:
                f.write(de_filedata)
            print("第{}个文件接受完成...\n".format(i))
        print("...共{}个文件接收完成...\n".format(len(fd_list)))


def file_upload(tcp_client_socket, key):
    print("上传中......")
    while True:
        file_path = input("请输入要上传的文件集合（输入exit退出）：")
        if file_path == "exit":
            fhead = struct.pack('128sI128s', 'exit'.encode(), 28, 'null'.encode())
            tcp_client_socket.send(fhead)
            break
        with open(file_path, 'r') as f:
            re = csv.DictReader(f)
            for item in re:
                filename = item['Title']
                en_filename = AES.encrypt(filename, key)
                adr = item['Path']
                fid = item['FID']
                en_fid = AES.encrypt(fid, key)
                file_content = None
                try:
                    with open(adr, "r") as f:
                        file_content = f.read()
                except Exception as e:
                    print("未找到该文件......")
                en_content = AES.encrypt(file_content, key)
                en_filesize = sys.getsizeof(en_content) - 49
                fhead = struct.pack('128sI128s', en_filename.encode(), en_filesize, en_fid.encode())
                tcp_client_socket.send(fhead)
                if file_content:
                    tcp_client_socket.send(en_content.encode('utf-8'))
                    print("已上传文件:%s " % filename)


def index_upload(tcp_client_socket):
    while True:
        filename = input("请输入索引表名（输入exit退出）：")
        if filename == 'exit':
            break
        if not os.path.isfile(filename):
            print('该文件不存在，请重新输入...')
            continue
        fhead = struct.pack('128sI', filename.encode(), os.stat(filename).st_size)
        tcp_client_socket.send(fhead)
        content = None
        with open(filename, 'rb') as f:
            content = f.read()
        tcp_client_socket.send(content)
        print('索引表上传成功')


def main():
    tcp_client_socket = socket(AF_INET, SOCK_STREAM)
    tcp_client_socket.connect(('127.0.0.1', 8002))
    key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'
    # key = os.urandom(16)  # 随即产生n个字节的字节流数据，可以作为随机加密key使用
    while True:
        hello_page()
        select_num = input("请输入您的操作序号：")
        if select_num == "1":
            tcp_client_socket.send(select_num.encode("utf-8"))
            search(tcp_client_socket, key)
        elif select_num == "2":
            tcp_client_socket.send(select_num.encode("utf-8"))
            download(tcp_client_socket, key)
        elif select_num == "3":
            tcp_client_socket.send(select_num.encode("utf-8"))
            file_upload(tcp_client_socket, key)
        elif select_num == "4":
            tcp_client_socket.send(select_num.encode("utf-8"))
            index_upload(tcp_client_socket)
        elif select_num == "5":
            tcp_client_socket.send(select_num.encode("utf-8"))
            break
        else:
            print("请重新输入...")
    tcp_client_socket.close()


if __name__ == '__main__':
    main()
