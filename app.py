#################  Nares & Chanin     ################
################# Automatio Engineer  ################
################# Smart Door project  ################
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, redirect, request, Response
from time import sleep
import time
from threading import Thread, Event
from flask_jsglue import JSGlue
import cv2, numpy as np, dlib, pickle
import serial
import datetime
from parinya import LINE
line = LINE('4kFK3UTAKoGl3sQfg0BX8mx5dXRtngml5qht5UGY8JC')

app = Flask(__name__)

jsglue = JSGlue(app)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread = Thread()
thread_stop_event = Event()

state_door = 0
turnonfan = 0
state_pump = 0
dutycircle =  30

frequency_r  = 10
guest = 0

def gen():
    global state_door
    global turnonfan
    global guest
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    FACE_DESC, FACE_NAME = pickle.load(open('trainset.pk','rb'))
    tracker = cv2.TrackerMedianFlow_create()
    onTracking = False
    cap = cv2.VideoCapture(0)
    while(True):

        ret, frame = cap.read()
        if onTracking == False:
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray,1.1,4)
            for (x,y,w,h) in faces:
                img = frame[y-10:y+h+10,x-10:x+w+10][:,:,::-1]
                dets = detector(img, 1)
                for k, d in enumerate(dets):
                    shape = sp(img,d)
                    face_desc0 = model.compute_face_descriptor(img, shape, 1)
                    distance = []
                    for face_desc in FACE_DESC:
                        distance.append(np.linalg.norm(np.array(face_desc)-np.array(face_desc0)))
                    distance = np.array(distance)
                    idx = np.argmin(distance)
                    if distance[idx] < 0.4:
                        name = FACE_NAME[idx]
                        cv2.putText(frame,name,(x,y-5),cv2.FONT_HERSHEY_DUPLEX,1,(255,255,255),2)
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                        state_door = 1
                        turnonfan = 1
                        if tracker.init(frame,(x, y, w, h)):
                            onTracking = True
                    else:
                        line.sendtext("guest coming")
                        line.sendimage(frame[y-10:y+h+10,x-10:x+w+10,::-1])
                        cv2.putText(frame,"guest",(x,y-5),cv2.FONT_HERSHEY_DUPLEX,1,(255,255,255),2)
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                        if tracker.init(frame,(x, y, w, h)):
                            onTracking = True
                        
        else:
            ok, bbox = tracker.update(frame)
            if ok:
                p1 = (int(bbox[0]),int(bbox[1]))
                p2 = (int(bbox[0]+bbox[2]),int(bbox[1]+bbox[3]))
                img = frame[int(bbox[1]):int(bbox[1]+bbox[3]),int(bbox[0]):int(bbox[0]+bbox[2])][:,:,::-1]
                dets = detector(img, 1)
                for k, d in enumerate(dets):
                    shape = sp(img,d)
                    face_desc0 = model.compute_face_descriptor(img, shape, 1)
                    distance = []
                    for face_desc in FACE_DESC:
                        distance.append(np.linalg.norm(np.array(face_desc)-np.array(face_desc0)))
                    distance = np.array(distance)
                    idx = np.argmin(distance)
                    if distance[idx] < 0.4:
                        name = FACE_NAME[idx]
                        cv2.putText(frame,name,(int(bbox[0]),int(bbox[1]-5)),cv2.FONT_HERSHEY_DUPLEX,1,(255,255,255),2)
                        cv2.rectangle(frame,p1,p2,(0,255,0),2)
                        guest = 0
                        
                        
                    else:
                        cv2.putText(frame,"guest",(int(bbox[0]),int(bbox[1]-5)),cv2.FONT_HERSHEY_DUPLEX,1,(255,255,255),2)
                        cv2.rectangle(frame,p1,p2,(0,0,255),2)
                        guest = 1
                        
            else:
                onTracking = False
                guest = 0
                tracker = cv2.TrackerMedianFlow_create()

        frame1 = cv2.resize(frame,(0,0),fx=1.0,fy=1.0)
        frame2 = cv2.imencode('.jpg',frame1)[1].tobytes()
        yield (b'--frame2\r\n'b'Content-type: image/jpeg\r\n\r\n'+frame2+b'\r\n')
        time.sleep(0.1)

