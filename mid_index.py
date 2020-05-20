"""
根据初步的一个索引表，生成一个索引项为[Keyword,FID_LIST]的索引表
"""
import csv
import os
from collections import Counter


def getallfilekw(path):
    """获取所有文件的所有关键字"""
    key_list = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for item in reader:
            key = item['Keywords'].split('，')
            for i in key:
                key_list.append(i)
    return key_list


def quchong(key_list):
    """对关键字列表去重"""
    temp_list = []  # 定义一个临时空列表，用于保存临时数据。
    for i in key_list:  # 遍历原列表，判断如果元素不在临时列表，就追加进去，如果在，就不加。
        if i not in temp_list:
            temp_list.append(i)
    return temp_list


def key_fid(temp_list, max_fre, init_path, kf_path):
    """新建一个csv文件存储所有关键字，索引项为【关键字，文件编号列表】"""
    fieldname = ['Keyword', 'FIDS']
    if not os.path.isfile(kf_path):
        with open(kf_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldname)
            writer.writeheader()

    for m in temp_list:
        fid_list = ['NULL'] * max_fre  # 这个max_fre是统计出来的关键字出现的最高频率
        with open(init_path, 'r') as f1:
            reader1 = csv.DictReader(f1)
            p = 0
            for item in reader1:
                temp = item['Keywords'].split('，')
                if m in temp:
                    fid_list[p] = item['FID']
                    p = p + 1
            str_list = '|'.join(fid_list)

        with open(kf_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Keyword', 'FIDS'])
            writer.writerow({'Keyword': m, 'FIDS': str_list})



def fre_kw(key_list):
    """统计关键词词频,并获得最高词频"""
    count = Counter(key_list)
    dict_count = dict(count)
    max_fre = max(dict_count.values())
    return max_fre


if __name__ == "__main__":
    init_path = 'D:\\Fuzzy Keywords Search\\测试文件夹\\plaintext_index400.csv'
    kf_path = 'D:\\Fuzzy Keywords Search\\测试文件夹\\Key-FID400.csv'
    key_list = getallfilekw(init_path)
    max_fre = fre_kw(key_list)
    temp_list = quchong(key_list)
    key_fid(temp_list, max_fre, init_path, kf_path)
