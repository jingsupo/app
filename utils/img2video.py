import os
import cv2

path = r'D:\Pictures\picture\\'
filelist = os.listdir(path)
fps = 30 #视频每秒帧数
size = (1920, 1080) #需要转为视频的图片的尺寸

video = cv2.VideoWriter("bar.mp4", 
                        cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)

for item in filelist:
    if item.endswith('.png'):
        item = path + item
        img = cv2.imread(item)
        video.write(img)

video.release()
cv2.destroyAllWindows()
