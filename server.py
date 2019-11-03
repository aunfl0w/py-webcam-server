#!/usr/bin/python3
import io
import socket
import cv2 as cv
import re
import sys
import atexit
from PIL import Image


def camServer():
    while True:
        socket, addr = serverSocket.accept()
        if socket:
            socketFile = socket.makefile('rwb')
            break

    try:
        request = socketFile.readline().decode('utf-8')        
        if request.find('image.jpg HTTP') == -1:
            socketFile.write(b'HTTP/1.0 200 OK\n\n')
            socketFile.write(b'bad request')           
            print("BAD : {}: {}".format(addr[0], request), end='')
            return
        
        print("GOOD: {}: {}".format(addr[0], request), end='')

        cam = cv.VideoCapture(0)
        cam.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
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
serverSocket.listen(0)
serverSocket.setblocking(1)

def cleanup():
    print("\nClosed Server")

atexit.register(cleanup)

print("Starting server for requests ending in image.jpg on port 8100")
while True:
    try: 
        camServer()
    except KeyboardInterrupt:
        sys.exit(0)
        
