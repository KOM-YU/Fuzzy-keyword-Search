import rsa
import base64
import os


# # 生成公钥和私钥
# pubkey, privkey = rsa.newkeys(512)
#
# # 将公钥存储到pem文件中
# pub = pubkey.save_pkcs1()
# with open('public.pem', 'wb') as f:
#     f.write(pub)
#
# # 将私钥存储到pem文件中
# priv = privkey.save_pkcs1()
# with open('private.pem', 'wb') as f:
#     f.write(priv)

key = b'\xba/\xf5\xa3\x18VD>\x08\x1b\xf5\xbd\xe2\x90\xe9\xa4'

with open('public.pem', 'rb') as f:
    p = f.read()
    pubkey = rsa.PublicKey.load_pkcs1(p)

en_key = rsa.encrypt(key, pubkey)
en_key64 = base64.b64encode(en_key).decode('utf-8')
print(en_key64)

with open('private.pem', 'rb') as f:
    p = f.read()
    privkey = rsa.PrivateKey.load_pkcs1(p)

de_key64 = base64.b64decode(en_key64.encode('utf-8'))
de_key = rsa.decrypt(de_key64, privkey)
print(de_key)




