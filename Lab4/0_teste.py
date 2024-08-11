import cv2

cams = []
for i in range(10):
    camera = cv2.VideoCapture(i)
    if camera.isOpened():
        cams.append((i, camera))
    camera.release()
    
for cam_index, cam in cams:
    print(f"Camera {cam_index}: {cam.get(3)}")
