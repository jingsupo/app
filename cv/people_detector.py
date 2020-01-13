import cv2


def is_inside(o, i):
    ox, oy, ow, oh = o
    ix, iy, iw, ih = i
    return ox > ix and oy > iy and ox + ow < ix + iw and oy + oh < iy + ih


def draw_people(image, people):
    x, y, w, h = people
    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)


img = cv2.imread('2.jpg')
cv2.imshow('haha', img)
cv2.waitKey()

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

found, w = hog.detectMultiScale(img)
print(found, w)

foundlist = []
for i, r in enumerate(found):
    flag = 0
    for ii, q in enumerate(found):
        if i != ii and is_inside(r, q):
            flag = 1
    if flag == 0:
        foundlist.append(r)

for p in foundlist:
    draw_people(img, p)

cv2.imwrite('test.jpg', img)
