import requests

ret = requests.get('http://toutiao.com/group/6273506991197470978/')
print(type(ret.content), ret.content)