def realtimeapp():
   
    global state_door, frequency_r, dutycircle, guest, turnonfan
    global state_pump
    port = serial.Serial("COM3",115200)
    while not thread_stop_event.isSet():
        if state_door ==1:
            port.write(b"UNLOCK\r\n")
            led0 = int(port.readline().decode()[-3])
            state_door=0
            
        else:
            port.write(b"LED0_READ\r\n")
            led0 = int(port.readline().decode()[-3])

        if state_pump ==1:
            port.write(b"PUMP\r\n")
            led2 = int(port.readline().decode()[-3])
            state_pump=0
            
        else:
            port.write(b"LED2_READ\r\n")
            led2 = int(port.readline().decode()[-3])

        period  = int(1000/frequency_r)
        duty_r = int((dutycircle*10)/frequency_r)
        PWM_C = "PWM0,"+str(period)+","+str(duty_r)+"\r\n"
        
        if turnonfan==1:
            port.write(PWM_C.encode())
        elif turnonfan==0:
            PWM_OFF = "PWM0,"+str(1000)+","+str(0)+"\r\n"
            port.write(PWM_OFF.encode())
            

        port.write(b"ADC0_READ\r\n")
        humidity = float(port.readline().decode()[5:])
        port.write(b"ADC1_READ\r\n")
        pm = float(port.readline().decode()[5:])
        port.write(b"ADC2_READ\r\n")
        airtemp = float(port.readline().decode()[5:])
        port.write(b"ADC3_READ\r\n")
        bodytemp = float(port.readline().decode()[5:])

        raw_time = datetime.datetime.now()
        pm_am = str(raw_time.strftime("%p"))
        now = str(raw_time).split(" ")
        date = now[0]
        time = now[1][:5]+' '+pm_am

        

        port.write(b"PSW0_READ\r\n")
        psw0 = int(port.readline().decode()[-3])
        port.write(b"PSW1_READ\r\n")
        psw1 = int(port.readline().decode()[-3])
        port.write(b"PSW2_READ\r\n")
        psw2 = int(port.readline().decode()[-3])
        if psw2 == 1:
            turnonfan = 0

        socketio.emit('statefan', {'data': turnonfan}, namespace='/INC362')
        socketio.emit('guest', {'data': guest}, namespace='/INC362')
        socketio.emit('state', {'data': led0}, namespace='/INC362')
        socketio.emit('state_pump', {'data': led2}, namespace='/INC362')
        socketio.emit('humiditydata', {'data': humidity}, namespace='/INC362')
        socketio.emit('pmdata', {'data': pm}, namespace='/INC362')
        socketio.emit('airtempdata', {'data': airtemp}, namespace='/INC362')
        socketio.emit('bodytempdata', {'data': bodytemp}, namespace='/INC362')
        socketio.emit('nowdate', {'data': date}, namespace='/INC362')
        socketio.emit('nowtime', {'data': time}, namespace='/INC362')
        socketio.emit('statepsw0', {'data': psw0}, namespace='/INC362')
        socketio.emit('statepsw1', {'data': psw1}, namespace='/INC362')
        socketio.emit('statepsw2', {'data': psw2}, namespace='/INC362')
        socketio.sleep(0.5)



@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/INC362')
def test_connect():
    global thread
    print('Client connected')
    if not thread.isAlive():
        thread = socketio.start_background_task(realtimeapp)

@socketio.on('unlock', namespace='/INC362')
def unlock(response):
    global state_door
    state_door = response


@socketio.on('pump', namespace='/INC362')
def Pump(response):
    global state_pump
    state_pump = response


@socketio.on('frequency', namespace='/INC362')
def frequency(response):
    global frequency_r
    frequency_r = response
   

@socketio.on('duty', namespace='/INC362')
def duty(response):
    global dutycircle
    dutycircle = response


@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame2')


if __name__ == '__main__':
    socketio.run(app)


