import os
from PIL import Image


def thumbnail(width, height):
	path = '/Users/jing/Pictures/hyf'
	filelist = os.listdir(path+'/original')
	for file in filelist:
		original = os.path.join(path, 'original', file)
		img = Image.open(original)
		img.thumbnail((width, height))
		thumbnail = os.path.join(path, 'thumbnail', 'thumb'+file)
		img.save(thumbnail)

thumbnail(300, 300)