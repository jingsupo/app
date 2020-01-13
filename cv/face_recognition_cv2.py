import os
import cv2
import numpy as np

# img = cv2.imread(r'D:\Pictures\02.jpg')
# cv2.imshow('pg', img)
# cv2.waitKey()

def face_detect(img):
    # 将测试图像转换为灰度图像，因为OpenCV人脸检测器需要灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 加载OpenCV人脸检测分类器Haar
    face_cascade = cv2.CascadeClassifier(r'D:\anaconda\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
    # 检测多尺度图像，返回值是一张脸部区域信息的列表(x,y,宽,高)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    # 如果未检测到面部，则返回原始图像
    if len(faces) == 0:
        return None, None
    # 目前假设只有一张脸，xy为左上角坐标，wh为矩形的宽高
    x, y, w, h = faces[0]
    return gray[y:y+w, x:x+h], faces[0]

# 该函数将读取所有的训练图像，从每个图像检测人脸并将返回两个相同大小的列表，分别为脸部信息和标签
def pre_training_data(fp):
    # 获取数据文件夹中的目录（每个主题一个目录）
    dirs = os.listdir(fp)
    # 两个列表分别保存所有的脸部和标签
    faces = []
    labels = []
    for dn in dirs:
        label = int(dn)
        sub_dir_path = fp + '/' + dn
        sub_img_name = os.listdir(sub_dir_path)
        for img_name in sub_img_name:
            img_path = sub_dir_path + '/' + img_name
            # 读取图像
            img = cv2.imread(img_path)
            cv2.imshow('Training on image...', img)
            cv2.waitKey(100)
            # 检测脸部
            face, rect = face_detect(img)
            if face is not None:
                faces.append(face)
                labels.append(label)
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    return faces, labels

faces, labels = pre_training_data('../../../training')
# 创建LBPH识别器并开始训练，当然也可以选择Eigen或者Fisher识别器
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.train(faces, np.array(labels))

# 根据给定的（x，y）坐标和宽度高度在图像上绘制矩形
def draw_rectangle(img, rect):
    x, y, w, h = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (128, 128, 0), 2)

# 根据给定的（x，y）坐标标识出人名
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (128, 128, 0), 2)

# 建立标签与人名的映射列表（标签只能为整数）
subjects = ['jiaju', 'jiaqiang', 'cainaihua', 'saaya']

def predict(test_img):
    # 生成图像的副本，这样就能保留原始图像
    img = test_img.copy()
    # 检测人脸
    face, rect = face_detect(img)
    # 预测人脸
    label = face_recognizer.predict(face)
    print(label)
    # 获取由人脸识别器返回的相应标签的名称
    label_text = subjects[label[0]]
    # 在检测到的脸部周围画一个矩形
    draw_rectangle(img, rect)
    # 标出预测的名字
    draw_text(img, label_text, rect[0], rect[1]-5)
    return img, label_text

# 加载测试图像
# test_img1 = cv2.imread('../../../testing/0.jpeg')
# test_img2 = cv2.imread('../../../testing/1.jfif')
test_img3 = cv2.imread('../../../testing/2.jpg')
test_img4 = cv2.imread('../../../testing/3.jpg')
# 执行预测
# pred_img1, pred_label_text1 = predict(test_img1)
# pred_img2, pred_label_text2 = predict(test_img2)
pred_img3, pred_label_text3 = predict(test_img3)
pred_img4, pred_label_text4 = predict(test_img4)
# 显示图像
# cv2.imshow(pred_label_text1, pred_img1)
# cv2.imshow(subjects[1], pred_img2)
cv2.imshow(subjects[2], pred_img3)
cv2.imshow(subjects[3], pred_img4)
cv2.waitKey()
cv2.destroyAllWindows()
