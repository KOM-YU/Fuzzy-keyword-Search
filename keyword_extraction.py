import jieba.analyse

"""
使用jieba分词模块提取关键词

jieba.analyse.extract_tags(sentence,topK)
sentence: 文本字符串
topK:  前几个，默认时20
"""


def kwords_extract(text) -> list:
    """提取文档关键字"""
    with open(text, encoding = 'ansi') as file_object:
        kwords = jieba.analyse.extract_tags(file_object.read(), 10)
        # print(kwords)
        # print(len(kwords))
        return  kwords


if __name__ == '__main__':
    file_path = r'D:\test\皇帝的新装续写800字.txt'
    print(kwords_extract(file_path))