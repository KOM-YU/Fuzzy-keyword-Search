"""
进行关键字查询，返回查询结果
"""

import csv
from pybloom_live import BloomFilter
from bitarray import bitarray


import AES


def build_trapdoor(word, key):
    """对查询关键字构建陷门集合"""
    fuzzy_keys = []
    for i in range(len(word)+1):
        pattern = word[:i] + "*" + word[i:]
        fuzzy_keys.append(pattern)
        if i < len(word):
            pattern = word[:i] + "*" + word[i+1:]
            fuzzy_keys.append(pattern)
    trapdoor = []
    for i in fuzzy_keys:
        trapdoor.append(AES.encrypt(i, key))
    return trapdoor


def retrieval(exactkw, trapdoor_set, key):
    results = []
    with open('D:\\Fuzzy Keywords Search\\encrypted_index.csv', 'r') as f:
        reader = csv.DictReader(f)
        for item in reader:
            kw = AES.decrypt(item['Keyword'], key)
            if kw == exactkw:
                de_fid = AES.decrypt(item['FIDS'], key)
                de_fid = de_fid.split('\x00')[0]
                de_fid = de_fid.split('|')
                for i in de_fid:
                    if i != 'NULL':
                        results.append(i)
                break
            else:
                ba = bitarray(item['BloomFilter'])
                fliter = BloomFilter(capacity=100)
                fliter.bitarray = ba
                flag = False
                for i in trapdoor_set:
                    if i in fliter:
                        flag = True
                if flag:
                    de_fid = AES.decrypt(item['FIDS'], key)
                    de_fid = de_fid.split('\x00')[0]
                    de_fid = de_fid.split('|')
                    for i in de_fid:
                        if i != 'NULL':
                            results.append(i)

    if results:
        # 列表结果去重
        temp_list = []  # 定义一个临时空列表，用于保存临时数据。
        for i in results:  # 遍历原列表，判断如果元素不在临时列表，就追加进去，如果在，就不加。
            if i not in temp_list:
                temp_list.append(i)
        return temp_list
    else:
        return '检索失败'


if __name__ == "__main__":
    key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'
    query = input('请输出查询关键字：')
    trapdoor_set = build_trapdoor(query, key)
    results = retrieval(trapdoor_set, key)
    print('查询结果为:'+'\n')
    print(results)



