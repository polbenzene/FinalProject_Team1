from flask import Flask,render_template,Response
import cv2
import pickle
import numpy as np
import cvzone

width, height = 45, 90

app=Flask(__name__)

#video input
camera=cv2.VideoCapture('carpark.mp4')
#camera=cv2.VideoCapture(0)

def generate_frames():
    def checkspaces(imgpro):

        spacecounter = 0

        for pos in posList:
            x,y = pos

            imgcrop = imgpro[y:y+height,x:x+width]

            #cv2.imshow(str(x*y), imgcrop)
            
            count = cv2.countNonZero(imgcrop)
        
            if count < 1350:
                color =(0,255,0)
                thickness = 5
                spacecounter += 1
            else:
                color =(0,0,255,0)
                thickness = 2

                
            cv2.rectangle(frame, pos,(pos[0]+width, pos[1]+height ), color, thickness)
            cvzone.putTextRect(frame,str(count),(x,y+height-5), scale = 1,
            thickness= 1, offset = 0, colorR=color) 
        cvzone.putTextRect(frame,f'Free: {spacecounter}/{len(posList)}',(10,50), scale = 3,
            thickness= 2, offset = 5, colorR=(0,0,255))

    while True:
            
        ## read the camera frame
        if camera.get(cv2.CAP_PROP_POS_FRAMES) == camera.get(cv2.CAP_PROP_FRAME_COUNT):
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success,frame=camera.read()   
        imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(3, 3), 1)
        imgthreshold = cv2.adaptiveThreshold(imgBlur, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 16)

        imgmedian = cv2.medianBlur(imgthreshold,5)
        kernel = np.ones((3,3),np.uint8)
        imgdilate = cv2.dilate(imgmedian,kernel, iterations=1) 
        checkspaces(imgdilate)
        #cv2.imshow("Image", image) 
        #cv2.imshow("Imageblur", imgBlur) 
        #cv2.imshow("Imagethresh", imgmedian)
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

with open('Carparkpos', 'rb') as f:
        posList = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)