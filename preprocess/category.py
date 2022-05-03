import sys
import json

name = 'book'
if len(sys.argv) > 1:
    name = sys.argv[1]

item_cate = {}
item_map = {}
cate_map = {}
with open('./data/%s_data/%s_item_map.txt' % (name, name), 'r') as f:
    for line in f:
        conts = line.strip().split(',')  # 书的出版号-> int id从1开始
        item_map[conts[0]] = conts[1]  # 生成dict

if name == 'taobao':
    with open('UserBehavior.csv', 'r') as f:
        for line in f:
            conts = line.strip().split(',')
            iid = conts[1]
            if conts[3] != 'pv':
                continue
            cid = conts[2]
            if iid in item_map:
                if cid not in cate_map:
                    cate_map[cid] = len(cate_map) + 1
                item_cate[item_map[iid]] = cate_map[cid]
elif name == 'book':
    with open('meta_Books.json', 'r') as f:
        for line in f:
            r = eval(line.strip())  #执行字符串，使得r变成了dict
            iid = r['asin']
            cates = r['categories']
            if iid not in item_map:  # 不处理冷书，不看它的cate
                continue
            cate = cates[0][-1]  # 第一维里的最后一项？估计是“分类”
            if cate not in cate_map:
                cate_map[cate] = len(cate_map) + 1  # 分类 -》 从小到大的int标号
            item_cate[item_map[iid]] = cate_map[cate]  # 从item的int -》 分类的int

with open('./data/%s_data/%s_cate_map.txt' % (name, name), 'w') as f:
    for key, value in cate_map.items():  # map都是原始id到缩小了的int id
        f.write('%s,%s\n' % (key, value))
with open('./data/%s_data/%s_item_cate.txt' % (name, name), 'w') as f:
    for key, value in item_cate.items():  # item int id -》 cate int id的映射
        f.write('%s,%s\n' % (key, value))

# item到cate 的id化数据写入硬盘
