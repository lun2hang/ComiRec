import os
import sys
import json
import random
from collections import defaultdict

random.seed(1230)

name = 'book'
filter_size = 5
if len(sys.argv) > 1:
    name = sys.argv[1]
if len(sys.argv) > 2:
    filter_size = int(sys.argv[2])

users = defaultdict(list)  # value是list，默认值是空list
item_count = defaultdict(int)  # value是 int，默认值是0


def read_from_amazon(source):
    with open(source, 'r') as f:
        for line in f:
            r = json.loads(line.strip())
            uid = r['reviewerID']  # user id
            iid = r['asin']  # book id
            item_count[iid] += 1  # 这本书被评价的次数
            ts = float(r['unixReviewTime'])  # 书被评价的时间
            users[uid].append((iid, ts))  # 追加，在uid的key下，追加所有 iid和ts对


def read_from_taobao(source):
    with open(source, 'r') as f:
        for line in f:
            conts = line.strip().split(',')
            uid = int(conts[0])
            iid = int(conts[1])
            if conts[3] != 'pv':
                continue
            item_count[iid] += 1
            ts = int(conts[4])
            users[uid].append((iid, ts))


if name == 'book':
    read_from_amazon('reviews_Books_5.json')  # 获得一个dict uid：iid ts，iid ts 多次互动的串
elif name == 'taobao':
    read_from_taobao('UserBehavior.csv')

items = list(item_count.items())  # 列表，里面的每个元素是 iid 和 被打分的次数 对
items.sort(key=lambda x:x[1], reverse=True) # 按照第二维，即打分次数排序，降序排好

item_total = 0
for index, (iid, num) in enumerate(items): # 0开始的下标和元素，元素就是个对
    if num >= filter_size:
        item_total = index + 1  # 大于filtersize次打分的书才被留下来，统计数量。
    else:
        break

item_map = dict(zip([items[i][0] for i in range(item_total)], list(range(1, item_total+1))))  # dict转换zip对象，对象元素是（书iid，int标号从1开始递增），只含互动次数大于阈值的。于是变成dict iid-》1~个数的整数标号，稠密IID的ID化！！！

user_ids = list(users.keys())  # 所有uid的list
filter_user_ids = []
for user in user_ids:  ## 遍历所有用户
    item_list = users[user] ## 单个用户评分的所有书和时间
    index = 0
    for item, timestamp in item_list:
        if item in item_map:  # 如果是互动次数足够的书，计数加一
            index += 1
    if index >= filter_size: # 如果这个用户发生的互动次数也大于相同的阈值，把这个足够稠密的uid加入list，并用稠密uid集合替代原始uid集合
        filter_user_ids.append(user)
user_ids = filter_user_ids # 剩余user_ids 都有N次以上跟被互动N次以上书的互动。人和书都只留被互动N次及以上的

random.shuffle(user_ids)
num_users = len(user_ids)
user_map = dict(zip(user_ids, list(range(num_users)))) # user map 是uid-》1~个数的整数标号。稠密UID的id化！！！ item map也是
split_1 = int(num_users * 0.8)
split_2 = int(num_users * 0.9)
train_users = user_ids[:split_1]  # 前0.8用于训练
valid_users = user_ids[split_1:split_2]  # 0.8~0.9 用于验证
test_users = user_ids[split_2:]  # 最后十分之一用于测试

def export_map(name, map_dict):  # iid -》 整数 写入文件，或者uid，仅限稠密的
    with open(name, 'w') as f:
        for key, value in map_dict.items():
            f.write('%s,%d\n' % (key, value))

def export_data(name, user_list):
    total_data = 0
    with open(name, 'w') as f:
        for user in user_list:
            if user not in user_map:  # 不写稀疏的。跳过
                continue
            item_list = users[user]  # 稠密用户的所有行为 书，时间对的序列
            item_list.sort(key=lambda x:x[1])  # 按时间从小到大，就是时间序
            index = 0
            for item, timestamp in item_list:
                if item in item_map:  # 只保留了稠密书
                    f.write('%d,%d,%d\n' % (user_map[user], item_map[item], index))  # 稠密uid的 int 化、iid的int 化、时间顺序号从1开始的三元组就是一行用户行为。
                    index += 1
                    total_data += 1
    return total_data # 总可用训练数据量

path = './data/' + name + '_data/'
if not os.path.exists(path):
    os.mkdir(path)

export_map(path + name + '_user_map.txt', user_map)  # 输出了热user 到 int 的映射查找表，隐含热uid集合，同理热item
export_map(path + name + '_item_map.txt', item_map)

total_train = export_data(path + name + '_train.txt', train_users)  # 训练 验证 集合，每行是（用户int，书int，互动顺序号从0开始）
total_valid = export_data(path + name + '_valid.txt', valid_users)
total_test = export_data(path + name + '_test.txt', test_users)
print('total behaviors: ', total_train + total_valid + total_test)


# user id化，item id化，时间序id化的训练数据。id化用的自增int，而没有用hash
