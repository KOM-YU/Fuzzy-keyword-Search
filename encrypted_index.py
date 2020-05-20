"""
生成模糊关键字集合，并存储到布隆过滤器中。
对索引表进行加密。
"""

import csv
import os
from pybloom_live import BloomFilter
import base64

import AES


def ed_1(word):
    """为每个关键字构建模糊集合，默认编辑距离为1"""
    fuzzy_keys = []
    for i in range(len(word)+1):
        pattern = word[:i] + "*" + word[i:]
        fuzzy_keys.append(pattern)
        if i < len(word):
            pattern = word[:i] + "*" + word[i+1:]
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


def kw_encrypt(fuzzy_set, key):
    """对模糊关键字集合进行加密"""
    en_list = []
    for i in fuzzy_set:
        en_list.append(AES.encrypt(i, key))
    return en_list


def add_to_filter(en_list, filter):
    """将模糊关键字集合存储到布隆过滤器中"""
    for k in en_list:
        filter.add(k)


def en_store(en_path, item, bitarray, key):
    """将加密信息存储到文件中"""
    fieldname = ['Keyword', 'BloomFilter', 'FIDS']
    if not os.path.isfile(en_path):
        with open(en_path, 'w', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=fieldname)
            wr.writeheader()

    with open(en_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldname)
        en_key = AES.encrypt(item['Keyword'], key)
        en_FID = AES.encrypt(item['FIDS'], key)
        writer.writerow({'Keyword': en_key, 'BloomFilter': bitarray, 'FIDS': en_FID})


# if __name__ == '__main__':
#     key = os.urandom(16)
#     with open('D:\\毕设项目\\明文索引表.csv', 'r') as f:
#         reader = csv.DictReader(f)
#         for item in reader:
#             kw_list = item['Keywords'].split('，')
#             filter = BloomFilter(capacity=100)
#             for kw in kw_list:
#                 fuzzy_set = build_fuzzy_keyword_set(kw)
#                 en_fuzzy_set = kw_encrypt(fuzzy_set, key)
#                 add_to_filter(en_fuzzy_set, filter)
#             bitarray = base64.b64encode(filter.bitarray.tobytes()).decode('ascii')
#             en_store(item, bitarray, key)