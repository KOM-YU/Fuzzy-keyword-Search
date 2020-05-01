from encrypted_index import *
from query import *

import AES


key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'

while 1:
    task = input('请选择执行操作：\n'
                 '（1）创建密文索引表；\n'
                 '（2）关键字查询; \n'
                 '（3）结束查询' + '\n')

    if task == str(1):
        with open('D:\\Fuzzy Keywords Search\\Key-FID.csv', 'r') as f:
            reader = csv.DictReader(f)
            for item in reader:
                filter = BloomFilter(capacity=100)
                fuzzy_set = build_fuzzy_keyword_set(item['Keyword'])
                en_fuzzy_set = kw_encrypt(fuzzy_set, key)
                add_to_filter(en_fuzzy_set, filter)
                ba = filter.bitarray.to01()
                en_store(item, ba, key)
        print('创建完成...\n')

    elif task == str(2):
        query = input('请输出查询关键字：' + '\n')
        trapdoor_set = build_trapdoor(query, key)
        results = retrieval(query, trapdoor_set, key)
        print('查询结果为:', results, '\n')

    elif task == str(3):
        break
