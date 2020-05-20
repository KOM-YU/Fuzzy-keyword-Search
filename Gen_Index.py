import datetime

from init_index import *
from mid_index import *
from encrypted_index import *


if __name__ == '__main__':
    doc_path = 'D:\\Fuzzy Keywords Search\\样本文件集'
    plain_path = 'D:\\Fuzzy Keywords Search\\plaintext_index.csv'
    KF_path = 'D:\\Fuzzy Keywords Search\\Key-FID.csv'
    en_path = 'D:\\Fuzzy Keywords Search\\encrypted_index.csv'

    starttime = datetime.datetime.now()
    print(starttime)
    # init_index.csv
    fieldname = ['FID', 'Title', 'Keywords', 'Path']
    if not os.path.isfile(plain_path):
        with open(plain_path, 'w', newline='') as f:
            wr = csv.DictWriter(f, fieldnames=fieldname)
            wr.writeheader()

    FilePathlist = get_filelist(doc_path)
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
        with open(plain_path, 'a', newline='', errors='ignore') as f:
            writer = csv.DictWriter(f, fieldnames=fieldname)
            writer.writerow({'FID': fid, 'Title': title, 'Keywords': keywords, 'Path':file_path})


    # mid_index.csv
    key_list = getallfilekw(plain_path)
    max_fre = fre_kw(key_list)
    temp_list = quchong(key_list)
    key_fid(temp_list, max_fre, plain_path, KF_path)


    # encrypted_index.csv
    key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'
    with open(KF_path, 'r') as f:
        reader = csv.DictReader(f)
        for item in reader:
            filter = BloomFilter(capacity=100)
            fuzzy_set_1 = ed_1(item['Keyword'])
            en_fuzzy_set = kw_encrypt(fuzzy_set_1, key)
            add_to_filter(en_fuzzy_set, filter)
            fuzzy_set_2 = ed_2(item['Keyword'])
            en_fuzzy_set = kw_encrypt(fuzzy_set_2, key)
            add_to_filter(en_fuzzy_set, filter)
            ba = filter.bitarray.to01()
            en_store(en_path, item, ba, key)

    endtime = datetime.datetime.now()
    print(endtime)
    print(endtime - starttime)