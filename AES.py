from Crypto.Cipher import AES
import base64
import os


def encrypt(text, key):
    """加密函数"""
    file_aes = AES.new(key, AES.MODE_ECB)   # 创建AES加密对象
    text = text.encode('utf-8')         # 明文必须编码成字节流数据，即数据类型为bytes
    while len(text) % 16 != 0:              # 对字节型数据进行长度判断
        text += b'\x00'                     # 如果字节型数据长度不是16倍整数就进行补充
    en_text = file_aes.encrypt(text)        # 明文进行加密，返回加密后的字节流数据
    return str(base64.b64encode(en_text), encoding='utf-8')  # 将加密后得到的字节流数据进行base64编码并再转换为unicode类型


def decrypt(text, key):
    """解密函数"""
    file_aes = AES.new(key, AES.MODE_ECB)
    text = bytes(text, encoding='utf-8')           # 将密文转换为bytes，此时的密文还是由base64编码过的
    text = base64.b64decode(text)                  # 对密文再进行base64解码
    de_text = file_aes.decrypt(text)               # 密文进行解密，返回明文的bytes
    return str(de_text, encoding='utf-8').strip()  # 将解密后得到的bytes型数据转换为str型，并去除末尾的填充


def file_encrypt(text, key):
    """文件加密函数"""
    file_aes = AES.new(key, AES.MODE_ECB)   # 创建AES加密对象
    while len(text) % 16 != 0:              # 对字节型数据进行长度判断
        text += b'\x00'                     # 如果字节型数据长度不是16倍整数就进行补充
    en_text = file_aes.encrypt(text)        # 明文进行加密，返回加密后的字节流数据
    return en_text


def file_decrypt(text, key):
    """文件解密函数"""
    file_aes = AES.new(key, AES.MODE_ECB)
    de_text = file_aes.decrypt(text)               # 密文进行解密，返回明文的bytes
    return de_text.strip()  # 将解密后得到的bytes型数据转换为str型，并去除末尾的填充


class FileAES:
    def __init__(self,key):
        self.key = key            # 将密钥转换为字符型数据
        self.mode = AES.MODE_ECB  # 操作模式选择ECB

    def encrypt(self, text):
        """加密函数"""
        file_aes = AES.new(self.key, self.mode)  # 创建AES加密对象
        text = text.encode('utf-8')  # 明文必须编码成字节流数据，即数据类型为bytes
        while len(text) % 16 != 0:  # 对字节型数据进行长度判断
            text += b'\x00'  # 如果字节型数据长度不是16倍整数就进行补充
        en_text = file_aes.encrypt(text)  # 明文进行加密，返回加密后的字节流数据
        return str(base64.b64encode(en_text), encoding='utf-8')  # 将加密后得到的字节流数据进行base64编码并再转换为unicode类型

    def decrypt(self, text):
        """解密函数"""
        file_aes = AES.new(self.key,self.mode)
        text = bytes(text, encoding='utf-8')  # 将密文转换为bytes，此时的密文还是由base64编码过的
        text = base64.b64decode(text)   # 对密文再进行base64解码
        de_text = file_aes.decrypt(text)  # 密文进行解密，返回明文的bytes
        return str(de_text, encoding='utf-8').strip()  # 将解密后得到的bytes型数据转换为str型，并去除末尾的填充


if __name__ == '__main__':
    key = os.urandom(16)        # 随即产生n个字节的字节流数据，可以作为随机加密key使用
    text = '中华文化博大精深！'  # 需要加密的内容
    # aes_test = FileAES(key)
    # cipher_text = aes_test.encrypt(text)
    # plain_text = aes_test.decrypt(cipher_text)
    # print('加密后：'+cipher_text)
    # print('解密后：'+plain_text)
    en_text = encrypt(text, key)
    print(en_text)
    a = en_text.encode()
    print(decrypt(a.decode(), key))