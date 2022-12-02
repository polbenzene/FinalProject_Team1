from flask import Flask,render_template,Response,session,request,redirect,g,url_for
#from flask_ngrok import run_with_ngrok
import cv2
import pickle
import os

#counters for parking_availability
counter = 0 
occupied = 0

app=Flask(__name__)
#run_with_ngrok(app)
app.secret_key = os.urandom(24)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['password'] == 'password':
            session['user'] = request.form['username']
            return redirect(url_for('protected'))

    return render_template('LoginPage.html')

@app.route('/protected')
def protected():
    if g.user:
        return render_template('index.html',user=session['user'])
    return redirect(url_for('protected'))

@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']

#video source
cap = cv2.VideoCapture('carpark.mp4')

#parking space postions
with open('park_positions', 'rb') as f:
    park_positions = pickle.load(f)

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# Parking space parameters
width, height = 45, 90
full = width * height
empty = 0.22

def generate_frames():
    def parking_space_counter(img_processed):
        global counter, occupied

        counter = 0
        occupied = 0

        for position in park_positions:
            x, y = position

            img_crop = img_processed[y:y + height, x:x + width]
            count = cv2.countNonZero(img_crop)

            ratio = count / full

            if ratio < empty:
                color = (0, 255, 0)
                counter += 1
            else:
                color = (0, 0, 255)

            cv2.rectangle(overlay, position, (position[0] + width, position[1] + height), color, -1)
            #cv2.putText(overlay, "{:.2f}".format(ratio), (x + 4, y + height - 4), font, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        occupied = len(park_positions) - counter    

    while True:

        # Video looping
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, frame = cap.read()
        overlay = frame.copy()

        # Frame processing
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

        parking_space_counter(img_thresh)
        alpha = 0.7
        frame_new = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        #w, h = 220, 60
        #cv2.rectangle(frame_new, (0, 0), (w, h), (255, 0, 255), -1)
        #cv2.putText(frame_new, f"{counter}/{len(park_positions)}", (int(w / 10), int(h * 3 / 4)), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        #cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  
        
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame_new)
            frame_new=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_new + b'\r\n')
                   
#website 
@app.route('/')
def login():
    return render_template('LoginPage.html', )

#processed parking lot video
@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

#available space count
@app.route('/count')
def count():
    p = counter
    return (str(p))

#occupied space count
@app.route('/occupied')
def occcupied():
    o = occupied
    return (str(o))

if __name__ == '__main__':
    app.run()

       