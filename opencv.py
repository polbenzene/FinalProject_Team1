import cv2
import pickle

image = cv2.imread("parkinglot.png") 

width, height = 45, 90

try:
    with open('Carparkpos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

def mouseclick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x,y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1= pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    with open('Carparkpos', 'wb') as f:
        pickle.dump(posList, f)

while True:
    image = cv2.imread("parkinglot.png")     
    for pos in posList:
        cv2.rectangle(image, pos,(pos[0]+width, pos[1]+height ), (250,0,250), 2)

    cv2.imshow('Test img', image)
    cv2.setMouseCallback("Test img", mouseclick)
    if cv2.waitKey(5) == 27:
        break 
    