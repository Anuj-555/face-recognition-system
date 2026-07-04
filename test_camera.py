import cv2

cam = cv2.VideoCapture(0)

ret, frame = cam.read()

if ret:
    print("Camera working")
else:
    print("Camera not working")

cam.release()