import os
import re


# path = input('请输入要搜索的路径：')
# name = input('请输入要查找的名字：')

path = 'D:/'
name = r'vc_redist'

ret = []

pattern = re.compile(name, re.I)
for root, dirs, files in os.walk(path):
    for dir in dirs:
        ret.append(os.path.join(root, dir))
    for file in files:
        ret.append(os.path.join(root, file))
for r in ret:
    # print(r)
    if pattern.findall(r):
        print(r)
