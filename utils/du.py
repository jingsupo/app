# *-*coding:utf8*-*

import sys
import os
from optparse import OptionParser


print(sys.argv)
# 定义选项和帮助信息
usage = sys.argv[0] + " [选项]... [对象]..."
parser = OptionParser(usage)
parser.add_option("-s",
                  dest="sum",
                  action="store_true",
                  default=False,
                  help="统计指定对象的的大小总和")
parser.add_option("-a",
                  dest="autodisplay",
                  action="store_true",
                  default=False,
                  help="根据大小自动显示 k,KB,MB,GB 等单位")
options, args = parser.parse_args()


# 判断文件或目录是否存在
def nofile(i):
    if not os.path.exists(i):
        sys.stderr.write(i + "\tis not exists\n")
        exit(1)


# 定义显示样式
def autodisplay(num):
    float(num)
    if num < 1024:
        return str(num) + "B"
    elif num < 1024 * 1024:
        return str("%.1f" % (num / 1024)) + "K"
    elif num < 1024 * 1024 * 1024:
        return str("%.1f" % (num / 1024 / 1024)) + "M"
    else:
        return str("%.2f" % (num / 1024 / 1024 / 1024)) + "G"


# 统计目录大小
def getsize(i):
    m = 0
    listdir = os.listdir(i)
    for d in listdir:
        path = os.path.join(i, d)
        if os.path.isdir(path):
            m += getsize(path)
        else:
            m += os.path.getsize(path)
    return m


sum = 0
for i in args:
    nofile(i)
    if os.path.isfile(i):
        size = os.path.getsize(i)
        sum += size
        print("%s\t%s" % (autodisplay(sum), i))
    if os.path.isdir(i):
        for x, y, z in os.walk(i):
            size = os.path.getsize(x)  # 对目录本身进行大小统计，和du统计结果有点不太一样
            sum += size
            if options.sum:
                pass
            else:
                if options.autodisplay:
                    print("%s\t%s" % (autodisplay(size), x))
                else:
                    print("%d\t%s" % (size, x))
            for f in z:
                size = os.path.getsize(os.path.join(x, f))  # 对目录里面文件进行大小统计
                sum += size
                if options.sum:
                    pass
                else:
                    if options.autodisplay:
                        print("%s\t%s" % (autodisplay(size), os.path.join(x, f)))
                    else:
                        print("%d\t%s" % (size, os.path.join(x, f)))

        """如果加上-s选项，这里就输入总的大小"""
        if options.sum:
            print("%s\t%s" % (autodisplay(sum), i))
            listdir = os.listdir(i)
            for d in listdir:
                path = os.path.join(i, d)
                if os.path.isdir(path):
                    m = getsize(path)
                    if options.autodisplay:
                        print("%s\t%s" % (autodisplay(m), path))
                    else:
                        print("%d\t%s" % (m, path))
