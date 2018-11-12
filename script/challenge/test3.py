import requests
import re

content = requests.get('http://www.pythonchallenge.com/pc/def/equality.html').content
m = re.findall("[a-z0-9]+[A-Z]{3}([a-z])[A-Z]{3}[a-z0-9]+",content)
print(m)
print(''.join(m))