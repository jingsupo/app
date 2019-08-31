# coding: utf-8

import time
from functools import wraps
import numpy as np
import matplotlib.pyplot as plt
from itertools import permutations
import cv2


# 计时装饰器
def timer(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("**********开始**********")
        start = time.time()
        result = function(*args, **kwargs)
        print("**********完成**********")
        end = time.time()
        print('耗时：%ss' % round(end - start, 2))
        return result
    return wrapper


# OpenCV—python RGB颜色直方图
def rgb_hist(path):
    img = cv2.imread(path)
    plt.imshow(np.flip(img, axis=2))
    plt.axis('off')
    plt.show()
    channels = cv2.split(img)  # BGR通道分离
    colors = ('b', 'g', 'r')  # 彩色图有三个通道，通道b:0,g:1,r:2
    plt.figure()
    plt.title('RGB Histogram')
    plt.xlabel('Bins')
    plt.ylabel('# of Pixels')
    for i in [0, 1, 2]:
        histogram = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(histogram, colors[i])
        plt.xlim([0, 256])
    plt.show()

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 九宫格
def nine():
    # 九宫格，从整数1-9中抽取，使每行每列对角线的和都为15
    nums = [i for i in range(1, 10)]
    # itertools模块中permutations方法：穷举参数中的元素，3表示3个元素一组，并过滤出一组内和为15的元素
    seq = [i for i in permutations(nums, 3) if sum(i) == 15]
    # 搜索行、列、对角线均为15的排列组合
    matrix = []
    for r1_1, r1_2, r1_3 in seq:
        for r2_1, r2_2, r2_3 in seq:
            for r3_1, r3_2, r3_3 in seq:
                if (r1_1 + r1_2 + r1_3 == 15
                        and r2_1 + r2_2 + r2_3 == 15
                        and r3_1 + r3_2 + r3_3 == 15
                        and r1_1 + r2_1 + r3_1 == 15
                        and r1_2 + r2_2 + r3_2 == 15
                        and r1_3 + r2_3 + r3_3 == 15
                        and r1_1 + r2_2 + r3_3 == 15
                        and r1_3 + r2_2 + r3_1 == 15):
                    r1 = [r1_1, r1_2, r1_3]
                    r2 = [r2_1, r2_2, r2_3]
                    r3 = [r3_1, r3_2, r3_3]
                    # 去重
                    if len(set(r1) & set(r2)) == 0:
                        if r1 not in matrix:
                            matrix = [r1, r2, r3]
                            print(matrix)


# 单例模式

# 1.使用__new__方法

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


# 2.使用装饰器

def singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return _singleton


# 斐波那契数列

def fibo1(n):
    a, b = 1, 1
    for i in range(n):
        yield a
        a, b = b, a + b


def fibo2(n):
    num = [1, 1]
    for i in range(n-2):
        num.append(num[-1] + num[-2])
    return num


'''
DP算法（动态规划）初试

    假设有一个6 * 6的棋盘，每个格子里面有一个奖品（每个奖品的价值在100到1000之间），现在要求从左上角开始到右下角结束，
每次只能往右或往下走一个格子，所经过的格子里的奖品归自己所有。问最多能收集价值多少的奖品。
    DP算法适用于前一步的决策影响后一步决策的问题。
    本题右下角格子的决策取决于其左边和上面的最优决策，因此，右下角a[i][j]只需要取max(a[i-1][j], a[i][j-1]) + a[i][j]；
其余部分只受左边或者上面的决策影响，因此，横向的a[i][j]应该取a[i][j-1] + a[i][j], 纵向的a[i][j]应该取a[i-1][j] + a[i][j]。
'''


def dp():
    arr = np.zeros((6, 6), dtype=np.int)
    for i in range(6):
        for j in range(6):
            arr[i, j] = np.random.randint(100, 1000)
    print("随机生成一个6*6的二维数组做为棋盘中的权值：")
    print(arr)

    # 首先将第一行和第一列的格子向右或向下累加，除了第一个格子，其余格子的值为前一个格子的值加当前格子的值
    for i in range(1, 6):
        arr[0, i] = arr[0, i - 1] + arr[0, i]
        arr[i, 0] = arr[i - 1, 0] + arr[i, 0]

    # 计算每个格子的最大值
    for i in range(1, 6):
        for j in range(1, 6):
            arr[i, j] = max(arr[i - 1, j], arr[i, j - 1]) + arr[i, j]
    print("变化后的数组：")
    print(arr)


# 排序算法

def bubble_sort(arr):
    # 冒泡排序
    n = len(arr)
    for j in range(n-1):
        # 设置原有数据是否有序的标志
        flag = 0
        # 内层每循环一次，最后的元素变为最大，所以针对所有的元素重复以上步骤的时候要排除最后一个。
        for i in range(n-1-j):
            # 如果相邻的两个数值中前值大于后值，则交换两个数值
            if arr[i] > arr[i+1]:
                arr[i], arr[i+1] = arr[i+1], arr[i]
                flag += 1
        # 内层循环遍历一次后，如果从来没有交换过数据，证明列表已经有序
        if not flag:
            break


def select_sort(arr):
    # 选择排序
    n = len(arr)
    for j in range(n-1):
        # 默认0位置的数据最小
        min_index = j
        for i in range(j+1, n):
            if arr[min_index] > arr[i]:
                # 把更小的数据的位置记录起来
                min_index = i
        # 循环结束时，min_index指向的是最小的数据的位置
        arr[min_index], arr[j] = arr[j], arr[min_index]


def insert_sort(arr):
    # 插入排序
    n = len(arr)
    # 从第2个位置，即下标为1的元素开始向前插入
    for j in range(1, n):
        # 从第j个元素开始向前比较，如果小于前一个元素，交换位置
        for i in range(j, 0, -1):
            if arr[i] < arr[i-1]:
                arr[i], arr[i-1] = arr[i-1], arr[i]
            else:
                break


def quick_sort(arr, start, end):
    # 快速排序
    # 递归的退出条件
    if start >= end:
        return
    # 设定起始元素为要寻找位置的基准元素
    mid = arr[start]
    # 序列左边的由左向右移动的游标
    left = start
    # 序列右边的由右向左移动的游标
    right = end
    while left < right:
        while left < right and arr[right] >= mid:
            right -= 1
        arr[left] = arr[right]
        while left < right and arr[left] < mid:
            left += 1
        arr[right] = arr[left]
    # 退出循环后，low与high重合
    # 将基准元素放到该位置
    arr[left] = mid
    # 对基准元素左边的子序列进行快速排序
    quick_sort(arr, start, left-1)
    # 对基准元素右边的子序列进行快速排序
    quick_sort(arr, left+1, end)


def merge_sort(arr):
    # 归并排序
    # 强制转换list
    if not isinstance(arr, list):
        arr = list(arr)
    # 递归的退出条件
    if len(arr) == 1:
        return arr
    # 二分分解
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    # 递归分解
    left_arr = merge_sort(left)
    right_arr = merge_sort(right)
    # 合并
    result = _merge(left_arr, right_arr)
    return result


def _merge(left, right):
    # 把两个有序序列合并为一个有序序列
    # 定义两个下标指针，分别从0开始
    le = 0
    ri = 0
    result = []
    while le < len(left) and ri < len(right):
        if left[le] <= right[ri]:
            result.append(left[le])
            le += 1
        else:
            result.append(right[ri])
            ri += 1
    result += left[le:]
    result += right[ri:]
    return result


