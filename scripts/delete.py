
import os
import cv2

data_path = os.path.join('./test.png')

img = cv2.imread(data_path)

# cv2.imshow('Frame view', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

blur = cv2.GaussianBlur(img, (5,5), 0)
canny = cv2.Canny(blur, threshold1=50, threshold2=200)

cv2.imshow('Frame view', canny)
cv2.waitKey(0)
cv2.destroyAllWindows()



