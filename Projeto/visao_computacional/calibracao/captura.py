import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
path = r'./calibracao/'

if not cap.isOpened():
    print("Cannot open camera")
    exit()

i = 1;    
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # Display the resulting frame
    cv.imshow('frame', frame)

    if cv.waitKey(1) == ord('x'):

        cv.imwrite(path + 'img_' + str(i) + '.jpg', frame)
        print("Foto tirada com sucesso!")
        i += 1
    
    if cv.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
