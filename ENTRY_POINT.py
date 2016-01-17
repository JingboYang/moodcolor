'''/* -*- mode: python; indent-tabs-mode: nil; tab-width: 4 -*- */'''

import sys, pygame, string, time
from pygame.locals import *
import gtk
import math
from indico_analysis import Analysis
import pprint
from plot import Plotter
from cv2.cv import *
import cv2
import numpy as np
import Tkinter as tk
import tkFileDialog
import copy


#######Environment Variables########
AQUA =(0,255,255)
BLACK =(0,0,0)
Fuchsia = (255,0,255)
GREY = (128,128,128)
LIME = (0,255,0)
MAROON = (128,0,0)
NAVYBLUE =(0,0,128)
OLIVE = (128,128,0)
PURPLE = (128,0,128)
RED =(255,0, 0)
SILVER =(192,192,192)
TEAL = (0,128,128)
YELLOW = (255,255,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLUE = (0,0,128)
CYAN = (0,255,255)
#######End Environment Variables########



#######Parameters########
text_xaxis = 20
text_yaxis = 80
#######End Parameters########



#######Global Variables########
inString = ""
inStringList = []
textInputList = []
#######End Global Variables########


#######Methods########
def updatetext():
    i = 0
    char_max = 52
    inStringList = []
    global textInputList
    textInputList = []
    while len(inString)> char_max*i:
        inStringList.append ( inString[i*char_max: min((i+1)*char_max,len(inString))] )
        i += 1
    for i in range (0,len(inStringList)):
        tempSurface = fontObj.render(inStringList[i], True, AQUA)
        tempRectObj = tempSurface.get_rect()
        tempRectObj.top = text_yaxis + 20*i
        tempRectObj.left = 15
        textInputList.append([tempSurface,tempRectObj])


def paragraphSplitter(text):
    
    delimiters = ['.', '"', ';', ':', '\n', '?', '!', '[', ']', ',', '(', ')', '"', "'"]

    sent = ""
    sentences = []

    last = True
    for a in text:

        sent = sent + a
        if a in delimiters:
            sentences.append(sent.replace('\n', ''))
            sent = ""
            last = False

    if last:
        sentences.append(sent.replace('\n', ''))

    # sentences = filter(None, sentences)
    return emptyCleanUp(sentences)

def resultSynthesizer(inList):
    
    result = []
    for i in range(1, len(inList[0]) + 1):
        result.append(i)

    result = [result, inList[0], inList[1], inList[2], inList[3], inList[4], inList[5], inList[6], inList[7], inList[8]]

    return result
    

def emptyCleanUp(items):
    
    # print items

    result = []
    for a in items:
        b = a
        b = b.replace(' ', '')
        b = b.replace('\t', '')
        # print b
        # print len(b)
        if len(b) != 0:
            result.append(a)

    return result


def transform_image(image999, parama, paramb, paramc):

    hsv_image = cv2.cvtColor(image999, CV_BGR2HSV)
	
    averages = cv2.mean(hsv_image)[0:3]
    desired_averages = (averages[0]/4.0 + parama*(255.0*3/4.0 + averages[0]*3/4.0),  averages[1]/4.0 + paramb*(255.0*3/4.0 + averages[1]*3/4.0), averages[2]/4 + paramc*(255.0*3/4.0 + averages[2]*3/4.0))
    rows, cols =  len(hsv_image), len(hsv_image[0])
	
    vectorize_hsv_mod = np.vectorize(hsv_mod)
    h,s,v = cv2.split(hsv_image)

    h2 = vectorize_hsv_mod(h, desired_averages[0])
    s2 = vectorize_hsv_mod(s, desired_averages[1])
    v2 = vectorize_hsv_mod(v, desired_averages[2])

    hsv_array = cv2.merge([h2, s2, v2])
    return cv2.cvtColor(hsv_array, CV_HSV2BGR)
	
def hsv_mod(value, desired):
	return np.uint8(value + (value/255.0)*((255.0-value)/255.0)*(desired-value))

def processImage(imageOLD, oldScore, newScore):

    #newScore = 1 - newScore

    imageP = copy.deepcopy(imageOLD)

    #xmin = 140
    #xmax = 260
    xmin = 158
    xmax = 278
    xhalf = (xmin + xmax) / 2
    xhalf2 = (xmax - xmin) /2
    #yzero = 270
    #ydistort = 20
    yzero = 255
    ydistort = 18

    oldC = (oldScore - 0.5) / 0.5 * ydistort
    oldA = -oldC / (xhalf2 * xhalf2)

    newC = (newScore - 0.5) / 0.5 * ydistort
    newA = -newC / (xhalf2 * xhalf2)

    # print (newA, newC)

    for x in range(xmin, xmax):        
        arrB = []
        arrG = []
        arrR = []
        for y in range(int(yzero - ydistort * 1.5), int(yzero + ydistort * 1.5)):
            arrB.append(imageP[y][x][0])
            arrG.append(imageP[y][x][1])
            arrR.append(imageP[y][x][2])
        
        tempX = x - xhalf
        tempX2 = tempX * tempX
        oldCenter = oldA * tempX2 + oldC + 1.5 * ydistort
        newCenter = newA * tempX2 + newC + 1.5 * ydistort

        # print (oldCenter, newCenter, len(arrB), tempX2)

        newB = newDistort(arrB, oldCenter, newCenter, len(arrB))
        newG = newDistort(arrG, oldCenter, newCenter, len(arrG))
        newR = newDistort(arrR, oldCenter, newCenter, len(arrR))

        offset = int(yzero - ydistort * 1.5)
        for y in range(int(yzero - ydistort * 1.5), int(yzero + ydistort * 1.5)):
            imageP[y][x][0] = newB[y - offset]
            imageP[y][x][1] = newG[y - offset]
            imageP[y][x][2] = newR[y - offset]
            #imageP[y][x][0] = 255
            #imageP[y][x][1] = 255
            #imageP[y][x][2] = 255
    
    
    #cv2.rectangle( imageP,
    #       ( xmin, int(yzero - ydistort * 1.5)),
    #       ( xmax, int(yzero + ydistort * 1.5)),
    #       ( 0, 255, 255 ),  3);

    return imageP

def newDistort(oldArray, oldCenter, newCenter, newlen):

	oldRight = len(oldArray) - oldCenter
	newRight = newlen - newCenter

	result = []

	for x in range (0, newlen):
		if x < newCenter:
			oldX = oldCenter + oldCenter * (x - newCenter) / float(newCenter)
		else:
			oldX = oldCenter + oldRight * (x - newCenter) / float(newRight) 
	
		if oldX < 0:
			oldX = 0
		elif oldX >= len(oldArray) - 1:
			oldX = len(oldArray)-2
			print oldX

		# print oldX
		oldArray[int(oldX)]

		value = float(oldArray[int(oldX)]) + float((oldX - int(oldX))) * (float(oldArray[int(oldX) + 1]) - float(oldArray[int(oldX)]))
		result.append(value)
	return result
#######End Methods########



#######Main########
# setup()

doFace = False

if len(sys.argv) == 2 and sys.argv[1] == '-face':
    doFace = True
else:
    root = tk.Tk()
    root.withdraw()
    file_path = tkFileDialog.askopenfilename()

    print file_path

pygame.init()
screenSize = swidth, sheight = 1000, 720
DISPLAYSURF = pygame.display.set_mode(screenSize)
pygame.display.set_caption('Mood Color')
pygame.font.init()

#fontObj = pygame.font.Font('freesansbold.ttf',32)

fontObj = pygame.font.Font("RopaSans-Regular.ttf", 22, bold=True)
fontObj2 = pygame.font.Font("RopaSans-Regular.ttf", 36, bold=True)
textSurfaceObj2 = fontObj2.render('Welcome to Mood Color', True, (255, 102, 0))
textRectObj2 = textSurfaceObj2.get_rect()
textRectObj2.center = (swidth / 2, 40)

indicoStuff = Analysis()
pp = pprint.PrettyPrinter(indent=4)

pt = Plotter(500, 450, 480, 250, DISPLAYSURF, 'Sentiment Analysis')

x = [1,2,3,4,5,6,7,8,9]
y = [2,4,2,1,5,7,8,2,0]

x2 = [3,6,9]
y2 = [1,4,8]

#pt.getData(x, y)
#pt.getData2(x2,y2)

counter = 0
counter2 = 0

t1 = time.time()
t2 = time.time()

#wordResult = [[],[],[],[],[],[],[],[],[]]
#sentResult = [[],[],[],[],[],[],[],[],[]]

wordResult = [[], []]
sentResult = [[], []]

'''
word = []
wordSentiment = []
wordPersonality = []
wordPolitical = []

sent = []
sentSentiment = []
sentPersonality = []
sentPolitical = []
'''

pygame.scrap.init()
clipboard = gtk.clipboard_get()

prevScore = 0.5
if doFace == False:
    ball = pygame.image.load(file_path)

    img = cv2.imread(file_path)

    ballrect = ball.get_rect()
    ballrect = ballrect.move(550, 80)

    image2 = cv2.resize(img, (420, 350));
else:
    ball = pygame.image.load('face2.jpg')

    img = cv2.imread('face2.jpg')

    ballrect = ball.get_rect()
    ballrect = ballrect.move(550, 80)

    image2 = cv2.resize(img, (420, 350));

image4 = copy.deepcopy(image2)

# loop()
while True:
    
    time.sleep(0.01)

    DISPLAYSURF.fill(WHITE)
    # DISPLAYSURF.blit(textSurfaceObj1, textRectObj1)
    DISPLAYSURF.blit(textSurfaceObj2, textRectObj2)
    for i in textInputList:
        DISPLAYSURF.blit(i[0], i[1])
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key < 256:
                inkey = chr(event.key)
                if event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    
                    # copy the text:
                    # text = pygame.scrap.get (SCRAP_TEXT)
                    text = clipboard.wait_for_text()
                    # print 'got these: ' + str(text) + '||||'
                    if text:
                        for i in text:
                            if i in string.printable and event.key != K_RETURN:
                                 inString += str(i)
                        #print 'lalalalalalalala'
                elif chr(event.key) == '/' and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    inString += '?'
                elif event.key == pygame.K_1 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    inString += '!'               
                elif event.key == K_BACKSPACE:
                    inString = inString[0:-1]
                elif event.key == K_RETURN:
                    inString += ' '
                elif inkey in string.printable:
                    if event.key == K_RETURN or event.key == 9:
                        inkey = chr(32)
                    inString += inkey
                updatetext()

                if event.key == K_RETURN or event.key == 9 or event.key == 32:
                    sentences = paragraphSplitter(inString)
                    # print inString
                    #pp.pprint(sentences)
                    sentenceResult = indicoStuff.getOverallResult(sentences)
                    sentResult = resultSynthesizer(sentenceResult)
                    pt.getData(sentResult[0], sentResult[1])

        if event.type == quit:
            pygame.quit()
            sys.exit()
   # pygame.display.update() 


    if pt.canAnimate(1):
        counter = counter + 1
        #print "counter " + str(counter)
        # print 'animate 1'
        # print sentResult
        if counter < len(sentResult[0]):
            pt.alert(1, counter)

            image4 = transform_image(image2, sentResult[1][counter], sentResult[2][counter], sentResult[7][counter])
            if doFace:
                image4 = processImage(image4, prevScore, sentResult[1][counter])
                prevScore = sentResult[1][counter]

        else:
            # print "elapsed time: " + str(time.time() - t1)
            if time.time() - t1 > 5:
                counter = 0
                t1 = time.time()
    #else:
        #print "occupied 1"

    # if pt.canAnimate(2):
    if False:
        counter2 = counter2 + 1
        #print "counter2 " + str(counter2)
        if counter2 < len(x2):
            pt.alert(2, counter2)
        else:
            if time.time() - t2 > 5:
                counter2 = 0
                t2 = time.time()
    #else:
        #print "occupied 2"

    pt.setColor(10, 200, 120)
    pt.zoomFit()

    pt.draw()


    pp=pygame.surfarray.make_surface(image4) 
    pp = pygame.transform.rotate(pp, -90)
    DISPLAYSURF.blit(pp, ballrect)

    pygame.display.flip()

#######End Main########



