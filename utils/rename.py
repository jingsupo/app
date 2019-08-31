import os


def rename():
	i = 0
	path = '/Users/jing/Pictures/hyf'
	filelist = os.listdir(path)  #列出改路径下的所有文件（包括文件夹）
	for file in filelist:
		i += 1
		olddir = os.path.join(path, file)  #原来的文件路径
		if os.path.isdir(olddir):  #如果是文件夹则跳过
			continue
		filename = os.path.splitext(file)[0]  #文件名
		filetype = os.path.splitext(file)[1]  #文件扩展名
		newdir = os.path.join(path, str(i)+filetype)  #新的文件路径
		os.rename(olddir, newdir)  #重命名

rename()