import numpy
import json
import random
import numpy as np


class DataIterator:

    def __init__(self, source,
                 batch_size=128,
                 maxlen=100,
                 train_flag=0
                ):
        self.read(source)
        self.users = list(self.users)
        
        self.batch_size = batch_size
        self.eval_batch_size = batch_size
        self.train_flag = train_flag
        self.maxlen = maxlen
        self.index = 0

    def __iter__(self):
        return self
    
    def next(self):
        return self.__next__()

    def read(self, source):
        self.graph = {}
        self.users = set()
        self.items = set()
        with open(source, 'r') as f:
            for line in f:
                conts = line.strip().split(',')
                user_id = int(conts[0])
                item_id = int(conts[1])
                time_stamp = int(conts[2])
                self.users.add(user_id)
                self.items.add(item_id)
                if user_id not in self.graph:
                    self.graph[user_id] = []
                self.graph[user_id].append((item_id, time_stamp))
        for user_id, value in self.graph.items():
            value.sort(key=lambda x: x[1])
            self.graph[user_id] = [x[0] for x in value]  # uid-》iid的list
        self.users = list(self.users)  # 集合
        self.items = list(self.items)  # 集合
    
    def __next__(self):
        if self.train_flag == 0: # 采样测试，采batch个不同的uid
            user_id_list = random.sample(self.users, self.batch_size)
        else:
            total_user = len(self.users)
            if self.index >= total_user:
                self.index = 0
                raise StopIteration
            user_id_list = self.users[self.index: self.index+self.eval_batch_size]  # 按顺序取batch个user
            self.index += self.eval_batch_size

        item_id_list = []
        hist_item_list = []
        hist_mask_list = []
        for user_id in user_id_list:  # 在一个batch内部，一条是一个user
            item_list = self.graph[user_id]  # 此user所有互动过的item
            if self.train_flag == 0:
                k = random.choice(range(4, len(item_list)))
                item_id_list.append(item_list[k])
            else:
                k = int(len(item_list) * 0.8)  # 所有行为item在80%截断
                item_id_list.append(item_list[k:])   # 后20% 装入item id list
            if k >= self.maxlen:
                hist_item_list.append(item_list[k-self.maxlen: k])  # 保留最近不大于maxlen个 历史item
                hist_mask_list.append([1.0] * self.maxlen)  # maxlen个1，作为保留数据的mask
            else:
                hist_item_list.append(item_list[:k] + [0] * (self.maxlen - k))   # 不足maxlen长时，后面补0
                hist_mask_list.append([1.0] * k + [0.0] * (self.maxlen - k))  # 前面1 后面0，mask的长度总是 maxlen
                
        return (user_id_list, item_id_list), (hist_item_list, hist_mask_list)   #batch里是个list，list每个行，是这个user下，uid，后20% item，前80% his item补长和代表数字存在的mask
