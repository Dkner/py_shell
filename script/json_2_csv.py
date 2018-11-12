import json
import csv

def write_line(line):
    json_obj = json.loads(line)
    f = csv.writer(open("corp_change.csv", "ab+"))

    for item in json_obj['items']:
        f.writerow([
            json_obj["corp_id"].encode('utf-8'),
            json_obj["corp_name"].encode('utf-8'),
            item["name"].encode('utf-8'),
            item["old"].encode('utf-8'),
            item["new"].encode('utf-8')
        ])

def f_gen(f):
    counter = 0
    while True:
        line = f.readline()
        counter += 1
        if line:
            print counter
            yield line
        else:
            return

f = csv.writer(open("corp_change.csv", "ab+"))
f.writerow(["corp_id", "corp_name", "name", "old", "new"])

with open("C:/Users/liliang_hu/Desktop/change.log") as f:
    gen = f_gen(f)
    for line in gen:
        try:
            write_line(line[:-2])
        except Exception,e:
            pass