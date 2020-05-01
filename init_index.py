"""
对文档集合中所有信息进行初步提取，建立一个索引项为
['FID', 'Title', 'Keywords']的索引表
"""

import os
import csv

from keyword_extraction import kwords_extract

path = 'D:\\Fuzzy Keywords Search\\样本文件集'


def get_filelist(path):
    """获取该目录下所有文件的存储路径，并存储在列表中"""
    FilePathlist = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            # 文件名列表，包含完整路径
            FilePathlist.append(os.path.join(home, filename))
            # 文件名列表，只包含文件名
            # Filelist.append( filename)
    return FilePathlist


def add_to_bloomfilter(filter, fuzzylist):
    """将模糊集合中每个模糊关键字加入布隆过滤器中"""
    for fuzzykw in fuzzylist:
        filter.add(fuzzykw)


if __name__ == "__main__":
    fieldname = ['FID', 'Title', 'Keywords', 'Path']
    if not os.path.isfile('D:\\Fuzzy Keywords Search\\plaintext_index.csv'):
        with open('D:\\Fuzzy Keywords Search\\plaintext_index.csv', 'w', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=fieldname)
            wr.writeheader()

    FilePathlist = get_filelist(path)
    count = 0
    for file_path in FilePathlist:
        count += 1
        fid = str(count).zfill(4)           # zfill对数字字符串左侧补0
        title = file_path.split('\\')[-1]

        # 提取文章关键字
        keywords_list = kwords_extract(file_path)
        keywords = ''
        for i in range(len(keywords_list) - 1):
            keywords += keywords_list[i]
            keywords += '，'
        keywords += keywords_list[-1]

        # 将各个数据存储在csv文件中
        fieldname = ['FID', 'Title', 'Keywords', 'Path']
        with open('D:\\Fuzzy Keywords Search\\plaintext_index.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldname)
            writer.writerow({'FID': fid, 'Title': title, 'Keywords': keywords, 'Path':file_path})
