import datetime
import random
import string
import sys

def chinese():
    """生成随机汉字"""
    head = random.randint(0xb0, 0xf7)
    body = random.randint(0xa1, 0xfe)
    val = f'{head:x}{body:x}'
    str = bytes.fromhex(val).decode('gb2312')
    return str


def gen_keyword():
    """生成随机中文词语"""
    size = random.randint(2, 4)
    zi_list = []
    for i in range(size):
        zi_list.append(chinese())
    ci = ''
    for k in zi_list:
        ci = ci + k
    return ci


def gen(num):
    list = []
    for i in range(num):
        size = random.randint(10, 16)
        kw = ''.join(random.sample(string.ascii_letters + string.digits, size))
        list.append(kw)
    return list


def kl(num):
    """生成指定数目的中文单词"""
    kw_list = []
    for i in range(num):
        kw_list.append(gen_keyword())
    return  kw_list


def ed_1(word):
    fuzzy_keys = []
    for i in range(len(word) + 1):
        pattern = word[:i] + "*" + word[i:]     # 将通配符插入字符串中
        fuzzy_keys.append(pattern)
        if i < len(word) and word[i] != '*':
            pattern = word[:i] + "*" + word[i + 1:]  # 将通配符替换字符串中某个字符
            fuzzy_keys.append(pattern)
    return fuzzy_keys

def qu_chong(key_list):
    """对关键字列表去重"""
    temp_list = []  # 定义一个临时空列表，用于保存临时数据。
    for i in key_list:  # 遍历原列表，判断如果元素不在临时列表，就追加进去，如果在，就不加。
        if i not in temp_list and i != '**':
            temp_list.append(i)
    return temp_list


def ed_2(word):
    fuzzy_keys = ed_1(word)
    fuzzy_keys_2 = []
    for i in fuzzy_keys:
        for k in ed_1(i):
            fuzzy_keys_2.append(k)
    fuzzy_keys_2 = qu_chong(fuzzy_keys_2)
    return fuzzy_keys_2


if __name__ == '__main__':
    print(ed_2('善良'))
    # list = gen(2000)
    # fl = []
    # size_init_fl = sys.getsizeof(fl)
    # print(size_init_fl)
    # for i in list:
    #     temp = ed_2(i)
    #     for k in temp:
    #         fl.append(k)
    # size_fl = sys.getsizeof(fl)
    # print(size_fl)
    # real_size = size_fl - size_init_fl
    # print(real_size)
    # kb_size = real_size / (1024*1024)
    # print(kb_size)
    # yushu = real_size % 1024
    # print(yushu)
    # starttime = datetime.datetime.now()
    # for i in list:
    #     ed_2(i)
    # endtime = datetime.datetime.now()
    # print(starttime)
    # print(endtime)
    # print(endtime - starttime)
    # word = '安全'
    # print(ed_1(word))
    # fuzzy_set = ed_2(word)
    # print(fuzzy_set)
    # print(len(fuzzy_set))

# starttime = datetime.datetime.now()

# endtime = datetime.datetime.now()
# print (endtime - starttime).seconds
