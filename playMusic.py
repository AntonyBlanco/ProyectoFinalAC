from threading import Thread
import cv2
import numpy as np
import sounddevice as sd
import random

global count
count=0
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

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
inlong = [
	400,400,400,200,200,
	400,200,200,1000,
	400,400,400,200,200,
	400,200,200,1000,
	400,200,200,400,200,200,
	200,200,200,200,400,200,200,
	200,200,200,200,400,200,200,
]

playSound = True
class Note(Thread):
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
        self.beep(imnote[count], imoctave[count], inlong[count])
        playSound = True
nota = None

celesteBajo = np.array([75, 185, 88], np.uint8)
celesteAlto = np.array([112, 255, 255], np.uint8)

# Colores a utilizar
colorCeleste = (255,113,82)
colorAmarillo = (89,222,255)
colorRosa = (128,0,255)
colorVerde = (0,255,36)
colorLimpiarPantalla = (29,112,246)

color = colorRosa  # Color de puntero
grosor = 3 # Grosor del marcador del puntero


x1 = None
y1 = None
imAux = None

bol=True
global inc_x
global inc_y

inc_x=0
inc_y=0

interfaz="menu"

# Variables para posiciones aleatorias del objetivo
showSquare = True
rndPositions = []
squaresGap = 100 # Distancia minima entre cada par de posiciones
def reFillSquarePositions():
    global rndPositions
    rndPositions.clear()
    # Algoritmo que evita sobreposicion entre 2 posiciones seguidas
    for i in range(len(imnote)):
        x = random.randint(0, 490)
        if i != 0:
            xDiff = abs(rndPositions[i-1][0] - x)
        if i != 0 and xDiff < squaresGap:
            co = (squaresGap**2 - xDiff**2) ** 0.5
            co = int(co)
            yBottom = rndPositions[i-1][1] - co
            yTop = rndPositions[i-1][1] + co
            if yTop >= 280:
                y = random.randint(0, yBottom)
            elif yBottom <= 0:
                y = random.randint(yTop, 280)
            else:
                y = random.randint(0, 280 - (2*co))
                if y > yBottom: y += 2*co
        else:
            y = random.randint(0, 280)
        rndPositions.append((x, y))
# Calcula a modo de cuadrado si un pointCoords está dentro del circulo
def coordsInCircle(circleCoords, radius, pointCoords):
    radius *= 0.8667 # Constante que asemeja un cuadrado a un circulo
    return circleCoords[0] + radius > pointCoords[0] and\
        circleCoords[0] - radius < pointCoords[0] and\
        circleCoords[1] + radius > pointCoords[1] and\
        circleCoords[1] - radius < pointCoords[1]
reFillSquarePositions()
indexRndPosition = 0

while True:

    ret,frame = cap.read()
    if ret==False: break

    frame = cv2.flip(frame,1)
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if imAux is None: imAux = np.zeros(frame.shape,dtype=np.uint8)

    # Detección del color celeste
    maskCeleste = cv2.inRange(frameHSV, celesteBajo, celesteAlto)
    maskCeleste = cv2.erode(maskCeleste,None,iterations = 1)
    maskCeleste = cv2.dilate(maskCeleste,None,iterations = 2)
    maskCeleste = cv2.medianBlur(maskCeleste, 13)
    cnts,_ = cv2.findContours(maskCeleste, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
    if interfaz == "menu":
        cv2.rectangle(frame,(130,120),(430,220),colorAmarillo,2)
        cv2.rectangle(frame,(430,120),(530,220),colorAmarillo,3)
        cv2.putText(frame,"TUTORIAL",(160,190),4,1.5,colorVerde,3,cv2.LINE_AA)
        cv2.rectangle(frame,(130,230),(430,330),colorAmarillo,2)
        cv2.rectangle(frame,(430,230),(530,330),colorAmarillo,3)
        cv2.putText(frame,"JUGAR",(200,300),4,1.5,colorVerde,3,cv2.LINE_AA)
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if 430 < x2 < 530 and 230 < y2 < 330:
                        interfaz="juego"
                        playingBGMusic = False
                    if 430 < x2 < 530 and 120 < y2 < 220:
                        interfaz="tutorial"
                        playingBGMusic = False
                cv2.circle(frame,(x2,y2),grosor,color,5)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "juego":
        if indexRndPosition == len(rndPositions):
            print("Ganaste :D")
            indexRndPosition = 0
            break
        if showSquare: # bol
            inc_x = rndPositions[indexRndPosition][0]
            inc_y = rndPositions[indexRndPosition][1]
            showSquare=False
        cv2.rectangle(frame,(50,100), (590, 430), colorRosa, 2)
        sa=str(count)
        cv2.putText(frame,sa,(570,50),6,2,colorLimpiarPantalla,3,cv2.LINE_AA)
        cv2.putText(frame,"SCORE",(550,80),6,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(40,40),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(43,43),4,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(40,80),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(43,83),4,0.8,colorCeleste,2,cv2.LINE_AA)

        # Dibujo de la nota en pantalla
        cv2.circle(frame,(75+inc_x,125+inc_y),25,colorRosa,2)
        
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if coordsInCircle((75+inc_x, 125+inc_y), 25, (x2, y2)):
                        if playSound:
                            nota = Note()
                            nota.start()
                        showSquare=True
                        count += 1
                        indexRndPosition = (indexRndPosition + 1)
                        break
                    if 0 < y2 < 60 or 0 < y1 < 60 :
                        imAux = imAux
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "tutorial":
        tutorialImg = cv2.imread("./TutorialInteraccion.png")
        frame = tutorialImg
        cv2.rectangle(frame, (6, 6), (42, 42), colorRosa, 2)
        cv2.line(frame, (14, 14), (34, 34), colorRosa, 2)
        cv2.line(frame, (14, 34), (34, 14), colorRosa, 2)
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if 6 < x2 < 42 and 6 < y1 < 42:
                        interfaz = "menu"
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None

    imAuxGray = cv2.cvtColor(imAux,cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(imAuxGray,10,255,cv2.THRESH_BINARY)
    thInv = cv2.bitwise_not(th)
    frame = cv2.bitwise_and(frame,frame,mask=thInv)
    frame = cv2.add(frame,imAux)

    cv2.imshow('Game', frame)

    k = cv2.waitKey(1)
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()