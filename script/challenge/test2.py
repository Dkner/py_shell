#coding=utf-8
import requests
import re

content = requests.get('http://www.pythonchallenge.com/pc/def/ocr.html').content
content = re.sub('[^a-zA-Z0-9.]','',content)
ind = content.index("below")+5
print content[ind:]+".html"