import rsa

# (pubkey, privkey) = rsa.newkeys(512)
#
# pub = pubkey.save_pkcs1().decode()
# with open('public.pem', 'w') as f:
#     f.write(pub)
#
# pri = privkey.save_pkcs1().decode()
# with open('private.pem', 'w') as f:
#     f.write(pri)

# 导入密钥
with open('public.pem','r') as f:
    pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())

with open('private.pem','r') as f:
    privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())

message = 'hello world'

# 用公钥加密、再用私钥解密
crypto = rsa.encrypt(message.encode(), pubkey)
message = rsa.decrypt(crypto, privkey)
print(message, crypto)

# 私钥签名
signature = rsa.sign(message, privkey, 'SHA-1')
# 公钥验证
auth = rsa.verify(message, signature, pubkey)

print(auth, signature)

