#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2021.2.3),
    on March 19, 2022, at 18:55
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019)
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195.
        https://doi.org/10.3758/s13428-018-01193-y
"""
from __future__ import absolute_import, division
from psychopy import locale_setup
from psychopy import prefs
import pandas as pd
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy.hardware import keyboard
import pandas as pd
import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import time
from Execution import Process
from cam import cam
from cv2 import waitKey
import random
class Communicate(QObject):
    closeApp = pyqtSignal()
import psychtoolbox as ptb
from psychopy import sound


class GUI(QMainWindow, QThread):
    def __init__(self):
        super(GUI,self).__init__()
        self.initUI()
        self.cam = cam()
        self.input = self.cam
        self.dirname = ""
        print("Input: cam")
        self.statusBar.showMessage("Input: cam",5000)
        self.btnOpen.setEnabled(False)
        self.process = Process()
        self.status = False
        self.frame = np.zeros((10,10,3),np.uint8)
        self.bpm = 0

    def initUI(self):
        font = QFont()
        font.setPointSize(10)
        self.btnStart = QPushButton("Start", self)
        self.btnStart.move(230,520)
        self.btnStart.setFixedWidth(100)
        self.btnStart.setFixedHeight(25)
        self.btnStart.setFont(font)
        self.btnStart.clicked.connect(self.run)
        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.move(0,720)
        self.btnOpen.setFixedWidth(0)
        self.btnOpen.setFixedHeight(0)
        self.btnOpen.setFont(font)
        self.btnOpen.clicked.connect(self.openFileDialog)

        self.cbbInput = QComboBox(self)
        self.cbbInput.addItem("cam")
        self.cbbInput.setCurrentIndex(0)
        self.cbbInput.setFixedWidth(0)
        self.cbbInput.setFixedHeight(0)
        self.cbbInput.move(0,700)
        self.cbbInput.setFont(font)
        self.cbbInput.activated.connect(self.selectInput)
        self.lblDisplay = QLabel(self)
        self.lblDisplay.setGeometry(10,10,640,480)
        self.lblDisplay.setStyleSheet("background-color: #000000")
        self.lblHR = QLabel(self) #Heart Rate
        self.lblHR.setGeometry(250,540,300,40)
        self.lblHR.setFont(font)
        self.lblHR2 = QLabel(self) #Stable HR
        self.lblHR2.setGeometry(250,570,300,40)
        self.lblHR2.setFont(font)
        self.lblHR2.setText("Heart rate: ")
        self.statusBar = QStatusBar()
        self.statusBar.setFont(font)
        self.setStatusBar(self.statusBar)
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        self.setGeometry(0,0,800,768)
        self.setWindowTitle("Heart BPM")
        self.show()
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self,"Message", "Are you sure want to quit",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.input.stop()
            cv2.destroyAllWindows()
        else:
            event.ignore()
    def selectInput(self):
        self.reset()
        if self.cbbInput.currentIndex() == 0:
            self.input = self.cam
            print("Input: cam")
            self.btnOpen.setEnabled(False)
    def mousePressEvent(self, event):
        self.c.closeApp.emit()
    def key_handler(self):
        self.pressed = waitKey(1) & 255  # wait for keypress for 10 ms
        if self.pressed == 27:  # exit program on 'esc'
            print("[INFO] Exiting")
            self.cam.stop()
            sys.exit()
    def openFileDialog(self):

       self.statusBar.showMessage("File name: " + self.dirname,5000)

    def reset(self):
        self.process.reset()
        self.lblDisplay.clear()
        self.lblDisplay.setStyleSheet("background-color: #000012")
    @QtCore.pyqtSlot()
    def main_loop(self):

        frame = self.input.get_frame()

        self.process.frame_in = frame
        self.process.run()
        print ('loop')
        self.frame = self.process.frame_out #get the frame to show in GUI
        self.bpm = self.process.bpm #get the bpm change over the time
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        img = QImage(self.frame, self.frame.shape[1], self.frame.shape[0],
                        self.frame.strides[0], QImage.Format_RGB888)
        cv2.imshow('frame', self.frame)
        self.lblDisplay.setPixmap(QPixmap.fromImage(img))

        if self.process.bpms.__len__() >50:
            if(max(self.process.bpms-np.mean(self.process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                self.lblHR2.setText("Heart Rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
        self.key_handler()  #if not the GUI cant show anything
    def run(self, input):
        self.reset()
        input = self.input
        self.input.dirname = self.dirname
        if self.status == False:
            self.status = True
            input.start()
            self.btnStart.setText("Stop")
            self.cbbInput.setEnabled(False)
            self.btnOpen.setEnabled(False)
            self.lblHR2.clear()
            while self.status == True:
                self.main_loop()
        elif self.status == True:
            self.status = False
            input.stop()
            self.btnStart.setText("Start")
            self.cbbInput.setEnabled(True)
#app = QApplication(sys.argv)
#ex = GUI()
#while ex.status == True:
#    ex.main_loop()
#sys.exit(app.exec_())
cam = cam()
cam.start()
input = cam
dirname = ""
print("Input: cam")
#self.statusBar.showMessage("Input: cam",5000)
#self.btnOpen.setEnabled(False)
process = Process()
status = False
frame = np.zeros((10,10,3),np.uint8)
bpm = 0
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = '2021.2.3'
expName = 'ColourTesting'  # from the Builder filename that created this script
expInfo = {'gender': '', 'age': '', 'participant': ''}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='C:\\Users\\dixit\\Downloads\\dixit bpm10\\psychopy\\N-Back\\ColourTesting_lastrun.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Start Code - component code to be run after the window creation

# Setup the Window
win = visual.Window(
    size=[1280, 720], fullscr=False, screen=0,
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True)
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# Setup eyetracking
ioDevice = ioConfig = ioSession = ioServer = eyetracker = None

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# Initialize components for Routine "Welcome"
WelcomeClock = core.Clock()
text_4 = visual.TextStim(win=win, name='text_4',
    text='Hello and welcome to the cognitive task. This is an n-back memory task\nYou will be asked to pay attention to a sequence of coloured squares\nand decide whether you saw the same square n times ago. \nThere 3 blocks with 3 different rules.  We will inform you about the new rule.\nPress space to continue.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_5 = keyboard.Keyboard()

# Initialize components for Routine "Instructions"
InstructionsClock = core.Clock()

text = visual.TextStim(win=win, name='text',
    text='This is the experiment to test the effect of happy/sad stimuli to person`s emotional state.\n\nPlease press space only when you decide the coloured square was repeated. Press space to begin.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);


# text = visual.TextStim(win=win, name='text',
#     text='This is the 1-back test. You will have to press space if you decide the previous coloured square was the same as the current one.\n\nPlease press space only when you decide the coloured square was repeated. Press space to begin.',
#     font='Arial',
#     pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
#     color='white', colorSpace='rgb', opacity=1,
#     languageStyle='LTR',
#     depth=0.0);
key_resp_2 = keyboard.Keyboard()

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
Fix = visual.TextStim(win=win, name='Fix',
    text=None,
    font='Arial',
    pos=[0,0], height=1.0, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
text_7 = visual.TextStim(win=win, name='text_7',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_3 = keyboard.Keyboard()
import cv2
import numpy as np
import time

class cam(object):
    def __init__(self):
        #print ("WebCamEngine init")
        self.dirname = "" #for nothing, just to make 2 inputs the same
        self.cap = None

    def start(self):
        print("[INFO] Start webcam")
        time.sleep(1) # wait for camera to be ready
        self.cap = cv2.VideoCapture(1)
        self.valid = False
        try:
            resp = self.cap.read()
            self.shape = resp[1].shape
            self.valid = True
        except:
            self.shape = None

    def get_frame(self):

        if self.valid:
            _,frame = self.cap.read()
            frame = cv2.flip(frame,1)
            # cv2.putText(frame, str(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            #           (65,220), cv2.FONT_HERSHEY_PLAIN, 2, (0,256,256))
        else:
            frame = np.ones((480,640,3), dtype=np.uint8)
            col = (0,256,256)
            cv2.putText(frame, "(Error: Camera not accessible)",
                       (65,220), cv2.FONT_HERSHEY_PLAIN, 2, col)
        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            print("[INFO] Stop webcam")



# Initialize components for Routine "Break"
BreakClock = core.Clock()
text_2 = visual.TextStim(win=win, name='text_2',
    text="It's now time for a short break. When you are ready to continue please press space. ",
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_4 = keyboard.Keyboard()

# Initialize components for Routine "Response"
ResponseClock = core.Clock()
text_response = visual.TextStim(win=win, name='text_response',
    text="Please rate the complexity of the previous task from 1 to 10",
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_response = keyboard.Keyboard()

# Initialize components for Routine "Instructions2"
Instructions2Clock = core.Clock()
text_5 = visual.TextStim(win=win, name='text_5',
    text='This is the 2-back test. You will have to press space if you decide the  coloured square two trials ago was the same as the current one.\n\nPlease press space only when you decide the coloured square was repeated. Press space to begin.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_6 = keyboard.Keyboard()

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
Fix = visual.TextStim(win=win, name='Fix',
    text=None,
    font='Arial',
    pos=[0,0], height=1.0, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
text_7 = visual.TextStim(win=win, name='text_7',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_3 = keyboard.Keyboard()
import cv2
import numpy as np
import time

class cam(object):
    def __init__(self):
        #print ("WebCamEngine init")
        self.dirname = "" #for nothing, just to make 2 inputs the same
        self.cap = None

    def start(self):
        print("[INFO] Start webcam")
        time.sleep(1) # wait for camera to be ready
        self.cap = cv2.VideoCapture(1)
        self.valid = False
        try:
            resp = self.cap.read()
            self.shape = resp[1].shape
            self.valid = True
        except:
            self.shape = None

    def get_frame(self):

        if self.valid:
            _,frame = self.cap.read()
            frame = cv2.flip(frame,1)
            # cv2.putText(frame, str(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            #           (65,220), cv2.FONT_HERSHEY_PLAIN, 2, (0,256,256))
        else:
            frame = np.ones((480,640,3), dtype=np.uint8)
            col = (0,256,256)
            cv2.putText(frame, "(Error: Camera not accessible)",
                       (65,220), cv2.FONT_HERSHEY_PLAIN, 2, col)
        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            print("[INFO] Stop webcam")

# Initialize components for Routine "Break"
BreakClock = core.Clock()
text_2 = visual.TextStim(win=win, name='text_2',
    text="It's now time for a short break. When you are ready to continue please press space. ",
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_4 = keyboard.Keyboard()

# Initialize components for Routine "Instructions3"
Instructions3Clock = core.Clock()
text_6 = visual.TextStim(win=win, name='text_6',
    text='This is the 3-back test. You will have to press space if you decide the  coloured square three trials ago was the same as the current one.\n\nPlease press space only when you decide the coloured square was repeated. Press space to begin.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_7 = keyboard.Keyboard()

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
Fix = visual.TextStim(win=win, name='Fix',
    text=None,
    font='Arial',
    pos=[0,0], height=1.0, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);

# Initialize components for Routine "trial"
trialClock = core.Clock()
text_7 = visual.TextStim(win=win, name='text_7',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_3 = keyboard.Keyboard()
import cv2
import numpy as np
import time

class cam(object):
    def __init__(self):
        #print ("WebCamEngine init")
        self.dirname = "" #for nothing, just to make 2 inputs the same
        self.cap = None

    def start(self):
        print("[INFO] Start webcam")
        time.sleep(1) # wait for camera to be ready
        self.cap = cv2.VideoCapture(1)
        self.valid = False
        try:
            resp = self.cap.read()
            self.shape = resp[1].shape
            self.valid = True
        except:
            self.shape = None

    def get_frame(self):

        if self.valid:
            _,frame = self.cap.read()
            frame = cv2.flip(frame,1)
            # cv2.putText(frame, str(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            #           (65,220), cv2.FONT_HERSHEY_PLAIN, 2, (0,256,256))
        else:
            frame = np.ones((480,640,3), dtype=np.uint8)
            col = (0,256,256)
            cv2.putText(frame, "(Error: Camera not accessible)",
                       (65,220), cv2.FONT_HERSHEY_PLAIN, 2, col)
        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            print("[INFO] Stop webcam")



# Initialize components for Routine "Thanks"
ThanksClock = core.Clock()
text_3 = visual.TextStim(win=win, name='text_3',
    text='Thank you for participanting in the experiment.\nThe experimenter will be with you shortly.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine

# ------Prepare to start Routine "Welcome"-------
continueRoutine = True
# update component parameters for each repeat
key_resp_5.keys = []
key_resp_5.rt = []
_key_resp_5_allKeys = []
# keep track of which components have finished
WelcomeComponents = [text_4, key_resp_5]
for thisComponent in WelcomeComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
WelcomeClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "Welcome"-------
while continueRoutine:
    # get current time
    t = WelcomeClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=WelcomeClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *text_4* updates
    if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        text_4.frameNStart = frameN  # exact frame index
        text_4.tStart = t  # local t and not account for scr refresh
        text_4.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
        text_4.setAutoDraw(True)

    # *key_resp_5* updates
    waitOnFlip = False
    if key_resp_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        key_resp_5.frameNStart = frameN  # exact frame index
        key_resp_5.tStart = t  # local t and not account for scr refresh
        key_resp_5.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(key_resp_5, 'tStartRefresh')  # time at next scr refresh
        key_resp_5.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(key_resp_5.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(key_resp_5.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if key_resp_5.status == STARTED and not waitOnFlip:
        theseKeys = key_resp_5.getKeys(keyList=['space'], waitRelease=False)
        _key_resp_5_allKeys.extend(theseKeys)
        if len(_key_resp_5_allKeys):
            key_resp_5.keys = _key_resp_5_allKeys[-1].name  # just the last key pressed
            key_resp_5.rt = _key_resp_5_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()

    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in WelcomeComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Welcome"-------
for thisComponent in WelcomeComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('text_4.started', text_4.tStartRefresh)
thisExp.addData('text_4.stopped', text_4.tStopRefresh)
# check responses
if key_resp_5.keys in ['', [], None]:  # No response was made
    key_resp_5.keys = None
thisExp.addData('key_resp_5.keys',key_resp_5.keys)
if key_resp_5.keys != None:  # we had a response
    thisExp.addData('key_resp_5.rt', key_resp_5.rt)
thisExp.addData('key_resp_5.started', key_resp_5.tStartRefresh)
thisExp.addData('key_resp_5.stopped', key_resp_5.tStopRefresh)
thisExp.nextEntry()
# the Routine "Welcome" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# def runRoutineOneBack ():
#     pathNeg = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Negative Pictures\Selected N'
#     pathPos = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Positive Pictures\selected p'
#     negative_images = os.listdir (pathNeg)
#     positive_images = os.listdir (pathPos)
#     negative_images = [os.path.join(pathNeg, image) for image in negative_images]
#     positive_images = [os.path.join(pathPos, image) for image in positive_images]
#     #print (negative_images)
#     #return 0
#     process.reset()
#     # ------Prepare to start Routine "Instructions"-------
#     continueRoutine = True
#     # update component parameters for each repeat
#     print (key_resp_2)
#     key_resp_2.keys = []
#     key_resp_2.rt = []
#     _key_resp_2_allKeys = []
#     # keep track of which components have finished
#     InstructionsComponents = [text, key_resp_2]
#     for thisComponent in InstructionsComponents:
#         thisComponent.tStart = None
#         thisComponent.tStop = None
#         thisComponent.tStartRefresh = None
#         thisComponent.tStopRefresh = None
#         if hasattr(thisComponent, 'status'):
#             thisComponent.status = NOT_STARTED
#     # reset timers
#     t = 0
#     _timeToFirstFrame = win.getFutureFlipTime(clock="now")
#     InstructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
#     frameN = -1

#     # -------Run Routine "Instructions"-------
#     while continueRoutine:
#         # get current time
#         t = InstructionsClock.getTime()
#         tThisFlip = win.getFutureFlipTime(clock=InstructionsClock)
#         tThisFlipGlobal = win.getFutureFlipTime(clock=None)
#         frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
#         # update/draw components on each frame

#         # *text* updates
#         if text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
#             # keep track of start time/frame for later
#             text.frameNStart = frameN  # exact frame index
#             text.tStart = t  # local t and not account for scr refresh
#             text.tStartRefresh = tThisFlipGlobal  # on global time
#             win.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
#             text.setAutoDraw(True)

#         # *key_resp_2* updates
#         waitOnFlip = False
#         if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
#             # keep track of start time/frame for later
#             key_resp_2.frameNStart = frameN  # exact frame index
#             key_resp_2.tStart = t  # local t and not account for scr refresh
#             key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
#             win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
#             key_resp_2.status = STARTED
#             # keyboard checking is just starting
#             waitOnFlip = True
#             win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
#             win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
#         if key_resp_2.status == STARTED and not waitOnFlip:
#             theseKeys = key_resp_2.getKeys(keyList=['space'], waitRelease=False)
#             _key_resp_2_allKeys.extend(theseKeys)
#             if len(_key_resp_2_allKeys):
#                 key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
#                 key_resp_2.rt = _key_resp_2_allKeys[-1].rt
#                 # a response ends the routine
#                 continueRoutine = False

#         # check for quit (typically the Esc key)
#         if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
#             core.quit()

#         # check if all components have finished
#         if not continueRoutine:  # a component has requested a forced-end of Routine
#             break
#         continueRoutine = False  # will revert to True if at least one component still running
#         for thisComponent in InstructionsComponents:
#             if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
#                 continueRoutine = True
#                 break  # at least one component has not yet finished

#         # refresh the screen
#         if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
#             win.flip()

#     # -------Ending Routine "Instructions"-------
#     for thisComponent in InstructionsComponents:
#         if hasattr(thisComponent, "setAutoDraw"):
#             thisComponent.setAutoDraw(False)
#     thisExp.addData('text.started', text.tStartRefresh)
#     thisExp.addData('text.stopped', text.tStopRefresh)
#     # check responses
#     if key_resp_2.keys in ['', [], None]:  # No response was made
#         key_resp_2.keys = None
#     thisExp.addData('key_resp_2.keys',key_resp_2.keys)
#     if key_resp_2.keys != None:  # we had a response
#         thisExp.addData('key_resp_2.rt', key_resp_2.rt)
#     thisExp.addData('key_resp_2.started', key_resp_2.tStartRefresh)
#     thisExp.addData('key_resp_2.stopped', key_resp_2.tStopRefresh)
#     thisExp.nextEntry()
#     # the Routine "Instructions" was not non-slip safe, so reset the non-slip timer
#     routineTimer.reset()

#     # set up handler to look after randomisation of conditions etc
#     Block1_1back = data.TrialHandler(nReps=1, method='random',
#         extraInfo=expInfo, originPath=-1,
#         trialList=data.importConditions('1_back_task.xlsx'),
#         seed=None, name='Block1_1back')
#     thisExp.addLoop(Block1_1back)  # add the loop to the experiment
#     thisBlock1_1back = Block1_1back.trialList[0]  # so we can initialise stimuli with some values
#     # abbreviate parameter names if possible (e.g. rgb = thisBlock1_1back.rgb)
#     if thisBlock1_1back != None:
#         for paramName in thisBlock1_1back:
#             exec('{} = thisBlock1_1back[paramName]'.format(paramName))

#     #random.shuffle (list (Block1_1back))
#     all_letters = []
#     data_exp = pd.read_excel('1_back_task.xlsx')
#     print (data_exp.head())
#     #return 0
#     all_letters = list (data_exp ['colourtest'])
#     print ('letters:', all_letters)
#     #return 0
#     #for thisBlock1_1back in Block1_1back:
#     #   all_letters.append (thisBlock1_1back ['colourtest'])
#     iteration = -1
#     list_of_stimuli = []

#     sound_happy = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Music\Happy.ogg'
#     sound_sad =   r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Music\Sad.ogg'

#     negative_images = [(i, sound_sad) for i in negative_images]
#     positive_images = [(i, sound_happy) for i in positive_images]

#     list_of_stimuli.extend (negative_images)
#     list_of_stimuli.extend (positive_images)

#     random.shuffle (list_of_stimuli)
#     finishedCalibration = False
#     i=0
#     while (not finishedCalibration):
#         frame = input.get_frame()
#         process.frame_in = frame
#         process.run()
#         frame = process.frame_out #get the frame to show in GUI
#         bpm = process.bpm #get the bpm change over the time
#         print (i,' ',bpm)
#         i+=1
#         if (bpm == 0):
#             finishedCalibration = False
#             continue
#         finishedCalibration = True
#         # if process.bpms.__len__() >50:
#         #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
#         #         print ('current bpm:', ' ', bpm)
#         #         break
#         #     else:
#         #         finishedCalibration = False
#     for stim, snd in list_of_stimuli:
#         stimulusimage = stim
#         showingimage = visual.ImageStim(win, image=stimulusimage)
#         showingimage.draw()
#         win.flip()
#         mySound = sound.Sound(snd, secs = 10)
#         mySound.play ()
#         #core.wait(10) #wait for 10second
#         while (True):
#             #check time and reset the value of bpm
#             i+=1
#             if (i==-1):
#                 break
#         mySound.stop()
#         iteration += 1
#         frame = input.get_frame()
#         process.frame_in = frame
#         process.run()
#         frame = process.frame_out #get the frame to show in GUI
#         bpm = process.bpm #get the bpm change over the time
#         print ('current value of BPM for iteration ', iteration,' :',bpm)
#     return 0
        # print ('ITER:', iteration, ' ', len (all_letters))
        # currentLoop = Block1_1back
        # # abbreviate parameter names if possible (e.g. rgb = thisBlock1_1back.rgb)
        # if thisBlock1_1back != None:
        #     for paramName in thisBlock1_1back:
        #         exec('{} = thisBlock1_1back[paramName]'.format(paramName))

        # # ------Prepare to start Routine "Fixation"-------
        # continueRoutine = True
        # routineTimer.add(10.000000)
        # # update component parameters for each repeat
        # Fix.setColor('white', colorSpace='rgb')
        # Fix.setPos((0, 0))
        # Fix.setText('')
        # Fix.setFont('Arial')
        # Fix.setHeight(0.1)
        # # keep track of which components have finished
        # FixationComponents = [Fix]
        # for thisComponent in FixationComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "Fixation"-------
        # i=0

        # while continueRoutine: # and routineTimer.getTime() > 0:
        #     # get current time
        #     t = FixationClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame
        #     # *Fix* updates
        #     if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         Fix.frameNStart = frameN  # exact frame index
        #         Fix.tStart = t  # local t and not account for scr refresh
        #         Fix.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
        #         Fix.setAutoDraw(True)
        #     if Fix.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
        #             # keep track of stop time/frame for later
        #             Fix.tStop = t  # not accounting for scr refresh
        #             Fix.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
        #             Fix.setAutoDraw(False)
        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()

        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in FixationComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished

        #     # refresh the screen
        #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        #         win.flip()

        # finishedCalibration = False
        # i = 0
        # #process.reset()
        # print ('TIMES:', process.times, len (process.times))
        # while (not finishedCalibration):
        #     frame = input.get_frame()
        #     process.frame_in = frame
        #     process.run()
        #     frame = process.frame_out #get the frame to show in GUI
        #     bpm = process.bpm #get the bpm change over the time
        #     print (i,' ',bpm)
        #     i+=1
        #     if (bpm == 0):
        #         finishedCalibration = False
        #         continue
        #     finishedCalibration = True
        #     # if process.bpms.__len__() >50:
        #     #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
        #     #         print ('current bpm:', ' ', bpm)
        #     #         break
        #     #     else:
        #     #         finishedCalibration = False

        # # -------Ending Routine "Fixation"-------
        # for thisComponent in FixationComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # Block1_1back.addData('Fix.started', Fix.tStartRefresh)
        # Block1_1back.addData('Fix.stopped', Fix.tStopRefresh)

        # # ------Prepare to start Routine "trial"-------
        # continueRoutine = True
        # routineTimer.reset ()
        # routineTimer.add(1.000000)
        # # update component parameters for each repeat

        # print ('CURRENT LETTER IS:', thisBlock1_1back ['colourtest'])
        # if (iteration >= len (all_letters)):
        #     break
        # curr_letter = all_letters [iteration]
        # #text_7.setText(thisBlock1_1back ['colourtest'])
        # text_7.setText (curr_letter)
        # key_resp_3.keys = []
        # key_resp_3.rt = []
        # _key_resp_3_allKeys = []
        # # keep track of which components have finished
        # trialComponents = [text_7, key_resp_3]
        # for thisComponent in trialComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1
        # flag = False
        # mySound = sound.Sound(secs = 0.5)
        # # -------Run Routine "trial"-------
        # i = 0
        # while continueRoutine and routineTimer.getTime() > 0:
        #     print ('gggg:', iteration)
        #     # get current time
        #     #get the bpm change over the time
        #     #i+=1
        #     #print (i,' ',process.bpms)
        #     #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        #     #cv2.imshow('frame', frame)
        #                 #self.lblHR2.setText("Heart Rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
        #     t = trialClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=trialClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame

        #     # *text_7* updates
        #     if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         text_7.frameNStart = frameN  # exact frame index
        #         text_7.tStart = t  # local t and not account for scr refresh
        #         text_7.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
        #         text_7.setAutoDraw(True)
        #     if text_7.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
        #             # keep track of stop time/frame for later
        #             text_7.tStop = t  # not accounting for scr refresh
        #             text_7.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
        #             text_7.setAutoDraw(False)

        #     # *key_resp_3* updates
        #     waitOnFlip = False
        #     if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         key_resp_3.frameNStart = frameN  # exact frame index
        #         key_resp_3.tStart = t  # local t and not account for scr refresh
        #         key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
        #         key_resp_3.status = STARTED
        #         # keyboard checking is just starting
        #         waitOnFlip = True
        #         win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
        #         win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
        #     if key_resp_3.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
        #             # keep track of stop time/frame for later
        #             key_resp_3.tStop = t  # not accounting for scr refresh
        #             key_resp_3.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
        #             key_resp_3.status = FINISHED
        #     if key_resp_3.status == STARTED and not waitOnFlip:
        #         theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
        #         _key_resp_3_allKeys.extend(theseKeys)
        #         if len(_key_resp_3_allKeys):
        #             key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
        #             key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
        #             # was this correct?
        #             # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
        #             #     key_resp_3.corr = 1
        #             # else:
        #             #     key_resp_3.corr = 0
        #             # a response ends the routine
        #             continueRoutine = False

        #     # check for quit (typically the Esc key)
        #     #if 'space' in key_resp_3.keys:
        #     print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1] != all_letters[iteration], iteration - 1)
        #     #mySound = sound.Sound('A')
        #     if 'space' in key_resp_3.keys and flag==False and iteration > 0 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 1]:
        #         print (all_letters[iteration], ' ', all_letters[iteration - 1])
        #         nextFlip = win.getFutureFlipTime(clock='ptb')
        #         mySound.play(when = nextFlip)  # sync with screen refresh
        #         print ('CLICK.................................................')
        #         flag = True
        #         #mySound = sound.Sound()
        #         # = ptb.GetSecs()
        #         #ySound.play()
        #     #else:
        #         #mySound.stop()

        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in trialComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished

        #     # refresh the screen
        #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        #         win.flip()



        # -------Ending Routine "trial"-------
    #     for thisComponent in trialComponents:
    #         if hasattr(thisComponent, "setAutoDraw"):
    #             thisComponent.setAutoDraw(False)
    #     #print ('bpm is:', bpm)
    #     #if process.bpms.__len__() > 50:
    #     #    if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
    #     #        print ('current bpm:', ' ', bpm)
    #     frame = input.get_frame()
    #     process.frame_in = frame
    #     #print (len (process.bpms))
    #     process.run()
    #     #frame = process.frame_out #get the frame to show in GUI
    #     bpm = process.bpm
    #     Block1_1back.addData('text_7.started', text_7.tStartRefresh)
    #     Block1_1back.addData('text_7.stopped', text_7.tStopRefresh)
    #     # check responses
    #     if key_resp_3.keys in ['', [], None]:  # No response was made
    #         key_resp_3.keys = None
    #         # # was no response the correct answer?!
    #         # if str(corresp).lower() == 'none':
    #         #     key_resp_3.corr = 1;  # correct non-response
    #         # else:
    #         #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
    #     # store data for Block1_1back (TrialHandler)
    #     Block1_1back.addData('key_resp_3.keys',key_resp_3.keys)
    #     Block1_1back.addData('key_resp_3.corr', key_resp_3.corr)
    #     if key_resp_3.keys != None:  # we had a response
    #         Block1_1back.addData('key_resp_3.rt', key_resp_3.rt)
    #     Block1_1back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
    #     Block1_1back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
    #     Block1_1back.addData('bpm', bpm)
    #     thisExp.nextEntry()

    # # completed 1 repeats of 'Block1_1back'


    # # ------Prepare to start Routine "Break"-------
    # continueRoutine = True
    # # update component parameters for each repeat
    # key_resp_4.keys = []
    # key_resp_4.rt = []
    # _key_resp_4_allKeys = []
    # # keep track of which components have finished
    # BreakComponents = [text_2, key_resp_4]
    # for thisComponent in BreakComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # BreakClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "Break"-------
    # while continueRoutine:
    #     # get current time
    #     t = BreakClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=BreakClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     # *text_2* updates
    #     if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         text_2.frameNStart = frameN  # exact frame index
    #         text_2.tStart = t  # local t and not account for scr refresh
    #         text_2.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
    #         text_2.setAutoDraw(True)

    #     # *key_resp_4* updates
    #     waitOnFlip = False
    #     if key_resp_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         key_resp_4.frameNStart = frameN  # exact frame index
    #         key_resp_4.tStart = t  # local t and not account for scr refresh
    #         key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
    #         key_resp_4.status = STARTED
    #         # keyboard checking is just starting
    #         waitOnFlip = True
    #         win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
    #         win.callOnFlip(key_resp_4.clearEvents, eventType='keyboard')  # clear events on next screen flip
    #     if key_resp_4.status == STARTED and not waitOnFlip:
    #         theseKeys = key_resp_4.getKeys(keyList=['space'], waitRelease=False)
    #         _key_resp_4_allKeys.extend(theseKeys)
    #         if len(_key_resp_4_allKeys):
    #             key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
    #             key_resp_4.rt = _key_resp_4_allKeys[-1].rt
    #             # a response ends the routine
    #             continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()

    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in BreakComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished

    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "Break"-------
    # for thisComponent in BreakComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # thisExp.addData('text_2.started', text_2.tStartRefresh)
    # thisExp.addData('text_2.stopped', text_2.tStopRefresh)
    # # check responses
    # if key_resp_4.keys in ['', [], None]:  # No response was made
    #     key_resp_4.keys = None
    # thisExp.addData('key_resp_4.keys',key_resp_4.keys)
    # if key_resp_4.keys != None:  # we had a response
    #     thisExp.addData('key_resp_4.rt', key_resp_4.rt)
    # thisExp.addData('key_resp_4.started', key_resp_4.tStartRefresh)
    # thisExp.addData('key_resp_4.stopped', key_resp_4.tStopRefresh)
    # thisExp.nextEntry()
    # # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    # # ------Prepare to start Routine "Response"-------
    # message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    # message.text = "Please rate the difficulty of the previous task"
    # scales = '1=Easy                       10=Very Difficult'
    # ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    # while ratingScale.noResponse:
    #     message.draw()
    #     ratingScale.draw()
    #     win.flip()
    #     #print ('no response...')
    # rating = ratingScale.getRating()
    # decisionTime = ratingScale.getRT()
    # choiceHistory = ratingScale.getHistory()
    # print('rating', rating)
    # print('decisionTime', decisionTime)
    # print('choiceHistory',choiceHistory)
    # Block1_1back.addData('text_7.started', 0)
    # Block1_1back.addData('text_7.stopped', 0)
    # Block1_1back.addData('key_resp_3.keys',0)
    # Block1_1back.addData('key_resp_3.corr', 0)
    # if key_resp_3.keys != None:  # we had a response
    #     Block1_1back.addData('key_resp_3.rt', 0)
    # Block1_1back.addData('key_resp_3.started', 0)
    # Block1_1back.addData('key_resp_3.stopped', 0)
    # Block1_1back.addData('bpm', 0)
    # Block1_1back.addData('diffuculty rating 1', rating)
    # Block1_1back.addData('decision time to rate 1', decisionTime)
    # thisExp.nextEntry()
    # continueRoutine = True
    # win.flip()

    # # get names of stimulus parameters
    # if Block1_1back.trialList in ([], [None], None):
    #     params = []
    # else:
    #     params = Block1_1back.trialList[0].keys()
    # # save data for this loop
    # Block1_1back.saveAsExcel(filename + 'Block1_1back.xlsx', sheetName='Block1_1back',
    #     stimOut=params,
    #     dataOut=['n','all_mean','all_std', 'all_raw'])
    # Block1_1back.saveAsText(filename + 'Block1_1back.csv', delim=',',
    #     stimOut=params,
    #     dataOut=['n','all_mean','all_std', 'all_raw'])

    # # update component parameters for each repeat
    # key_response.keys = []
    # key_response.rt = []

    # _key_resp_res_allKeys = []

    # # keep track of which components have finished
    # ResponseComponents = [text_response, key_response]
    # for thisComponent in ResponseComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # ResponseClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "Break"-------
    # while continueRoutine:
    #     # get current time
    #     t = ResponseClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=ResponseClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     # *text_2* updates
    #     if text_response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         text_response.frameNStart = frameN  # exact frame index
    #         text_response.tStart = t  # local t and not account for scr refresh
    #         text_response.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(text_response, 'tStartRefresh')  # time at next scr refresh
    #         text_response.setAutoDraw(True)

    #     # *key_resp_4* updates
    #     waitOnFlip = False
    #     if key_response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         key_response.frameNStart = frameN  # exact frame index
    #         key_response.tStart = t  # local t and not account for scr refresh
    #         key_response.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(key_response, 'tStartRefresh')  # time at next scr refresh
    #         key_response.status = STARTED
    #         # keyboard checking is just starting
    #         waitOnFlip = True
    #         win.callOnFlip(key_response.clock.reset)  # t=0 on next screen flip
    #         win.callOnFlip(key_response.clearEvents, eventType='keyboard')  # clear events on next screen flip
    #     if key_response.status == STARTED and not waitOnFlip:
    #         theseKeys = key_response.getKeys(keyList=['space'], waitRelease=False)
    #         _key_resp_res_allKeys.extend(theseKeys)
    #         if len(_key_resp_res_allKeys):
    #             key_resp_res.keys = _key_resp_res_allKeys[-1].name  # just the last key pressed
    #             key_resp_res.rt = _key_resp_res_allKeys[-1].rt
    #             # a response ends the routine
    #             continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()

    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in ResponseComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished

    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "Response"-------
    # for thisComponent in ResponseComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # thisExp.addData('text_response.started', text_response.tStartRefresh)
    # thisExp.addData('text_response.stopped', text_response.tStopRefresh)
    # # check responses
    # if key_response.keys in ['', [], None]:  # No response was made
    #     key_response.keys = None
    # thisExp.addData('key_response.keys',key_response.keys)
    # if key_response.keys != None:  # we had a response
    #     thisExp.addData('key_response.rt', key_response.rt)
    # thisExp.addData('key_response.started', key_response.tStartRefresh)
    # thisExp.addData('key_response.stopped', key_response.tStopRefresh)
    # thisExp.nextEntry()
    # # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    # # ------Prepare to start Routine "Instructions2"-------
    # continueRoutine = True
    # # update component parameters for each repeat
    # key_resp_6.keys = []
    # key_resp_6.rt = []
    # _key_resp_6_allKeys = []
    # # keep track of which components have finished
    # Instructions2Components = [text_5, key_resp_6]
    # for thisComponent in Instructions2Components:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # Instructions2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1


def runRoutineTwoBack ():
    pathNeg = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Negative Pictures\Selected N'
    pathPos = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Positive Pictures\selected p'
    negative_images = os.listdir (pathNeg)
    positive_images = os.listdir (pathPos)
    negative_images = [os.path.join(pathNeg, image) for image in negative_images]
    positive_images = [os.path.join(pathPos, image) for image in positive_images]
    sound_happy = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Happy.ogg'
    sound_sad = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Sad.ogg'
    sounds = [sound_sad,sound_happy]
    process.reset()
    # ------Prepare to start Routine "Instructions2"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_6.keys = []
    key_resp_6.rt = []
    _key_resp_6_allKeys = []
    # keep track of which components have finished
    Instructions2Components = [text_5, key_resp_6]
    for thisComponent in Instructions2Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    Instructions2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    routineTimer.reset()
    print ('Before instruction 2')
    # -------Run Routine "Instructions2"-------
    while continueRoutine:
        #print (text_5.status)
        #break
        #exit()
        # get current time
        t = Instructions2Clock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=Instructions2Clock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_5* updates
        if text_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            print ('text_5')
            # keep track of start time/frame for later
            text_5.frameNStart = frameN  # exact frame index
            text_5.tStart = t  # local t and not account for scr refresh
            text_5.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_5, 'tStartRefresh')  # time at next scr refresh
            text_5.setAutoDraw(True)

        # *key_resp_6* updates
        waitOnFlip = False
        if key_resp_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_6.frameNStart = frameN  # exact frame index
            key_resp_6.tStart = t  # local t and not account for scr refresh
            key_resp_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_6, 'tStartRefresh')  # time at next scr refresh
            key_resp_6.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_6.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_6.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_6.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_6.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_6_allKeys.extend(theseKeys)
            if len(_key_resp_6_allKeys):
                key_resp_6.keys = _key_resp_6_allKeys[-1].name  # just the last key pressed
                key_resp_6.rt = _key_resp_6_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Instructions2Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Instructions2"-------
    for thisComponent in Instructions2Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_5.started', text_5.tStartRefresh)
    thisExp.addData('text_5.stopped', text_5.tStopRefresh)
    # check responses
    if key_resp_6.keys in ['', [], None]:  # No response was made
        key_resp_6.keys = None
    thisExp.addData('key_resp_6.keys',key_resp_6.keys)
    if key_resp_6.keys != None:  # we had a response
        thisExp.addData('key_resp_6.rt', key_resp_6.rt)
    thisExp.addData('key_resp_6.started', key_resp_6.tStartRefresh)
    thisExp.addData('key_resp_6.stopped', key_resp_6.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Instructions2" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    Block2_2back = data.TrialHandler(nReps=1, method='random',
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions('2_back_task.xlsx'),
        seed=None, name='Block2_2back')
    thisExp.addLoop(Block2_2back)  # add the loop to the experiment
    thisBlock2_2back = Block2_2back.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock2_2back.rgb)
    if thisBlock2_2back != None:
        for paramName in thisBlock2_2back:
            exec('{} = thisBlock2_2back[paramName]'.format(paramName))
    #random.shuffle (Block2_2back)
    all_letters = []
    data_exp = pd.read_excel('2_back_task.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['numbers'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['numbers'])
    iteration = -1
    sounds = [sound_happy, sound_sad]
    snds_list = []
    for i in range (len (all_letters)):
        s = random.choice (sounds)
        mySound = sound.Sound(s, secs = 1)
        snds_list.append (mySound)

    for thisBlock2_2back in Block2_2back:
        currentLoop = Block2_2back
        iteration += 1
        # abbreviate parameter names if possible (e.g. rgb = thisBlock2_2back.rgb)
        if thisBlock2_2back != None:
            for paramName in thisBlock2_2back:
                exec('{} = thisBlock2_2back[paramName]'.format(paramName))
        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(10.000000)
        # update component parameters for each repeat
        Fix.setColor('white', colorSpace='rgb')
        Fix.setPos((0, 0))
        Fix.setText('')
        Fix.setFont('Arial')
        Fix.setHeight(0.1)
        # keep track of which components have finished
        FixationComponents = [Fix]
        for thisComponent in FixationComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        # -------Run Routine "Fixation"-------
        while continueRoutine: #and routineTimer.getTime() > 0:

            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *Fix* updates
            if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Fix.frameNStart = frameN  # exact frame index
                Fix.tStart = t  # local t and not account for scr refresh
                Fix.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
                Fix.setAutoDraw(True)
            if Fix.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    Fix.tStop = t  # not accounting for scr refresh
                    Fix.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
                    Fix.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
            # frame = input.get_frame()
            # process.frame_in = frame
            # process.run()
            # frame = process.frame_out #get the frame to show in GUI
            # bpm = process.bpm #get the bpm change over the time
            # i+=1
            # #print (i,' ',process.bpms)
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         continueRoutine = False
        finishedCalibration = False
        i = 0
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        while (not finishedCalibration):
            frame = input.get_frame()
            print (frame)
            process.frame_in = frame
            process.run()
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print (i,' ',bpm)
            i+=1
            if (bpm == 0):
                finishedCalibration = False
                continue
            finishedCalibration = True
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         finishedCalibration = False

        # -------Ending Routine "Fixation"-------
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block2_2back.addData('Fix.started', Fix.tStartRefresh)
        Block2_2back.addData('Fix.stopped', Fix.tStopRefresh)

        sound_happy = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Happy.ogg'
        sound_sad = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Sad.ogg'
        # negative_images = [(i, sound_sad) for i in negative_images]
        # positive_images = [(i, sound_happy) for i in positive_images]
        # list_of_stimuli.extend (negative_images)
        # list_of_stimuli.extend (positive_images)
        # random.shuffle (list_of_stimuli)
        mySound = snds_list [iteration - 1]
        mySound.play ()
        mySound.stop()
        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        routineTimer.add(1.000000)
        # update component parameters for each repeat
        #text_7.setText(thisBlock2_2back['colourtest'])
        if (iteration >= len (all_letters)):
            break
        curr_letter = all_letters [iteration]
        #text_7.setText(thisBlock1_1back ['colourtest'])
        text_7.setText (curr_letter)
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # keep track of which components have finished
        trialComponents = [text_7, key_resp_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        flag = False
        mySound = sound.Sound(secs = 0.5)
        # -------Run Routine "trial"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_7* updates
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                text_7.setAutoDraw(True)
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
                    text_7.setAutoDraw(False)

            # *key_resp_3* updates
            waitOnFlip = False
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_3.tStop = t  # not accounting for scr refresh
                    key_resp_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
                    key_resp_3.status = FINISHED
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
                    key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
                    # was this correct?
                    # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
                    #     key_resp_3.corr = 1
                    # else:
                    #     key_resp_3.corr = 0
                    # a response ends the routine
                    continueRoutine = False
            #mySound = sound.Sound('A')
            print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1]!= all_letters[iteration])
            if 'space' in key_resp_3.keys and flag==False and iteration > 0 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 1]:
                print (all_letters[iteration], ' ', all_letters[iteration - 1])
                nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.play(when = nextFlip)  # sync with screen refresh
                print ('CLICK.................................................')
                flag = True
                #mySound = sound.Sound()
                # = ptb.GetSecs()
                #ySound.play()
            #else:
                #mySound.stop()
            # check for quit (typically the Esc key)

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        frame = input.get_frame()
        process.frame_in = frame
        process.run()
        frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm
        if process.bpms.__len__() >50:
            if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                print ('current bpm:', ' ', bpm)
        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block2_2back.addData('text_7.started', text_7.tStartRefresh)
        Block2_2back.addData('text_7.stopped', text_7.tStopRefresh)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
            # was no response the correct answer?!
            # if str(corresp).lower() == 'none':
            #     key_resp_3.corr = 1;  # correct non-response
            # else:
            #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
        # store data for Block2_2back (TrialHandler)
        Block2_2back.addData('key_resp_3.keys',key_resp_3.keys)
        Block2_2back.addData('key_resp_3.corr', key_resp_3.corr)
        if key_resp_3.keys != None:  # we had a response
            Block2_2back.addData('key_resp_3.rt', key_resp_3.rt)
        Block2_2back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
        Block2_2back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
        Block2_2back.addData('bpm', bpm)
        thisExp.nextEntry()

    # completed 1 repeats of 'Block2_2back'

    # ------Prepare to start Routine "Response"-------
    message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    message.text = "Please rate the difficulty of the previous task"
    scales = '1=Easy                       10=Very Difficult'
    ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    while ratingScale.noResponse:
        message.draw()
        ratingScale.draw()
        win.flip()
    rating = ratingScale.getRating()
    decisionTime = ratingScale.getRT()
    choiceHistory = ratingScale.getHistory()
    #win.close()

    print('rating 2', rating)
    print('decisionTime 2', decisionTime)
    print('choiceHistory 2',choiceHistory)
    #thisExp.addData('diffuculty rating 2', rating)
    #thisExp.addData('decision time to rate 2', decisionTime)
    #thisExp.nextEntry()
    Block2_2back.addData('text_7.started', 0)
    Block2_2back.addData('text_7.stopped', 0)
    Block2_2back.addData('key_resp_3.keys',0)
    Block2_2back.addData('key_resp_3.corr', 0)
    if key_resp_3.keys != None:  # we had a response
        Block2_2back.addData('key_resp_3.rt', 0)
    Block2_2back.addData('key_resp_3.started', 0)
    Block2_2back.addData('key_resp_3.stopped', 0)
    Block2_2back.addData('bpm', 0)
    Block2_2back.addData('diffuculty rating 1', rating)
    Block2_2back.addData('decision time to rate 1', decisionTime)
    thisExp.nextEntry()
    # get names of stimulus parameters
    if Block2_2back.trialList in ([], [None], None):
        params = []
    else:
        params = Block2_2back.trialList[0].keys()
    # save data for this loop
    Block2_2back.saveAsExcel(filename + 'Block2_2back.xlsx', sheetName='Block2_2back',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])
    Block2_2back.saveAsText(filename + 'Block2_2back.csv', delim=',',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])

    # ------Prepare to start Routine "Break"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_4.keys = []
    key_resp_4.rt = []
    _key_resp_4_allKeys = []
    # keep track of which components have finished
    BreakComponents = [text_2, key_resp_4]
    for thisComponent in BreakComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    BreakClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Break"-------
    while continueRoutine:
        # get current time
        t = BreakClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=BreakClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_2* updates
        if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_2.frameNStart = frameN  # exact frame index
            text_2.tStart = t  # local t and not account for scr refresh
            text_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
            text_2.setAutoDraw(True)

        # *key_resp_4* updates
        waitOnFlip = False
        if key_resp_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_4.frameNStart = frameN  # exact frame index
            key_resp_4.tStart = t  # local t and not account for scr refresh
            key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
            key_resp_4.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_4.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_4.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_4.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_4_allKeys.extend(theseKeys)
            if len(_key_resp_4_allKeys):
                key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
                key_resp_4.rt = _key_resp_4_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in BreakComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Break"-------
    for thisComponent in BreakComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_2.started', text_2.tStartRefresh)
    thisExp.addData('text_2.stopped', text_2.tStopRefresh)
    # check responses
    if key_resp_4.keys in ['', [], None]:  # No response was made
        key_resp_4.keys = None
    thisExp.addData('key_resp_4.keys',key_resp_4.keys)
    if key_resp_4.keys != None:  # we had a response
        thisExp.addData('key_resp_4.rt', key_resp_4.rt)
    thisExp.addData('key_resp_4.started', key_resp_4.tStartRefresh)
    thisExp.addData('key_resp_4.stopped', key_resp_4.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()


def runRoutineThreeBack ():
    process.reset()
    # ------Prepare to start Routine "Instructions3"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_7.keys = []
    key_resp_7.rt = []
    _key_resp_7_allKeys = []
    # keep track of which components have finished
    Instructions3Components = [text_6, key_resp_7]
    for thisComponent in Instructions3Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    Instructions3Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Instructions3"-------
    while continueRoutine:
        # get current time
        t = Instructions3Clock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=Instructions3Clock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_6* updates
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            text_6.setAutoDraw(True)

        # *key_resp_7* updates
        waitOnFlip = False
        if key_resp_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_7.frameNStart = frameN  # exact frame index
            key_resp_7.tStart = t  # local t and not account for scr refresh
            key_resp_7.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_7, 'tStartRefresh')  # time at next scr refresh
            key_resp_7.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_7.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_7.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_7.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_7.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_7_allKeys.extend(theseKeys)
            if len(_key_resp_7_allKeys):
                key_resp_7.keys = _key_resp_7_allKeys[-1].name  # just the last key pressed
                key_resp_7.rt = _key_resp_7_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Instructions3Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Instructions3"-------
    for thisComponent in Instructions3Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_6.started', text_6.tStartRefresh)
    thisExp.addData('text_6.stopped', text_6.tStopRefresh)
    # check responses
    if key_resp_7.keys in ['', [], None]:  # No response was made
        key_resp_7.keys = None
    thisExp.addData('key_resp_7.keys',key_resp_7.keys)
    if key_resp_7.keys != None:  # we had a response
        thisExp.addData('key_resp_7.rt', key_resp_7.rt)
    thisExp.addData('key_resp_7.started', key_resp_7.tStartRefresh)
    thisExp.addData('key_resp_7.stopped', key_resp_7.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Instructions3" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    Block3_3back = data.TrialHandler(nReps=1, method='random',
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions('3_back_task.xlsx'),
        seed=None, name='Block3_3back')
    thisExp.addLoop(Block3_3back)  # add the loop to the experiment
    thisBlock3_3back = Block3_3back.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock3_3back.rgb)
    if thisBlock3_3back != None:
        for paramName in thisBlock3_3back:
            exec('{} = thisBlock3_3back[paramName]'.format(paramName))

    all_letters = []
    data_exp = pd.read_excel('3_back_task.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['numbers'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['colourtest'])
    iteration = -1
    #process.reset()
    #random.shuffle (Block3_3back)
    for thisBlock3_3back in Block3_3back:
        iteration += 1
        print ('ITERATION:', iteration)
        currentLoop = Block3_3back
        # abbreviate parameter names if possible (e.g. rgb = thisBlock3_3back.rgb)
        if thisBlock3_3back != None:
            for paramName in thisBlock3_3back:
                exec('{} = thisBlock3_3back[paramName]'.format(paramName))

        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(10.000000)
        # update component parameters for each repeat
        Fix.setColor('white', colorSpace='rgb')
        Fix.setPos((0, 0))
        Fix.setText('')
        Fix.setFont('Arial')
        Fix.setHeight(0.1)
        # keep track of which components have finished
        FixationComponents = [Fix]
        for thisComponent in FixationComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        #process.reset()
        # -------Run Routine "Fixation"-------
        while continueRoutine: #and routineTimer.getTime() > 0:
            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *Fix* updates
            if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Fix.frameNStart = frameN  # exact frame index
                Fix.tStart = t  # local t and not account for scr refresh
                Fix.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
                Fix.setAutoDraw(True)
            if Fix.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    Fix.tStop = t  # not accounting for scr refresh
                    Fix.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
                    Fix.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
            # frame = input.get_frame()
            # process.frame_in = frame
            # process.run()
            # frame = process.frame_out #get the frame to show in GUI
            # bpm = process.bpm #get the bpm change over the time
            # i+=1
            # #print (i,' ',process.bpms)
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         continueRoutine = False
        finishedCalibration = False
        i = 0
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        while (not finishedCalibration):
            frame = input.get_frame()
            process.frame_in = frame
            process.run()
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print (i,' ',bpm)
            i+=1
            if (bpm == 0):
                finishedCalibration = False
                continue
            finishedCalibration = True
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         finishedCalibration = False
        # -------Ending Routine "Fixation"-------
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block3_3back.addData('Fix.started', Fix.tStartRefresh)
        Block3_3back.addData('Fix.stopped', Fix.tStopRefresh)

        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        routineTimer.add(1.000000)
        # update component parameters for each repeat
        if (iteration >= len (all_letters)):
            break
        curr_letter = all_letters [iteration]
        #text_7.setText(thisBlock1_1back ['colourtest'])
        text_7.setText (curr_letter)
        #text_7.setText(thisBlock3_3back['colourtest'])
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # keep track of which components have finished
        trialComponents = [text_7, key_resp_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        flag = False
        mySound = sound.Sound(secs = 0.5)
        # -------Run Routine "trial"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_7* updates
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                text_7.setAutoDraw(True)
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
                    text_7.setAutoDraw(False)

            # *key_resp_3* updates
            waitOnFlip = False
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_3.tStop = t  # not accounting for scr refresh
                    key_resp_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
                    key_resp_3.status = FINISHED
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
                    key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
                    # was this correct?
                    # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
                    #     key_resp_3.corr = 1
                    # else:
                    #     key_resp_3.corr = 0
                    # a response ends the routine
                    continueRoutine = False
            print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1]!= all_letters[iteration])
            if 'space' in key_resp_3.keys and flag==False and iteration > 0 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 1]:
                print (all_letters[iteration], ' ', all_letters[iteration - 1])
                nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.play(when = nextFlip)  # sync with screen refresh
                print ('CLICK.................................................')
                flag = True
                #mySound = sound.Sound()
                # = ptb.GetSecs()
                #ySound.play()
            #else:
             #   mySound.stop()
            # check for quit (typically the Esc key)

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        frame = input.get_frame()
        process.frame_in = frame
        process.run()
        frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm
        if process.bpms.__len__() > 50:
            if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                print ('current bpm:', ' ', bpm)
        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        #Block3_3back.addData ('correctness', label_correct)
        Block3_3back.addData('text_7.started', text_7.tStartRefresh)
        Block3_3back.addData('text_7.stopped', text_7.tStopRefresh)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
            # was no response the correct answer?!
            # if str(corresp).lower() == 'none':
            #     key_resp_3.corr = 1;  # correct non-response
            # else:
            #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
        # store data for Block3_3back (TrialHandler)
        Block3_3back.addData('key_resp_3.keys',key_resp_3.keys)
        Block3_3back.addData('key_resp_3.corr', key_resp_3.corr)
        if key_resp_3.keys != None:  # we had a response
            Block3_3back.addData('key_resp_3.rt', key_resp_3.rt)
        Block3_3back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
        Block3_3back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
        Block3_3back.addData('bpm', bpm)
        thisExp.nextEntry()

    # completed 1 repeats of 'Block3_3back'

    # ------Prepare to start Routine "Response"-------
    message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    message.text = "Please rate the difficulty of the previous task"
    scales = '1=Easy                       10=Very Difficult'
    ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    while ratingScale.noResponse:
        message.draw()
        ratingScale.draw()
        win.flip()
    rating = ratingScale.getRating()
    decisionTime = ratingScale.getRT()
    choiceHistory = ratingScale.getHistory()
    #win.close()
    print('rating 3', rating)
    print('decisionTime 3', decisionTime)
    print('choiceHistory 3',choiceHistory)
    Block3_3back.addData('text_7.started', 0)
    Block3_3back.addData('text_7.stopped', 0)
    Block3_3back.addData('key_resp_3.keys',0)
    Block3_3back.addData('key_resp_3.corr', 0)
    if key_resp_3.keys != None:  # we had a response
        Block3_3back.addData('key_resp_3.rt', 0)
    Block3_3back.addData('key_resp_3.started', 0)
    Block3_3back.addData('key_resp_3.stopped', 0)
    Block3_3back.addData('bpm', 0)
    Block3_3back.addData('diffuculty rating 1', rating)
    Block3_3back.addData('decision time to rate 1', decisionTime)
    thisExp.nextEntry()
    #thisExp.addData('diffuculty rating 3', rating)
    #thisExp.addData('decision time to rate 3', decisionTime)
    #thisExp.nextEntry()

    # get names of stimulus parameters
    if Block3_3back.trialList in ([], [None], None):
        params = []
    else:
        params = Block3_3back.trialList[0].keys()
    # save data for this loop
    Block3_3back.saveAsExcel(filename + 'Block3_3back.xlsx', sheetName='Block3_3back',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])
    Block3_3back.saveAsText(filename + 'Block3_3back.csv', delim=',',
        stimOut=params,
        dataOut=['n','all_mean','all_std', 'all_raw'])

def runRoutineOneBack (music_type):
    label_correct = 'incorrect'
    pathNeg = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Negative Pictures\Selected N'
    pathPos = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Positive Pictures\selected p'
    negative_images = os.listdir (pathNeg)
    positive_images = os.listdir (pathPos)
    negative_images = [os.path.join(pathNeg, image) for image in negative_images]
    positive_images = [os.path.join(pathPos, image) for image in positive_images]
    sound_happy = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Happy.ogg'
    sound_sad = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Sad.ogg'
    sounds = [sound_sad,sound_happy]
    process.reset()
    # ------Prepare to start Routine "Instructions"-------
    continueRoutine = True
    # update component parameters for each repeat
    print (key_resp_2)
    key_resp_2.keys = []
    key_resp_2.rt = []
    _key_resp_2_allKeys = []
    # keep track of which components have finished
    InstructionsComponents = [text, key_resp_2]
    for thisComponent in InstructionsComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    InstructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Instructions"-------
    while continueRoutine:
        # get current time
        t = InstructionsClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=InstructionsClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text* updates
        if text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text.frameNStart = frameN  # exact frame index
            text.tStart = t  # local t and not account for scr refresh
            text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
            text.setAutoDraw(True)

        # *key_resp_2* updates
        waitOnFlip = False
        if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.tStart = t  # local t and not account for scr refresh
            key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_2.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_2.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_2_allKeys.extend(theseKeys)
            if len(_key_resp_2_allKeys):
                key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
                key_resp_2.rt = _key_resp_2_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in InstructionsComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Instructions"-------
    for thisComponent in InstructionsComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text.started', text.tStartRefresh)
    thisExp.addData('text.stopped', text.tStopRefresh)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys = None
    thisExp.addData('key_resp_2.keys',key_resp_2.keys)
    if key_resp_2.keys != None:  # we had a response
        thisExp.addData('key_resp_2.rt', key_resp_2.rt)
    thisExp.addData('key_resp_2.started', key_resp_2.tStartRefresh)
    thisExp.addData('key_resp_2.stopped', key_resp_2.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Instructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    if (music_type == 'sad'):
        Block1_1back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('1_back_task_sad.xlsx'),
            seed=None, name='Block1_1back')
    else:
        Block1_1back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('1_back_task_happy.xlsx'),
            seed=None, name='Block1_1back')
    thisExp.addLoop(Block1_1back)  # add the loop to the experiment
    thisBlock1_1back = Block1_1back.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock1_1back.rgb)
    if thisBlock1_1back != None:
        for paramName in thisBlock1_1back:
            exec('{} = thisBlock1_1back[paramName]'.format(paramName))

    #random.shuffle (list (Block1_1back))
    all_letters = []
    if (music_type == 'sad'):
        data_exp = pd.read_excel('1_back_task_sad.xlsx')
    else:
        data_exp = pd.read_excel('1_back_task_happy.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['numbers'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['colourtest'])
    iteration = -1
    snd = random.choice (sounds)
    if (music_type == 'happy'):
        snd = sounds [1]
    else:
        snd = sounds [0]
    backMusic = sound.Sound(snd)
    backMusic.play ()
    print ('BEGIN::::PRINT', Block1_1back)
    bpms = []
    key_resp = []
    key_rt = []
    fix_started = []
    correct = []
    sound_l = []
    fix_end = []
    for thisBlock1_1back in Block1_1back:
        iteration += 1
        #core.wait(10) #wait for 10second
        print ('ITER:', iteration, ' ', len (all_letters))
        currentLoop = Block1_1back
        # abbreviate parameter names if possible (e.g. rgb = thisBlock1_1back.rgb)
        if thisBlock1_1back != None:
            for paramName in thisBlock1_1back:
                exec('{} = thisBlock1_1back[paramName]'.format(paramName))

        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(10.000000)
        # update component parameters for each repeat
        Fix.setColor('white', colorSpace='rgb')
        Fix.setPos((0, 0))
        Fix.setText('')
        Fix.setFont('Arial')
        Fix.setHeight(0.1)
        # keep track of which components have finished
        FixationComponents = [Fix]
        for thisComponent in FixationComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "Fixation"-------
        i=0

        while continueRoutine: # and routineTimer.getTime() > 0:
            if (backMusic.status == FINISHED):
                backMusic.play ()
            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            # *Fix* updates
            if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Fix.frameNStart = frameN  # exact frame index
                Fix.tStart = t  # local t and not account for scr refresh
                Fix.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
                Fix.setAutoDraw(True)
            if Fix.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    Fix.tStop = t  # not accounting for scr refresh
                    Fix.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
                    Fix.setAutoDraw(False)
            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        finishedCalibration = False
        i = 0
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        while (not finishedCalibration):
            frame = input.get_frame()
            process.frame_in = frame
            process.run()
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print (i,' ',bpm)
            i+=1
            if (bpm == 0):
                finishedCalibration = False
                continue
            finishedCalibration = True
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         finishedCalibration = False

        # -------Ending Routine "Fixation"-------
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        Block1_1back.addData('Fix.started', Fix.tStartRefresh)
        Block1_1back.addData('Fix.stopped', Fix.tStopRefresh)
        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        routineTimer.reset ()
        routineTimer.add(2.000000)
        # update component parameters for each repeat

        print ('CURRENT LETTER IS:', thisBlock1_1back ['numbers'])
        if (iteration >= len (all_letters)):
            break
        curr_letter = all_letters [iteration]
        #text_7.setText(thisBlock1_1back ['colourtest'])
        text_7.setText (curr_letter)
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # keep track of which components have finished
        trialComponents = [text_7, key_resp_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        flag = False
        mySound = sound.Sound(secs = 0.5)
        # -------Run Routine "trial"-------
        i = 0
        label_correct = 'incorrect'
        while continueRoutine and routineTimer.getTime() > 0:
            print ('gggg:', iteration)
            # get current time
            #get the bpm change over the time
            #i+=1
            #print (i,' ',process.bpms)
            #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            #cv2.imshow('frame', frame)
                        #self.lblHR2.setText("Heart Rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_7* updates
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                text_7.setAutoDraw(True)
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
                    text_7.setAutoDraw(False)

            # *key_resp_3* updates
            waitOnFlip = False
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_3.tStop = t  # not accounting for scr refresh
                    key_resp_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
                    key_resp_3.status = FINISHED
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
                    key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
                    # was this correct?
                    # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
                    #     key_resp_3.corr = 1
                    # else:
                    #     key_resp_3.corr = 0
                    # a response ends the routine
                    continueRoutine = False

            # check for quit (typically the Esc key)
            #if 'space' in key_resp_3.keys:
            print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1] != all_letters[iteration], iteration - 1)
            #mySound = sound.Sound('A')
            if 'space' in key_resp_3.keys and flag==False and iteration > 0 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 1]:
                print (all_letters[iteration], ' ', all_letters[iteration - 1])
                nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.play(when = nextFlip)  # sync with screen refresh
                print ('CLICK.................................................')
                flag = True
                label_correct = 'incorrect'
                #mySound = sound.Sound()
                # = ptb.GetSecs()
                #ySound.play()
            else:
                if 'space' in key_resp_3.keys and iteration > 0 and iteration < len (all_letters) and all_letters[iteration] == all_letters[iteration - 1]:
                    label_correct = 'correct'
                #mySound.stop()

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()



        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        #print ('bpm is:', bpm)
        #if process.bpms.__len__() > 50:
        #    if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
        #        print ('current bpm:', ' ', bpm)
        frame = input.get_frame()
        process.frame_in = frame
        #print (len (process.bpms))
        process.run()
        #frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm
        Block1_1back.addData ('correctness', label_correct)
        Block1_1back.addData('text_7.started', text_7.tStartRefresh)
        Block1_1back.addData('text_7.stopped', text_7.tStopRefresh)



        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
            key_resp3 = ''
        else:
            key_resp3 = 'space'
            # # was no response the correct answer?!
            # if str(corresp).lower() == 'none':
            #     key_resp_3.corr = 1;  # correct non-response
            # else:
            #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
        # store data for Block1_1back (TrialHandler)
        print ('ITERATION-VLAUEFDF:', iteration)
        print ('KEY RESPONSE:', key_resp3)
        Block1_1back.addData('key_resp_3.keys',key_resp3)
        #Block1_1back.addData('key_resp_3.corr', key_resp_3.corr)
        #if key_resp_3.keys != None:  # we had a response

        #Block1_1back.addData('key_resp_3.rt', key_resp_3.rt)

        #Block1_1back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
        #Block1_1back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
        Block1_1back.addData('bpm', bpm)
        Block1_1back.addData('sound', snd.split ('\\')[-1])
        sound_l.append (snd.split ('\\')[-1])
        bpms.append (bpm)
        correct.append (label_correct)
        key_resp.append (key_resp3)
        fix_started.append (Fix.tStartRefresh)
        fix_end.append (Fix.tStopRefresh)
        #print ('DFJKFJKFJDJKFDJFKD:', Block1_1back)
        #thisExp.nextEntry()
    backMusic.stop()
    # completed 1 repeats of 'Block1_1back'
    #print ('DFJKFJKFJDJKFDJFKD:', Block1_1back)

    # ------Prepare to start Routine "Break"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_4.keys = []
    key_resp_4.rt = []
    _key_resp_4_allKeys = []
    # keep track of which components have finished
    BreakComponents = [text_2, key_resp_4]
    for thisComponent in BreakComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    BreakClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Break"-------
    while continueRoutine:
        # get current time
        t = BreakClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=BreakClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_2* updates
        if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_2.frameNStart = frameN  # exact frame index
            text_2.tStart = t  # local t and not account for scr refresh
            text_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
            text_2.setAutoDraw(True)

        # *key_resp_4* updates
        waitOnFlip = False
        if key_resp_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_4.frameNStart = frameN  # exact frame index
            key_resp_4.tStart = t  # local t and not account for scr refresh
            key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
            key_resp_4.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_4.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_4.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_4.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_4_allKeys.extend(theseKeys)
            if len(_key_resp_4_allKeys):
                key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
                key_resp_4.rt = _key_resp_4_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in BreakComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Break"-------
    for thisComponent in BreakComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_2.started', text_2.tStartRefresh)
    thisExp.addData('text_2.stopped', text_2.tStopRefresh)
    # check responses
    if key_resp_4.keys in ['', [], None]:  # No response was made
        key_resp_4.keys = None
    thisExp.addData('key_resp_4.keys',key_resp_4.keys)
    if key_resp_4.keys != None:  # we had a response
        thisExp.addData('key_resp_4.rt', key_resp_4.rt)
    thisExp.addData('key_resp_4.started', key_resp_4.tStartRefresh)
    thisExp.addData('key_resp_4.stopped', key_resp_4.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    # ------Prepare to start Routine "Response"-------
    message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    message.text = "Please rate the difficulty of the previous task"
    scales = '1=Easy                       10=Very Difficult'
    ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    while ratingScale.noResponse:
        message.draw()
        ratingScale.draw()
        win.flip()
        #print ('no response...')
    rating = ratingScale.getRating()
    decisionTime = ratingScale.getRT()
    choiceHistory = ratingScale.getHistory()
    print('rating', rating)
    print('decisionTime', decisionTime)
    print('choiceHistory',choiceHistory)
    #Block1_1back.addData('text_7.started', 0)
    #Block1_1back.addData('text_7.stopped', 0)
    #Block1_1back.addData('key_resp_3.keys',0)
    #Block1_1back.addData('key_resp_3.corr', 0)
    #if key_resp_3.keys != None:  # we had a response
    #    Block1_1back.addData('key_resp_3.rt', 0)
    #Block1_1back.addData('key_resp_3.started', 0)
    #Block1_1back.addData('key_resp_3.stopped', 0)
    #Block1_1back.addData('bpm', 0)
    #Block1_1back.addData('diffuculty rating 1', rating)
    #Block1_1back.addData('decision time to rate 1', decisionTime)
    #thisExp.nextEntry()
    continueRoutine = True
    win.flip()
    diff = [rating] * len (bpms)
    df = pd.DataFrame ({'bpms':bpms, 'key_resp':key_resp, 'fix_started':fix_started,'fix_end':fix_end, 'correctness':correct, 'sound':sound_l, 'difficulty':diff})
    df.to_excel ('data/experiment.xlsx')
    # get names of stimulus parameters
    if Block1_1back.trialList in ([], [None], None):
        params = []
    else:
        params = Block1_1back.trialList[0].keys()
    # save data for this loop
    print ('fdfjkdfjkfd:', Block1_1back)
    if (music_type =='sad'):
        Block1_1back.saveAsExcel(filename + 'Block1_1back_sad.xlsx', sheetName='Block1_1back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block1_1back.saveAsText(filename + 'Block1_1back_sad.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    else:
        Block1_1back.saveAsExcel(filename + 'Block1_1back_happy.xlsx', sheetName='Block1_1back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block1_1back.saveAsText(filename + 'Block1_1back_happy.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])

    # # update component parameters for each repeat
    # key_response.keys = []
    # key_response.rt = []

    # _key_resp_res_allKeys = []

    # # keep track of which components have finished
    # ResponseComponents = [text_response, key_response]
    # for thisComponent in ResponseComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # ResponseClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "Break"-------
    # while continueRoutine:
    #     # get current time
    #     t = ResponseClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=ResponseClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     # *text_2* updates
    #     if text_response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         text_response.frameNStart = frameN  # exact frame index
    #         text_response.tStart = t  # local t and not account for scr refresh
    #         text_response.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(text_response, 'tStartRefresh')  # time at next scr refresh
    #         text_response.setAutoDraw(True)

    #     # *key_resp_4* updates
    #     waitOnFlip = False
    #     if key_response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         key_response.frameNStart = frameN  # exact frame index
    #         key_response.tStart = t  # local t and not account for scr refresh
    #         key_response.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(key_response, 'tStartRefresh')  # time at next scr refresh
    #         key_response.status = STARTED
    #         # keyboard checking is just starting
    #         waitOnFlip = True
    #         win.callOnFlip(key_response.clock.reset)  # t=0 on next screen flip
    #         win.callOnFlip(key_response.clearEvents, eventType='keyboard')  # clear events on next screen flip
    #     if key_response.status == STARTED and not waitOnFlip:
    #         theseKeys = key_response.getKeys(keyList=['space'], waitRelease=False)
    #         _key_resp_res_allKeys.extend(theseKeys)
    #         if len(_key_resp_res_allKeys):
    #             key_resp_res.keys = _key_resp_res_allKeys[-1].name  # just the last key pressed
    #             key_resp_res.rt = _key_resp_res_allKeys[-1].rt
    #             # a response ends the routine
    #             continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()

    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in ResponseComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished

    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "Response"-------
    # for thisComponent in ResponseComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # thisExp.addData('text_response.started', text_response.tStartRefresh)
    # thisExp.addData('text_response.stopped', text_response.tStopRefresh)
    # # check responses
    # if key_response.keys in ['', [], None]:  # No response was made
    #     key_response.keys = None
    # thisExp.addData('key_response.keys',key_response.keys)
    # if key_response.keys != None:  # we had a response
    #     thisExp.addData('key_response.rt', key_response.rt)
    # thisExp.addData('key_response.started', key_response.tStartRefresh)
    # thisExp.addData('key_response.stopped', key_response.tStopRefresh)
    # thisExp.nextEntry()
    # # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    # # ------Prepare to start Routine "Instructions2"-------
    # continueRoutine = True
    # # update component parameters for each repeat
    # key_resp_6.keys = []
    # key_resp_6.rt = []
    # _key_resp_6_allKeys = []
    # # keep track of which components have finished
    # Instructions2Components = [text_5, key_resp_6]
    # for thisComponent in Instructions2Components:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # Instructions2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

def runRoutineTwoBackUpd (music_type):
    label_correct = 'incorrect'
    pathNeg = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Negative Pictures\Selected N'
    pathPos = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Positive Pictures\selected p'
    negative_images = os.listdir (pathNeg)
    positive_images = os.listdir (pathPos)
    negative_images = [os.path.join(pathNeg, image) for image in negative_images]
    positive_images = [os.path.join(pathPos, image) for image in positive_images]
    sound_happy = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Happy.ogg'
    sound_sad = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Sad.ogg'
    sounds = [sound_sad,sound_happy]
    process.reset()
    # ------Prepare to start Routine "Instructions2"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_6.keys = []
    key_resp_6.rt = []
    _key_resp_6_allKeys = []
    # keep track of which components have finished
    Instructions2Components = [text_5, key_resp_6]
    for thisComponent in Instructions2Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    label_correct = 'incorrect'
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    Instructions2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    routineTimer.reset()
    print ('Before instruction 2')
    # -------Run Routine "Instructions2"-------
    while continueRoutine:
        #print (text_5.status)
        #break
        #exit()
        # get current time
        t = Instructions2Clock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=Instructions2Clock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_5* updates
        if text_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            print ('text_5')
            # keep track of start time/frame for later
            text_5.frameNStart = frameN  # exact frame index
            text_5.tStart = t  # local t and not account for scr refresh
            text_5.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_5, 'tStartRefresh')  # time at next scr refresh
            text_5.setAutoDraw(True)

        # *key_resp_6* updates
        waitOnFlip = False
        if key_resp_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_6.frameNStart = frameN  # exact frame index
            key_resp_6.tStart = t  # local t and not account for scr refresh
            key_resp_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_6, 'tStartRefresh')  # time at next scr refresh
            key_resp_6.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_6.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_6.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_6.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_6.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_6_allKeys.extend(theseKeys)
            if len(_key_resp_6_allKeys):
                key_resp_6.keys = _key_resp_6_allKeys[-1].name  # just the last key pressed
                key_resp_6.rt = _key_resp_6_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Instructions2Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Instructions2"-------
    for thisComponent in Instructions2Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_5.started', text_5.tStartRefresh)
    thisExp.addData('text_5.stopped', text_5.tStopRefresh)
    # check responses
    if key_resp_6.keys in ['', [], None]:  # No response was made
        key_resp_6.keys = None
    thisExp.addData('key_resp_6.keys',key_resp_6.keys)
    if key_resp_6.keys != None:  # we had a response
        thisExp.addData('key_resp_6.rt', key_resp_6.rt)
    thisExp.addData('key_resp_6.started', key_resp_6.tStartRefresh)
    thisExp.addData('key_resp_6.stopped', key_resp_6.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Instructions2" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    if (music_type == 'sad'):
        Block2_2back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('2_back_task_sad.xlsx'),
            seed=None, name='Block2_2back')
    else:
        Block2_2back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('2_back_task_happy.xlsx'),
            seed=None, name='Block2_2back')
    thisExp.addLoop(Block2_2back)  # add the loop to the experiment
    thisBlock2_2back = Block2_2back.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock2_2back.rgb)
    if thisBlock2_2back != None:
        for paramName in thisBlock2_2back:
            exec('{} = thisBlock2_2back[paramName]'.format(paramName))
    #random.shuffle (Block2_2back)
    all_letters = []
    if (music_type == 'sad'):
        data_exp = pd.read_excel('2_back_task_sad.xlsx')
    else:
        data_exp = pd.read_excel('2_back_task_happy.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['numbers'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['colourtest'])
    iteration = -1
    snd = random.choice (sounds)
    if (music_type == 'happy'):
        snd = sounds [1]
    else:
        snd = sounds [0]
    backMusic = sound.Sound(snd)
    backMusic.play ()
    bpms = []
    key_resp = []
    key_rt = []
    fix_started = []
    correct = []
    sound_l = []
    fix_end = []
    for thisBlock2_2back in Block2_2back:
        currentLoop = Block2_2back
        iteration += 1
        # abbreviate parameter names if possible (e.g. rgb = thisBlock2_2back.rgb)
        if thisBlock2_2back != None:
            for paramName in thisBlock2_2back:
                exec('{} = thisBlock2_2back[paramName]'.format(paramName))

        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(10.000000)
        # update component parameters for each repeat
        Fix.setColor('white', colorSpace='rgb')
        Fix.setPos((0, 0))
        Fix.setText('')
        Fix.setFont('Arial')
        Fix.setHeight(0.1)
        # keep track of which components have finished
        FixationComponents = [Fix]
        for thisComponent in FixationComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        # -------Run Routine "Fixation"-------
        while continueRoutine: #and routineTimer.getTime() > 0:
            if (backMusic.status == FINISHED):
                backMusic.play ()
            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *Fix* updates
            if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Fix.frameNStart = frameN  # exact frame index
                Fix.tStart = t  # local t and not account for scr refresh
                Fix.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
                Fix.setAutoDraw(True)
            if Fix.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    Fix.tStop = t  # not accounting for scr refresh
                    Fix.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
                    Fix.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
            # frame = input.get_frame()
            # process.frame_in = frame
            # process.run()
            # frame = process.frame_out #get the frame to show in GUI
            # bpm = process.bpm #get the bpm change over the time
            # i+=1
            # #print (i,' ',process.bpms)
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         continueRoutine = False
        finishedCalibration = False
        i = 0
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        while (not finishedCalibration):
            frame = input.get_frame()
            print (frame)
            process.frame_in = frame
            process.run()
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print (i,' ',bpm)
            i+=1
            if (bpm == 0):
                finishedCalibration = False
                continue
            finishedCalibration = True
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         finishedCalibration = False

        # -------Ending Routine "Fixation"-------
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block2_2back.addData('Fix.started', Fix.tStartRefresh)
        Block2_2back.addData('Fix.stopped', Fix.tStopRefresh)

        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        routineTimer.add(1.000000)
        # update component parameters for each repeat
        #text_7.setText(thisBlock2_2back['colourtest'])
        if (iteration >= len (all_letters)):
            break
        curr_letter = all_letters [iteration]
        #text_7.setText(thisBlock1_1back ['colourtest'])
        text_7.setText (curr_letter)
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # keep track of which components have finished
        trialComponents = [text_7, key_resp_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        flag = False
        mySound = sound.Sound(secs = 0.5)
        # -------Run Routine "trial"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_7* updates
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                text_7.setAutoDraw(True)
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
                    text_7.setAutoDraw(False)

            # *key_resp_3* updates
            waitOnFlip = False
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_3.tStop = t  # not accounting for scr refresh
                    key_resp_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
                    key_resp_3.status = FINISHED
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
                    key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
                    # was this correct?
                    # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
                    #     key_resp_3.corr = 1
                    # else:
                    #     key_resp_3.corr = 0
                    # a response ends the routine
                    continueRoutine = False
            #mySound = sound.Sound('A')
            label_correct = 'incorrect'
            print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1]!= all_letters[iteration])
            if 'space' in key_resp_3.keys and flag==False and iteration > 1 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 2]:
                print (all_letters[iteration], ' ', all_letters[iteration - 1])
                nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.play(when = nextFlip)  # sync with screen refresh
                print ('CLICK.................................................')
                flag = True
                label_correct = 'incorrect'
                #mySound = sound.Sound()
                # = ptb.GetSecs()
                #ySound.play()
            else:
                if 'space' in key_resp_3.keys and iteration > 1 and iteration < len (all_letters) and all_letters[iteration] == all_letters[iteration - 2]:
                    label_correct = 'correct'
                #mySound.stop()
            # check for quit (typically the Esc key)

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        frame = input.get_frame()
        process.frame_in = frame
        process.run()
        frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm
        if process.bpms.__len__() >50:
            if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                print ('current bpm:', ' ', bpm)
        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block2_2back.addData ('correctness', label_correct)
        Block2_2back.addData('text_7.started', text_7.tStartRefresh)
        Block2_2back.addData('text_7.stopped', text_7.tStopRefresh)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
            key_resp3 = ''
        else:
            key_resp3 = 'space'
            # was no response the correct answer?!
            # if str(corresp).lower() == 'none':
            #     key_resp_3.corr = 1;  # correct non-response
            # else:
            #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
        # store data for Block2_2back (TrialHandler)
        sound_l.append (snd.split ('\\')[-1])
        bpms.append (bpm)
        correct.append (label_correct)
        key_resp.append (key_resp3)
        fix_started.append (Fix.tStartRefresh)
        fix_end.append (Fix.tStopRefresh)
        Block2_2back.addData('key_resp_3.keys',key_resp_3.keys)
        Block2_2back.addData('key_resp_3.corr', key_resp_3.corr)
        if key_resp_3.keys != None:  # we had a response
            Block2_2back.addData('key_resp_3.rt', key_resp_3.rt)
        Block2_2back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
        Block2_2back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
        Block2_2back.addData('bpm', bpm)
        Block2_2back.addData('sound', snd.split ('\\')[-1])
        thisExp.nextEntry()
    backMusic.stop()
    # completed 1 repeats of 'Block2_2back'

    # ------Prepare to start Routine "Response"-------
    message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    message.text = "Please rate the difficulty of the previous task"
    scales = '1=Easy                       10=Very Difficult'
    ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    while ratingScale.noResponse:
        message.draw()
        ratingScale.draw()
        win.flip()
    rating = ratingScale.getRating()
    decisionTime = ratingScale.getRT()
    choiceHistory = ratingScale.getHistory()
    #win.close()

    print('rating 2', rating)
    print('decisionTime 2', decisionTime)
    print('choiceHistory 2',choiceHistory)
    #thisExp.addData('diffuculty rating 2', rating)
    #thisExp.addData('decision time to rate 2', decisionTime)
    #thisExp.nextEntry()
    Block2_2back.addData('text_7.started', 0)
    Block2_2back.addData('text_7.stopped', 0)
    Block2_2back.addData('key_resp_3.keys',0)
    Block2_2back.addData('key_resp_3.corr', 0)
    if key_resp_3.keys != None:  # we had a response
        Block2_2back.addData('key_resp_3.rt', 0)
    Block2_2back.addData('key_resp_3.started', 0)
    Block2_2back.addData('key_resp_3.stopped', 0)
    Block2_2back.addData('bpm', 0)
    Block2_2back.addData('diffuculty rating 1', rating)
    Block2_2back.addData('decision time to rate 1', decisionTime)
    thisExp.nextEntry()
    # get names of stimulus parameters
    diff = [rating] * len (bpms)
    df = pd.DataFrame ({'bpms':bpms, 'key_resp':key_resp, 'fix_started':fix_started,'fix_end':fix_end, 'correctness':correct, 'sound':sound_l, 'difficulty':diff})
    df.to_excel ('data/experiment2.xlsx')
    if Block2_2back.trialList in ([], [None], None):
        params = []
    else:
        params = Block2_2back.trialList[0].keys()
    # save data for this loop
    if (music_type =='sad'):
        Block2_2back.saveAsExcel(filename + 'Block2_2back_sad.xlsx', sheetName='Block2_2back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block2_2back.saveAsText(filename + 'Block2_2back_sad.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    else:
        Block2_2back.saveAsExcel(filename + 'Block2_2back_happy.xlsx', sheetName='Block2_2back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block2_2back.saveAsText(filename + 'Block2_2back_happy.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])

    # ------Prepare to start Routine "Break"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_4.keys = []
    key_resp_4.rt = []
    _key_resp_4_allKeys = []
    # keep track of which components have finished
    BreakComponents = [text_2, key_resp_4]
    for thisComponent in BreakComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    BreakClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Break"-------
    while continueRoutine:
        # get current time
        t = BreakClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=BreakClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_2* updates
        if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_2.frameNStart = frameN  # exact frame index
            text_2.tStart = t  # local t and not account for scr refresh
            text_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
            text_2.setAutoDraw(True)

        # *key_resp_4* updates
        waitOnFlip = False
        if key_resp_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_4.frameNStart = frameN  # exact frame index
            key_resp_4.tStart = t  # local t and not account for scr refresh
            key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
            key_resp_4.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_4.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_4.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_4.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_4_allKeys.extend(theseKeys)
            if len(_key_resp_4_allKeys):
                key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
                key_resp_4.rt = _key_resp_4_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in BreakComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Break"-------
    for thisComponent in BreakComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_2.started', text_2.tStartRefresh)
    thisExp.addData('text_2.stopped', text_2.tStopRefresh)
    # check responses
    if key_resp_4.keys in ['', [], None]:  # No response was made
        key_resp_4.keys = None
    thisExp.addData('key_resp_4.keys',key_resp_4.keys)
    if key_resp_4.keys != None:  # we had a response
        thisExp.addData('key_resp_4.rt', key_resp_4.rt)
    thisExp.addData('key_resp_4.started', key_resp_4.tStartRefresh)
    thisExp.addData('key_resp_4.stopped', key_resp_4.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Break" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()


def runRoutineThreeBackUpd (music_type):
    label_correct = 'no reponse'
    pathNeg = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Negative Pictures\Selected N'
    pathPos = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Positive Pictures\selected p'
    negative_images = os.listdir (pathNeg)
    positive_images = os.listdir (pathPos)
    negative_images = [os.path.join(pathNeg, image) for image in negative_images]
    positive_images = [os.path.join(pathPos, image) for image in positive_images]
    sound_happy = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Happy.ogg'
    sound_sad = r'C:\Users\dixit\Downloads\experiment2_fixed_order\dixit bpm10\Music\Sad.ogg'
    sounds = [sound_sad,sound_happy]
    process.reset()
    # ------Prepare to start Routine "Instructions3"-------
    continueRoutine = True
    # update component parameters for each repeat
    key_resp_7.keys = []
    key_resp_7.rt = []
    _key_resp_7_allKeys = []
    # keep track of which components have finished
    Instructions3Components = [text_6, key_resp_7]
    for thisComponent in Instructions3Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    Instructions3Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Instructions3"-------
    while continueRoutine:
        # get current time
        t = Instructions3Clock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=Instructions3Clock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_6* updates
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            text_6.setAutoDraw(True)

        # *key_resp_7* updates
        waitOnFlip = False
        if key_resp_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_7.frameNStart = frameN  # exact frame index
            key_resp_7.tStart = t  # local t and not account for scr refresh
            key_resp_7.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_7, 'tStartRefresh')  # time at next scr refresh
            key_resp_7.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_7.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_7.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_7.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_7.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_7_allKeys.extend(theseKeys)
            if len(_key_resp_7_allKeys):
                key_resp_7.keys = _key_resp_7_allKeys[-1].name  # just the last key pressed
                key_resp_7.rt = _key_resp_7_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Instructions3Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Instructions3"-------
    for thisComponent in Instructions3Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_6.started', text_6.tStartRefresh)
    thisExp.addData('text_6.stopped', text_6.tStopRefresh)
    # check responses
    if key_resp_7.keys in ['', [], None]:  # No response was made
        key_resp_7.keys = None
    thisExp.addData('key_resp_7.keys',key_resp_7.keys)
    if key_resp_7.keys != None:  # we had a response
        thisExp.addData('key_resp_7.rt', key_resp_7.rt)
    thisExp.addData('key_resp_7.started', key_resp_7.tStartRefresh)
    thisExp.addData('key_resp_7.stopped', key_resp_7.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "Instructions3" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    if (music_type == 'sad'):
        Block3_3back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('3_back_task_sad.xlsx'),
            seed=None, name='Block3_3back')
        thisExp.addLoop(Block3_3back)  # add the loop to the experiment
        thisBlock3_3back = Block3_3back.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisBlock3_3back.rgb)
        if thisBlock3_3back != None:
            for paramName in thisBlock3_3back:
                exec('{} = thisBlock3_3back[paramName]'.format(paramName))
    else:
        Block3_3back = data.TrialHandler(nReps=1, method='random',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions('3_back_task_happy.xlsx'),
            seed=None, name='Block3_3back')
        thisExp.addLoop(Block3_3back)  # add the loop to the experiment
        thisBlock3_3back = Block3_3back.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisBlock3_3back.rgb)
        if thisBlock3_3back != None:
            for paramName in thisBlock3_3back:
                exec('{} = thisBlock3_3back[paramName]'.format(paramName))

    all_letters = []
    if (music_type == 'sad'):
        data_exp = pd.read_excel('3_back_task_sad.xlsx')
    else:
        data_exp = pd.read_excel('3_back_task_happy.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['numbers'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['colourtest'])
    iteration = -1
    #process.reset()
    #random.shuffle (Block3_3back)
    snd = random.choice (sounds)
    if (music_type == 'happy'):
        snd = sounds [1]
    else:
        snd = sounds [0]
    backMusic = sound.Sound(snd)
    backMusic.play ()
    bpms = []
    key_resp = []
    key_rt = []
    fix_started = []
    correct = []
    sound_l = []
    fix_end = []
    for thisBlock3_3back in Block3_3back:
        iteration += 1
        print ('ITERATION:', iteration)
        currentLoop = Block3_3back
        # abbreviate parameter names if possible (e.g. rgb = thisBlock3_3back.rgb)
        if thisBlock3_3back != None:
            for paramName in thisBlock3_3back:
                exec('{} = thisBlock3_3back[paramName]'.format(paramName))

        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(10.000000)
        # update component parameters for each repeat
        Fix.setColor('white', colorSpace='rgb')
        Fix.setPos((0, 0))
        Fix.setText('')
        Fix.setFont('Arial')
        Fix.setHeight(0.1)
        # keep track of which components have finished
        FixationComponents = [Fix]
        for thisComponent in FixationComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        #process.reset()
        # -------Run Routine "Fixation"-------
        while continueRoutine: #and routineTimer.getTime() > 0:
            if (backMusic.status == FINISHED):
                backMusic.play ()
            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *Fix* updates
            if Fix.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Fix.frameNStart = frameN  # exact frame index
                Fix.tStart = t  # local t and not account for scr refresh
                Fix.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Fix, 'tStartRefresh')  # time at next scr refresh
                Fix.setAutoDraw(True)
            if Fix.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Fix.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    Fix.tStop = t  # not accounting for scr refresh
                    Fix.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Fix, 'tStopRefresh')  # time at next scr refresh
                    Fix.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
            # frame = input.get_frame()
            # process.frame_in = frame
            # process.run()
            # frame = process.frame_out #get the frame to show in GUI
            # bpm = process.bpm #get the bpm change over the time
            # i+=1
            # #print (i,' ',process.bpms)
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         continueRoutine = False
        finishedCalibration = False
        i = 0
        #process.reset()
        print ('TIMES:', process.times, len (process.times))
        while (not finishedCalibration):
            frame = input.get_frame()
            process.frame_in = frame
            process.run()
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print (i,' ',bpm)
            i+=1
            if (bpm == 0):
                finishedCalibration = False
                continue
            finishedCalibration = True
            # if process.bpms.__len__() >50:
            #     if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #         print ('current bpm:', ' ', bpm)
            #         break
            #     else:
            #         finishedCalibration = False
        # -------Ending Routine "Fixation"-------
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block3_3back.addData('Fix.started', Fix.tStartRefresh)
        Block3_3back.addData('Fix.stopped', Fix.tStopRefresh)

        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        routineTimer.add(1.000000)
        # update component parameters for each repeat
        if (iteration >= len (all_letters)):
            break
        curr_letter = all_letters [iteration]
        #text_7.setText(thisBlock1_1back ['colourtest'])
        text_7.setText (curr_letter)
        #text_7.setText(thisBlock3_3back['colourtest'])
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # keep track of which components have finished
        trialComponents = [text_7, key_resp_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        flag = False
        mySound = sound.Sound(secs = 0.5)
        # -------Run Routine "trial"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_7* updates
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                text_7.setAutoDraw(True)
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_7, 'tStopRefresh')  # time at next scr refresh
                    text_7.setAutoDraw(False)

            # *key_resp_3* updates
            waitOnFlip = False
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_3.tStop = t  # not accounting for scr refresh
                    key_resp_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_3, 'tStopRefresh')  # time at next scr refresh
                    key_resp_3.status = FINISHED
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = [key.name for key in _key_resp_3_allKeys]  # storing all keys
                    key_resp_3.rt = [key.rt for key in _key_resp_3_allKeys]
                    # was this correct?
                    # if (key_resp_3.keys == str(corresp)) or (key_resp_3.keys == corresp):
                    #     key_resp_3.corr = 1
                    # else:
                    #     key_resp_3.corr = 0
                    # a response ends the routine
                    continueRoutine = False
            label_correct = 'incorrect'
            print (all_letters[iteration], ' ', all_letters[iteration - 1], all_letters[iteration - 1]!= all_letters[iteration])
            if 'space' in key_resp_3.keys and flag==False and iteration > 2 and iteration < len (all_letters) and all_letters[iteration] != all_letters[iteration - 3]:
                print (all_letters[iteration], ' ', all_letters[iteration - 1])
                nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.play(when = nextFlip)  # sync with screen refresh
                print ('CLICK.................................................')
                flag = True
                label_correct = 'incorrect'
                #mySound = sound.Sound()
                # = ptb.GetSecs()
                #ySound.play()
            else:
                if 'space' in key_resp_3.keys and iteration > 2 and iteration < len (all_letters) and all_letters[iteration] == all_letters[iteration - 3]:
                    label_correct = 'correct'
             #   mySound.stop()
            # check for quit (typically the Esc key)

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        frame = input.get_frame()
        process.frame_in = frame
        process.run()
        frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm
        if process.bpms.__len__() > 50:
            if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                print ('current bpm:', ' ', bpm)
        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Block3_3back.addData ('correctness', label_correct)
        Block3_3back.addData('text_7.started', text_7.tStartRefresh)
        Block3_3back.addData('text_7.stopped', text_7.tStopRefresh)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
            key_resp3 = ''
        else:
            key_resp3 = 'space'
            # was no response the correct answer?!
            # if str(corresp).lower() == 'none':
            #     key_resp_3.corr = 1;  # correct non-response
            # else:
            #     key_resp_3.corr = 0;  # failed to respond (incorrectly)
        # store data for Block3_3back (TrialHandler)
        Block3_3back.addData('key_resp_3.keys',key_resp_3.keys)
        Block3_3back.addData('key_resp_3.corr', key_resp_3.corr)
        if key_resp_3.keys != None:  # we had a response
            Block3_3back.addData('key_resp_3.rt', key_resp_3.rt)
        Block3_3back.addData('key_resp_3.started', key_resp_3.tStartRefresh)
        Block3_3back.addData('key_resp_3.stopped', key_resp_3.tStopRefresh)
        Block3_3back.addData('bpm', bpm)
        Block3_3back.addData('sound', snd.split ('\\')[-1])
        sound_l.append (snd.split ('\\')[-1])
        bpms.append (bpm)
        correct.append (label_correct)
        key_resp.append (key_resp3)
        fix_started.append (Fix.tStartRefresh)
        fix_end.append (Fix.tStopRefresh)
        thisExp.nextEntry()
    backMusic.stop()
    # completed 1 repeats of 'Block3_3back'

    # ------Prepare to start Routine "Response"-------
    message = visual.TextStim(win=win, alignHoriz='center', pos=(0,0.75))
    message.text = "Please rate the difficulty of the previous task"
    scales = '1=Easy                       10=Very Difficult'
    ratingScale = visual.RatingScale(win=win, pos=(0,-0.75), scale=scales, size=0.75, stretch=1.5)
    while ratingScale.noResponse:
        message.draw()
        ratingScale.draw()
        win.flip()
    rating = ratingScale.getRating()
    decisionTime = ratingScale.getRT()
    choiceHistory = ratingScale.getHistory()
    #win.close()
    print('rating 3', rating)
    print('decisionTime 3', decisionTime)
    print('choiceHistory 3',choiceHistory)
    Block3_3back.addData('text_7.started', 0)
    Block3_3back.addData('text_7.stopped', 0)
    Block3_3back.addData('key_resp_3.keys',0)
    Block3_3back.addData('key_resp_3.corr', 0)
    if key_resp_3.keys != None:  # we had a response
        Block3_3back.addData('key_resp_3.rt', 0)
    Block3_3back.addData('key_resp_3.started', 0)
    Block3_3back.addData('key_resp_3.stopped', 0)
    Block3_3back.addData('bpm', 0)
    Block3_3back.addData('diffuculty rating 1', rating)
    Block3_3back.addData('decision time to rate 1', decisionTime)
    thisExp.nextEntry()
    #thisExp.addData('diffuculty rating 3', rating)
    #thisExp.addData('decision time to rate 3', decisionTime)
    #thisExp.nextEntry()
    diff = [rating] * len (bpms)
    df = pd.DataFrame ({'bpms':bpms, 'key_resp':key_resp, 'fix_started':fix_started,'fix_end':fix_end, 'correctness':correct, 'sound':sound_l, 'difficulty':diff})
    df.to_excel ('data/experiment3.xlsx')
    # get names of stimulus parameters
    if Block3_3back.trialList in ([], [None], None):
        params = []
    else:
        params = Block3_3back.trialList[0].keys()
    # save data for this loop
    if (music_type == 'sad'):
        Block3_3back.saveAsExcel(filename + 'Block3_3back_sad.xlsx', sheetName='Block3_3back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block3_3back.saveAsText(filename + 'Block3_3back_sad.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    else:
        Block3_3back.saveAsExcel(filename + 'Block3_3back_happy.xlsx', sheetName='Block3_3back',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        Block3_3back.saveAsText(filename + 'Block3_3back_happy.csv', delim=',',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])

def runRoutineThanks ():
    # ------Prepare to start Routine "Thanks"-------
    continueRoutine = True
    # update component parameters for each repeat
    # keep track of which components have finished
    ThanksComponents = [text_3]
    for thisComponent in ThanksComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ThanksClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    # -------Run Routine "Thanks"-------
    while continueRoutine:
        # get current time
        t = ThanksClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ThanksClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_3* updates
        if text_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_3.frameNStart = frameN  # exact frame index
            text_3.tStart = t  # local t and not account for scr refresh
            text_3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_3, 'tStartRefresh')  # time at next scr refresh
            text_3.setAutoDraw(True)

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in ThanksComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    # -------Ending Routine "Thanks"-------
    for thisComponent in ThanksComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('text_3.started', text_3.tStartRefresh)
    thisExp.addData('text_3.stopped', text_3.tStopRefresh)
    # the Routine "Thanks" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # Flip one final time so any remaining win.callOnFlip()
    # and win.timeOnFlip() tasks get executed before quitting
    win.flip()

    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename+'.csv', delim='auto')
    thisExp.saveAsPickle(filename)
    logging.flush()
    # make sure everything is closed down
    thisExp.abort()  # or data files will save again on exit
    win.close()
    core.quit()

order = [1,2,3,4,5,6]
#runRoutineOneBack()
random_order = random.shuffle (order)
for i in order:
    if (i == 3):
        runRoutineThreeBackUpd('sad')
    elif (i == 1):
        runRoutineOneBack('sad')
    elif (i == 2):
        runRoutineTwoBackUpd('sad')
    elif (i == 4):
        runRoutineThreeBackUpd('happy')
    elif (i == 5):
        runRoutineOneBack('happy')
    elif (i == 6):
        runRoutineTwoBackUpd('happy')

runRoutineThanks()