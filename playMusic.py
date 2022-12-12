from threading import Thread
import cv2
import numpy as np
import sounddevice as sd
import imutils
import random

cap = cv2.VideoCapture(0)
bg = None

playSound = True

imnote = [
        10,10,10,6,1,
        10,6,1,10,
        5,5,5,6,1,
        9,6,1,10,
        10,10,10,10,9,8,
        7,6,8,12,4,3,2,
        1,12,1,6,9,6,9,
        ]
imoctave = [
        4,4,4,4,5,
        4,4,5,4,
        5,5,5,5,5,
        4,4,5,4,
        5,4,4,5,5,5,
        5,5,5,4,5,5,5,
        5,4,5,4,4,4,4,
        ]
imlong = [
        500,500,500,250,250,
        500,250,250,1000,
        500,500,500,250,250,
        500,250,250,1000,
        500,250,250,500,250,250,
        250,250,250,250,500,250,250,
        250,250,250,250,500,250,250,
        ]

class NoteThread(Thread):
    def __init__(self, x, y, nota:int, octava:int, duracion:int):
        super().__init__()
        self.x = x
        self.y = y
        self.nota = nota
        self.octava = octava
        self.duracion = duracion
    def frec(self, nota:int, octava:int)->int:
        expo = octava *12 + (nota-58)
        return int (440* ((2 ** (1/12)) **expo))
    
    def beep(self, nota:int, octava:int, duracion:int)->None:
        framerate = 44100
        t = np.linspace(0, duracion/1000, int (framerate*duracion/1000))
        frequency = self.frec(nota, octava)
        data = np.sin(2*np.pi*frequency*t)
        sd.play(data, framerate)
        sd.wait()
    def run(self):
        global playSound
        playSound = False
        self.beep(self.nota, self.octava, self.duracion)
        playSound = True
notasStarWars = []
def recargarNota():
    global nota
nota = NoteThread(0,0,0,0,0)
class SongThread(Thread):
    def run(self):
        for n, o, d in zip(imnote, imoctave, imlong):
            notasStarWars.append(NoteThread(200,300,n, o, d/2))
            print(n, o, d)
            nota.beep(n, o, d)
testSongThread = SongThread()
#testSongThread.run()
#for i in range(len(notasStarWars)):
#    notasStarWars[i].start()
#    print(i)

# Generar lista de coordenadas donde colocar los circulos
coordsList = []
for i in range(5):
    coordsList.append((random.randint(50,550), random.randint(50,350)))

while True:
    ret, frame = cap.read()
    if ret == False: break
    
    frame = imutils.resize(frame, width=640)
    frame = cv2.flip(frame, 20)
    frameaux = frame.copy()
    
    if bg is not None:
        cv2.imshow('bg', bg)

    #for x in coordsList:
    for i in range(5):
        cv2.circle(frame,(random.randint(50,450), random.randint(50,350)),25,(0,222,255),2)
    cv2.rectangle(frame,(0,0),(640,480),(0,222,255),1)
    
    cv2.imshow('Frame', frame)
    
    key = cv2.waitKey(10)
    
    if key == ord("i"):
        bg = cv2.cvtColor(frameaux, cv2.COLOR_BGR2GRAY)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()