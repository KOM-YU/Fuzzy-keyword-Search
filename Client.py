from socket import *
import struct
import os
import sys
import datetime
from tkinter import *
import tkinter.messagebox
from tkinter.simpledialog import askstring


from query import *


def search():
    tcp_client_socket.send('1'.encode("utf-8"))
    while True:
        # 输入关键字，构建陷门集合，并将两者进行传输
        # starttime = datetime.datetime.now()
        kw = askstring("文件检索", "请输入检索关键字：")
        if kw is None:
            tcp_client_socket.send('exit'.encode())
            break
        elif kw == '':
            tkinter.messagebox.showwarning('警告', '不能输入为空！')
            continue
        else:
            en_kw = AES.encrypt(kw, key)
            tcp_client_socket.send(en_kw.encode())
        trapdoor_set = build_trapdoor(kw, key)
        trapdoor_string = ' '.join(trapdoor_set)
        tcp_client_socket.send(trapdoor_string.encode())

        # 对接收的检索结果进行处理
        consequence_string = tcp_client_socket.recv(1024*1024).decode()
        if consequence_string == 'wrong':
            tkinter.messagebox.showinfo(title='检索结果', message='检索失败...')
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
                tl = []
                with open('plaintext_index.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for item in reader:
                        if item['FID'] in temp_list:
                            tl.append("{}  {}".format(item['FID'], item['Title']))
                temp = '\n'.join(tl)
                tkinter.messagebox.showinfo(title='检索结果', message="编号   文件名\n"+temp)
                # print('检索结果为：')
                # print(temp_list)

        # endtime = datetime.datetime.now()
        # print(starttime)
        # print(endtime)
        # print((endtime - starttime).total_seconds())


def download():
    tcp_client_socket.send('2'.encode("utf-8"))
    # 输入要下载的文件编号并传输给服务器
    while True:
        fd = askstring("文件下载", "请输入要下载的文件编号（可输入多个编号，以空格隔开）：")
        if fd is None:
            tcp_client_socket.send('exit'.encode())
            break
        elif fd == '':
            tkinter.messagebox.showwarning('警告', '不能输入为空！')
            continue
            # fd_list.append(AES.encrypt(fd, key))
        fd_list = fd.split(' ')
        tm = []
        for m in fd_list:
            tm.append(AES.encrypt(m, key))
        fd_list_string = ' '.join(tm)
        tcp_client_socket.send(fd_list_string.encode())

        # 从服务器下载文件并对文件进行解密存储
        re_f = []
        for i in range(len(tm)):
            i = i + 1
            # print("第{}个文件接收中...".format(i))
            FILEINFO_SIZE = struct.calcsize('1024sI')
            fhead = tcp_client_socket.recv(FILEINFO_SIZE)
            fn, fsize = struct.unpack('1024sI', fhead)
            fn = fn.decode().strip('\00')
            de_fn = AES.decrypt(fn, key)
            de_fn = de_fn.strip(b'\x00'.decode())  # 解密出来的字符串末尾有看不见的空字符，编码成字节流时就会发现
            store_path = r'D:\Fuzzy Keywords Search\Download\download_{}'.format(de_fn)
            filedata = tcp_client_socket.recv(fsize).decode(encoding='utf-8')
            de_filedata = AES.decrypt(filedata, key)
            # print(de_filedata)
            with open(store_path, 'w', encoding='utf-8') as f:
                f.write(de_filedata)
            re_f.append("第{}个文件:{},接受完成。".format(i, de_fn))
            # print("第{}个文件接受完成...\n".format(i))
        tkinter.messagebox.showinfo(title='下载结果', message="\n".join(re_f))
        # print("...共{}个文件接收完成...\n".format(len(fd_list)))


def file_upload():
    tcp_client_socket.send('3'.encode("utf-8"))
    print("上传中......")
    while True:
        file_path = askstring("文件加密上传", "请输入要上传的文件集合：")
        if file_path is None:
            fhead = struct.pack('128sI128s', 'exit'.encode(), 28, 'null'.encode())
            tcp_client_socket.send(fhead)
            break
        elif file_path == '':
            tkinter.messagebox.showwarning('警告', '不能输入为空！')
            continue
        fn_list = []
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
                        en_content = AES.encrypt(file_content, key)
                        en_filesize = sys.getsizeof(en_content) - 49
                        fhead = struct.pack('128sI128s', en_filename.encode(), en_filesize, en_fid.encode())
                        tcp_client_socket.send(fhead)
                        if file_content:
                            tcp_client_socket.send(en_content.encode('utf-8'))
                            fn_list.append("已上传文件:{}" .format(filename))
                            # print("已上传文件:%s " % filename)
                except Exception as e:
                    tkinter.messagebox.showwarning('警告', '未找到该文件......')
                    print("未找到该文件......")
        fn_string = '\n'.join(fn_list)
        tkinter.messagebox.showinfo(title='上传结果', message=fn_string)


def index_upload():
    tcp_client_socket.send('4'.encode("utf-8"))
    while True:
        filename = askstring("索引表上传", "请输入索引表名：")
        if filename is None:
            break
        elif not os.path.isfile(filename):
            tkinter.messagebox.showwarning('警告', '不能输入为空！')
            continue
        else:
            fhead = struct.pack('128sI', filename.encode(), os.stat(filename).st_size)
            tcp_client_socket.send(fhead)
            content = None
            with open(filename, 'rb') as f:
                content = f.read()
            tcp_client_socket.send(content)
            tkinter.messagebox.showinfo('提示', '索引表上传成功！')
            break


def quit():
    root.quit()
    tcp_client_socket.send('5'.encode("utf-8"))


if __name__ == '__main__':
    tcp_client_socket = socket(AF_INET, SOCK_STREAM)
    tcp_client_socket.connect(('127.0.0.1', 8002))
    key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'
    # key = os.urandom(16)  # 随即产生n个字节的字节流数据，可以作为随机加密key使用
    root = Tk()
    root.geometry('400x300')
    root.title('欢迎进入文件管理系统')

    btn1 = Button(root, text='1  文件检索', anchor=NW, command=search)  # command中只能写函数名，不能带参数，括号也不行！
    btn1.place(width=100, relx=0.4, rely=0.15)

    btn2 = Button(root, text='2  文件下载', anchor=NW, command=download)
    btn2.place(width=100, relx=0.4, rely=0.3)

    btn3 = Button(root, text='3  文件加密上传', anchor=NW, command=file_upload)
    btn3.place(width=100, relx=0.4, rely=0.45)

    btn4 = Button(root, text='4  索引表上传', anchor=NW, command=index_upload)
    btn4.place(width=100, relx=0.4, rely=0.6)

    btn5 = Button(root, text='5  退出', command=quit, anchor=NW)
    btn5.place(width=100, relx=0.4, rely=0.75)

    root.mainloop()
    tcp_client_socket.close()
