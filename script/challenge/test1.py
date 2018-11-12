s = """g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."""

def trans(char):
	shift = 2
	if char>='a' and char<='z':
		i = ord(char)
		i = (i + shift - 97) % 26 + 97
		return chr(i)
	else:
		return char

new_s = map(trans, s)
print(''.join(new_s))

import string

intab='abcdefghijklmnopqrstuvwxyz'
outtab='cdefghijklmnopqrstuvwxyzab'
transtab=string.maketrans(intab,outtab)

# ciphertext=r"g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."
ciphertext="""map"""

plaintext=ciphertext.translate(transtab)

print(plaintext)