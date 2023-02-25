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
    text='Hello and welcome to the emotional task. Please stay steady and look at the screen\n\nPress space to continue.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0);
key_resp_5 = keyboard.Keyboard()

# Initialize components for Routine "Instructions"
InstructionsClock = core.Clock()

text = visual.TextStim(win=win, name='text',
    text='Please look at the blank screen \n It will starts in 10 seconds\n\nPress space to begin.',
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

def runEmpty ():
    hr = []
    st = []
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
    iteration = -1
    finishedCalibration = False
    i=0
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
    for i in range (24):
        core.wait(5.0)
        iteration += 1
        win.flip()
        frame = input.get_frame()
        process.frame_in = frame
        process.run()

        print ('after run')
        frame = process.frame_out #get the frame to show in GUI
        bpm = process.bpm #get the bpm change over the time
        print ('current value of BPM for iteration ', iteration,' :',bpm)
        hr.append (bpm)
        st.append ('Empty')

    df = DataFrame({'Heart Rate': hr, 'Stimuli Type': st})
    df.to_excel('empty_heart_rate.xlsx', sheet_name='One', index=False)
    return 0

from pandas import DataFrame

def runRoutineTwo ():
    hr = []
    st = []
    pathNeg = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Negative Pictures\Selected N'
    pathPos = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Positive Pictures\selected p'
    negative_images = os.listdir (pathNeg)
    positive_images = os.listdir (pathPos)
    negative_images = [os.path.join(pathNeg, image) for image in negative_images]
    positive_images = [os.path.join(pathPos, image) for image in positive_images]
    #print (negative_images)
    #return 0
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
    Block1_1back = data.TrialHandler(nReps=1, method='random',
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions('1_back_task.xlsx'),
        seed=None, name='Block1_1back')
    thisExp.addLoop(Block1_1back)  # add the loop to the experiment
    thisBlock1_1back = Block1_1back.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock1_1back.rgb)
    if thisBlock1_1back != None:
        for paramName in thisBlock1_1back:
            exec('{} = thisBlock1_1back[paramName]'.format(paramName))

    #random.shuffle (list (Block1_1back))
    all_letters = []
    data_exp = pd.read_excel('1_back_task.xlsx')
    print (data_exp.head())
    #return 0
    all_letters = list (data_exp ['colourtest'])
    print ('letters:', all_letters)
    #return 0
    #for thisBlock1_1back in Block1_1back:
    #   all_letters.append (thisBlock1_1back ['colourtest'])
    iteration = -1
    list_of_stimuli = []

    sound_happy = r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Music\Happy.ogg'
    sound_sad =   r'C:\Users\NU\Desktop\freelance\project2\N-Back\BPM\dixit bpm10\Music\Sad.ogg'

    negative_images = [(i, sound_sad) for i in negative_images]
    positive_images = [(i, sound_happy) for i in positive_images]
    random.shuffle (positive_images)
    list_of_stimuli.extend (negative_images)
    list_of_stimuli.extend (positive_images)

    random.shuffle (list_of_stimuli)
    finishedCalibration = False
    i=0
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
    stim, snd = positive_images [0]
    mySound = sound.Sound(snd)
    mySound.play ()
    for list_of_stimuli in [positive_images]:
        for stim, snd in list_of_stimuli:
            if (mySound.status == FINISHED):
                mySound.play ()
            print ('iteration:', iteration)
            stimulusimage = stim
            showingimage = visual.ImageStim(win, image=stimulusimage)
            showingimage.draw()
            win.flip()
            core.wait(5.0)
            iteration += 1
            frame = input.get_frame()
            process.frame_in = frame
            process.run()
            print ('after run')
            frame = process.frame_out #get the frame to show in GUI
            bpm = process.bpm #get the bpm change over the time
            print ('current value of BPM for iteration ', iteration,' :',bpm)
            hr.append (bpm)
            st.append ('Positive')
    mySound.stop()
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
    rating_list = [rating] * len (hr)
    print('rating', rating)
    print('decisionTime', decisionTime)
    print('choiceHistory',choiceHistory)
    win.flip()
    rating_list = [rating] * len (hr)
    df = DataFrame({'Heart Rate': hr, 'Stimuli Type': st, 'Difficulty Rating':rating_list})
    df.to_excel('negative_heart_rate.xlsx', sheet_name='One', index=False)
    return 0



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
runEmpty()
runRoutineThanks()