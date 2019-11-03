#!/usr/bin/python3
import io
import socket
import cv2 as cv
import re
import sys
import atexit
from datetime import datetime
from PIL import Image

def getTimestamp():
    now = datetime.now()
    return now.strftime('%Y-%m-%d-%H:%M:%S %Z')


def camServer():
    while True:
        socket, addr = serverSocket.accept()
        if socket:
            socketFile = socket.makefile('rwb')
            break

    try:
        request = socketFile.readline().decode('utf-8')
        request = request.replace('\n','')
        request = request.replace('\r','')
        if request.find('image.jpg HTTP') == -1:
            socketFile.write(b'HTTP/1.0 404 OK\n\n')
            
            print("{} {} {} 404".format(addr[0], getTimestamp(), request))
            return
        
        print("{} {} {} 200".format(addr[0], getTimestamp(), request))

        cam = cv.VideoCapture(0)
        cam.set(cv.CAP_PROP_FRAME_WIDTH, 960)
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        data, imgHSV = cam.read()
        if data:
            imgRGB = cv.cvtColor(imgHSV, cv.COLOR_BGR2RGB)
            imgPIL = Image.fromarray(imgRGB)
            memFile = io.BytesIO()
            imgPIL.save(memFile, format="jpeg")
            memFile.seek(0)
            socketFile.write(b'HTTP/1.0 200 OK\n')
            socketFile.write(b'Content-Type: image/jpeg\n')
            socketFile.write(b'\n')
            socketFile.write(memFile.read())
            memFile.close()
            cam.release()
    finally:
        socketFile.flush()
        socketFile.close()
        socket.close()


serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('0.0.0.0', 8100))
serverSocket.listen(1)
serverSocket.setblocking(1)

def cleanup():
    print("\nClosed Server")

atexit.register(cleanup)

print("Starting server for requests ending in image.jpg on port 8100")
while True:
    try: 
        camServer()
    except BrokenPipeError as e:
        print(e)
    except KeyboardInterrupt:
        sys.exit(0)
        
