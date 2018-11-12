#coding=utf-8
import time
import json
import urllib
import re
import requests
from lcurl import Lcurl


class FUNCBOX(object):

    def __getattr__(self, key):
        return self.my_defined_func

    def my_default_func(self, **kw):
        return kw['value']

    def my_eval_func(self, **kw):
        new = kw['new']
        return eval(kw['value'])

    def my_time_func(self, **kw):
        timestamp_str = str(round(time.time()))
        return timestamp_str

    def my_milltime_func(self, **kw):
        milltimestamp_str = str(round(time.time() * 1000))
        return milltimestamp_str

    def my_defined_func(self, **kw):
        the_instance = kw['instance']
        the_method = kw['method']
        return getattr(the_instance, the_method)(**kw)

class Transformer(object):
    def trans(self, input, map):
        output = {}
        func_service = FUNCBOX()
        for (k, (v, func_name)) in map.items():
            kw = {"value": v, "new": input, "instance": self, "method": func_name}
            try:
                col = getattr(func_service, func_name)(**kw)
                if col:
                    output[k] = col
            except Exception, e:
                print '[Trans ' + k + ' Error]:' + str(e)
        return output

    def my_trans_key_words_func(self, **kw):
        new = kw['new']
        value = eval(kw['value'])
        value = re.sub('(^\[|\]$)', '', value)
        return value.split(',')

    def change_date(self, date):
        try:
            return int(time.mktime(time.strptime(date, '%Y.%m')))
        except Exception, e:
            return ''

    def test(self, **kw):
        return kw['value']+"shitttttttttttt"


input = [
    {
        "address": "",
        "company_name": "牛犊工作室（Newdo",
        "company_phones": "",
        "company_web": "http://www.newdotech.com/",
        "contacts": "1",
        "corp_category": 1,
        "description": "牛犊科技，智能照明创新者。牛犊工作室先后设计了酷毙灯、3D红外立体手势识别系统、电源管理系统、Love Disk等作品。",
        "founding_time": "2012.9",
        "industries": "Slogan：暂未收录",
        "investor_list": "",
        "key_words": '''[智能家居, 灯泡灯具, 硬件]''',
        "last_update": 1488188039,
        "logo_url": "e5e4e0dec153580ef8e055c1c8a8a06b",
        "product_description": "牛犊科技，智能照明创新者。牛犊工作室先后设计了酷毙灯、3D红外立体手势识别系统、电源管理系统、Love Disk等作品。",
        "product_url": "16d6f6f7626e54afeafecc48e3bd24c0",
        "revenue": "",
        "scale": "暂未收录",
        "simple_name": "牛犊科技",
        "source": "itorange",
        "style": "1",
        "rival_companies": [
            "我要认领",
            "WiPlug推",
            "Yeelink",
            "YeeLight易灯",
            "善从科技",
            "苏州摩多物联科技"
        ]
    },
    {
        "company_web": "http://www.nowledgedata.com.cn",
        "revenue": "",
        "product_url": "0b9e3feab29163307b2a765e77780a24",
        "simple_name": "识代运筹NowledgeData",
        "industries": "基于大数据的营销整合解决方案",
        "style": "1",
        "scale": "150-300人",
        "contacts": "1",
        "last_update": 1488284690,
        "source": "itorange",
        "company_name": "陕西识代运筹信息科技股份有限公司",
        "key_words": "[口碑舆情, 大数据, 大数据营销, 广告营销, 微博营销, 数据挖掘, 整合营销传播]",
        "logo_url": "a84080b7e35c8cc5253377f12adb1c03",
        "corp_category": 1,
        "description": "识代运筹NowledgeData是一家专注于对互联网，特别是社交网络的品牌口碑和舆情进行收集和分析的公司，为客户提供基于大数据的营销整合解决方案。",
        "address": "",
        "product_description": "识代运筹NowledgeData是一家专注于对互联网，特别是社交网络的品牌口碑和舆情进行收集和分析的公司，为客户提供基于大数据的营销整合解决方案。",
        "founding_time": "2011.3",
        "itorange_id": "13",
        "company_phones": "",
        "investor_list": "c05c2dee9b8e16cf2df6abaa30dce8de.html",
        "rival_companies": [
            "我要认领",
            "SocialAgent社交特工",
            "众人互联",
            "微决策Infomorrow",
            "Infomorrow英莫信息",
            "索孚科技Soforit"
        ]
    }
]

trans_corp_map = {
    "source": ["1", "test"],
    "style": ["0", "my_default_func"],
    "simple_name": ["new['company_name']", "my_eval_func"],
    "logo_url": ["new['logo_url']", "my_eval_func"],
    "description": ["new['description']", "my_eval_func"],
    "opponents": ['new["rival_companies"]', "my_eval_func"],
    "business": ["new['key_words']", "my_trans_key_words_func"],
    "key_words": ["new['key_words']", "my_eval_func"],
    "company_web": ["new['company_web']", "my_eval_func"],
    "client_time": ["", "my_time_func"],
    "create_time": ["new['founding_time']", "my_eval_func"],
}

trans_product_map = {
    "op": ["add", "my_default_func"],
    "source": ["1", "my_default_func"],
    "type": ["0", "my_default_func"],
    "product_name": ["new['simple_name']", "my_eval_func"],
    "key_words": ["new['key_words']", "my_eval_func"],
    "client_time": ["", "my_time_func"],
    "multi_content": ['''[{"type":"1","content":new["industries"]},
                        {"type":"2","content":new["logo_url"]},
                        {"type":"2","content":new["product_url"]},
                        {"type":"3","content":new["product_description"]}]''', "my_eval_func"],
}


def fuzzySuggestCorpName(keyword):
    url = 'https://api-sandbox.intsig.net/user/CCAppService/enterprise/advanceSearch'
    url_param = {
        'keyword': keyword,
        'start': 0
    }
    curl = Lcurl()
    r = curl.get(url, url_param)
    if not r:
        return False
    ret = r.json()
    print ret
    if ret['status'] == '1' and ret['data']['total'] > 0:
        return ret['data']['items'][0]
    else:
        return False

def getSummaryByName(name):
    url = 'https://srh.intsig.net/CCAppService/enterprise/getSummaryByName'
    url_param = {
        'name': name
    }
    param = urllib.urlencode(url_param)
    url = url + '?' + param
    r = requests.get(url)
    print r.content

trans_service = Transformer()
for i in input:
    i['founding_time'] = trans_service.change_date(i['founding_time'])
    corp_output = trans_service.trans(input=i, map=trans_corp_map)
    product_output = trans_service.trans(input=i, map=trans_product_map)
    print corp_output['business'],json.dumps(corp_output).encode('utf-8'), json.dumps(product_output).encode('utf-8')

# fuzzySuggestCorpName('北京腾云天下科技有限公司')
# getSummaryByName('江苏省电信公司苏州分公司')
