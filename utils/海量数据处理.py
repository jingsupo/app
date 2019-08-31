from collections import Counter
import os
import random
import numpy as np
import redis
from memory_profiler import profile


# """
# Top-k的最小堆解决方法
# 问题描述：有N(N>>10000)个整数,求出其中的前K个最大的数。（称作Top k或者Top 10）
#
# 问题分析：由于(1)输入的大量数据；(2)只要前K个，对整个输入数据的保存和排序是相当的不可取的。
#
# 可以利用数据结构的最小堆来处理该问题。
#
# 最小堆如图所示，对于每个非叶子节点的数值，一定不大于孩子节点的数值。这样可用含有K个节点的最小堆来保存K个目前的最大值(当然根节点是其中的最小数值)。
#
# 每次有数据输入的时候可以先与根节点比较。若不大于根节点，则舍弃；否则用新数值替换根节点数值。并进行最小堆的调整。
# """
#
#
# def heap_sort(arr, k):
#     # 构建小顶堆
#     def siftdown(arr, start, end):
#         i, j = start, start*2+1
#         while j < end:
#             # 查看左右子树最小节点
#             if j+1 < end and arr[j+1] < arr[j]:
#                 j += 1
#             # 如果不需要交换则停止
#             if arr[i] < arr[j]:
#                 break
#             # 交换父子
#             arr[i], arr[j] = arr[j], arr[i]
#             i, j = j, j*2+1
#
#     # 构建最小堆
#     end = len(arr)
#     for i in range(end//2-1, -1, -1):
#         siftdown(arr, i, end)
#     # print('小顶堆', arr)
#
#     # 提取k个元素，每提取一个元素，构建一遍最小堆
#     li = []
#     for i in range(k):
#         if len(arr) > i:
#             # 取出最小的
#             li.append(arr[0])
#             # 最后一个与第一个交换，这里只是假设。
#             arr[end-1-i], arr[0] = arr[0], arr[end-1-i]
#             # 重新构建堆，不考虑最后一个
#             siftdown(arr, 0, end-1-i)
#         else:
#             break
#     return li
#
#
# b = np.random.randint(0, 1000000, 1000000)
# print(sorted(b)[:10])
# print(heap_sort(b, 10))


# # 大文件分割
# # -*- coding:utf-8 -*-
# from datetime import datetime
#
#
# def split_file(source_dir, target_dir):
#     source_dir = source_dir
#     target_dir = target_dir
#
#     # 计数器
#     flag = 0
#
#     # 文件名
#     name = 1
#
#     # 存放数据
#     datalist = []
#
#     print("**********文件分割开始**********")
#     print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#
#     with open(source_dir, 'r') as f_source:
#         for line in f_source:
#             flag += 1
#             datalist.append(line)
#             if flag == 2000000:
#                 with open(target_dir + str(name) + ".txt", 'w+') as f_target:
#                     for data in datalist:
#                         f_target.write(data)
#                 name += 1
#                 flag = 0
#                 datalist = []
#
#     # 处理最后一批行数少于200万行的
#     with open(target_dir + str(name) + ".txt", 'w+') as f_target:
#         for data in datalist:
#             f_target.write(data)
#
#     print("**********文件分割完成**********")
#     print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#
#
# if __name__ == "__main__":
#     source_dir = input('请输入源文件：')
#     target_dir = input('请输入目标文件夹：')
#     split_file(source_dir, target_dir)


# 分而治之/哈希映射
def split_file(file, path='D:/data/data/'):
    # 大文件路径
    bigfile = file
    # 小文件存放路径
    path = path
    if not os.path.exists(path):
        os.mkdir(path)
    # 要分割的文件数
    num = 100
    # 要分割的文件对象存放列表
    f_list = []
    # 创建num个文件对象放入列表
    for i in range(num):
        f_list.append(open(path + str(i) + '.txt', 'a'))
    # 读取大文件
    with open(bigfile, 'r') as f_source:
        for line in f_source:
            # 求哈希值的模
            h = hash(line) % num
            # 按哈希值的模对应的文件将每行写入文件
            f_list[h].write(line)
    # 关闭所有文件对象
    for f in f_list:
        f.close()


# 生成随机整数
def gen_int(n=1):
    return np.random.randint(0, int(n), int(n))


# 生成随机IP
def gen_ip(n=1):
    for _ in range(n):
        yield '10.10.'+str(random.randint(0, 255))+'.'+str(random.randint(0, 255))


# 写入文件
def write(path, array):
    with open(path, 'w') as f:
        for n in array:
            f.write(str(n)+'\n')


# 打印
def print_file(path):
    with open(path) as f:
        for line in f:
            print(line)
            # pass


# 元素频次统计
def count(path):
    res = Counter()
    with open(path) as f:
        f_list = f.readlines()
        common_100 = Counter(f_list).most_common(100)
        res.update(common_100)
    return res


def mcount(path):
    res = Counter()
    for root, dirs, files in os.walk(path):
        for file in files:
            fp = os.path.join(root, file)
            print(fp)
            with open(fp) as f:
                f_list = f.readlines()
                common_100 = Counter(f_list).most_common(100)
                res.update(common_100)
    return res


# 连接redis
def to_redis(path):
    r = redis.Redis(host='192.168.75.150')
    # 建立管道，批量插入，一次或多次提交，提升速度
    with r.pipeline() as p:
        with open(path) as f:
            interval = np.arange(100, 1000, 100)*10000
            for index, line in enumerate(f):
                p.setbit('int', int(line), 1)
                if index in interval:
                    p.execute()
        p.execute()


def to_redis2(path):
    r = redis.Redis(host='192.168.75.150', db=1)
    # 建立管道，批量插入，一次或多次提交，提升速度
    with r.pipeline() as p:
        with open(path) as f:
            interval = np.arange(100, 1000, 100)*10000
            for index, line in enumerate(f):
                v0 = r.getbit(line, 0)
                v1 = r.getbit(line, 1)
                if v0 == 0 and v1 == 0:
                    p.setbit(line, 1, 1)
                elif v0 == 0 and v1 == 1:
                    p.setbit(line, 0, 1)
                    p.setbit(line, 1, 0)
                else:
                    pass
                if index in interval:
                    p.execute()
        p.execute()


@profile
def run():
    # arr = gen_int(10000000)

    # ip = gen_ip(100000000)

    # write('D:/data/ip.txt', ip)

    # print_file('D:/data/ip.txt')

    # split_file('D:/data/ip.txt')

    # res = mcount('D:/data/data')
    # print(sorted(res.keys(), key=lambda x: x[1], reverse=True)[:10])

    # print("开始写入redis...")
    # to_redis('D:/data/int1.txt')  # 1000万个整数，使用管道，只提交1次时：耗时266.25s，内存占用4G，增加提交次数后：耗时221.99s，内存占用1G
    # print("写入redis完成...")

    pass


run()
