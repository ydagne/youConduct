#!/usr/bin/env python
# encoding: utf-8


#	 ColorSounds
#
#  Copyright 2015 Yihenew Beyene
#  
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



import time
import numpy as np
import cv2
import fluidsynth

class colorSound():

     def __init__(self):
     
         self.running = False
         
         # create video capture device
         self.cap = cv2.VideoCapture(0)
         if(not self.cap.isOpened()):
            raise IOError, "Could not find video capture device"
            
         
         # Fluidsynth
         self.gain       = 0.4
         self.samplerate = 44100
         self.fs         = fluidsynth.Synth(self.gain, self.samplerate)
         self.fs.start('pulseaudio')
         #self.sfid   = fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
         self.sfid    = self.fs.sfload("soundFont1.sf2")

         # There are 3 presets in 'soundFont1.sf2'
         # The original soundfont that comes with fluidsynth is located in
         # "/usr/share/sounds/sf2/FluidR3_GM.sf2". This has more presets.
         # If you want to use FluidR3_GM.sf2, make sure that you select
         # the appropriate program number and banks
         
         # The following are taken from 'soundFont1.sf2'
         self.progs   = [0, 40, 52]  # Yamaha Grand Piano, Voilin, Ahh Choir
         self.banks   = [0,  0,  0]
         
         
         self.speed   = 100
         self.chan1keyPast = 1
         self.chan2keyPast = 1
         self.chan3keyPast = 1
         self.stime2 = time.time()
         self.stime3 = time.time()
         self.chan2Active = False
         self.chan3Active = False
       
         # Assign one preset per channel
         for chan in range(1,4):
            #self.fs.program_change(chan, progs[k])
            self.fs.program_select(chan, 
                                   self.sfid,
                                   self.banks[chan-1],
                                   self.progs[chan-1])

     def start(self):
            
             self.running = True
            
             # define range of blue color in HSV
             lower_blue = np.array([100,50,50])
             upper_blue = np.array([130,255,255])
           
             # define range of green color in HSV
             lower_green = np.array([40, 50, 50])
             upper_green = np.array([75, 255, 255]) 
  
             # define range of red color in HSV
             lower_red1 = np.array([0, 180, 100])
             upper_red1 = np.array([5, 255, 255]) 
             
             lower_red2 = np.array([175, 200, 100])
             upper_red2 = np.array([179, 255, 255]) 
             
             halfNotes = [37,39,42,44,46,49,51,54,56,58,61,63,66,
                          68,70,73,75,78,80,82,85,87,90,92,94]
             fullNotes = []
             
             for n in range(36,97):
                if n not in halfNotes:
                   fullNotes.append(n)
                   
             nUpperKeys = len(halfNotes)
             nLowerKeys = len(fullNotes)
                
             
             cv2.namedWindow('RGB Color tracker')
             
             sleepTime = 0.1       # Key reading time interval (seconds)
             loopTimeout = 3       # Timeout for Viloin and Choir loops

             while self.running:

                     # Take snapshot
                     _,frame =  self.cap.read()
                     #frame   = cv2.flip(frame,1)
                     
                     # Get image size
                     H = len(frame)
                     W = len(frame[0])

                     # Filter the image
                     #frame = cv2.blur(frame,(3,3))
                     frame = cv2.GaussianBlur(frame,(5,5),0)

                     # convert to hsv and find range of colors
                     hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

                     # threshold the image for each color and find contours
                     
                     # Threshold for green color
                     thresh          = cv2.inRange(hsv,lower_green, upper_green)
                     contoursGreen,_ = cv2.findContours(thresh,cv2.RETR_LIST,
                                                        cv2.CHAIN_APPROX_SIMPLE)
                                                
                     # Threshold for blue color        
                     thresh          = cv2.inRange(hsv,lower_blue, upper_blue)
                     contoursBlue,_  = cv2.findContours(thresh,cv2.RETR_LIST,
                                                        cv2.CHAIN_APPROX_SIMPLE)
                                         
                     # Threshold for red color               
                     thresh          = cv2.inRange(hsv,lower_red1, upper_red1)
                     thresh         += cv2.inRange(hsv,lower_red2, upper_red2)
                     contoursRed,_   = cv2.findContours(thresh,cv2.RETR_LIST,
                                                        cv2.CHAIN_APPROX_SIMPLE)

                     # Get a contour with the largest area
                     greanDetected = False
                     blueDetected  = False
                     redDetected   = False
                     
                     # Minimum contour area for detection
                     maxGarea = 10
                     maxBarea = 10
                     maxRarea = 10
                     
                     for c in contoursGreen:
                         if cv2.contourArea(c) > maxGarea:
                             mmaxGarea     = cv2.contourArea(c)
                             gContour      = c
                             greanDetected = True
                             
                     for c in contoursBlue:
                         if cv2.contourArea(c) > maxBarea:
                             maxBarea     = cv2.contourArea(c)
                             bContour     = c
                             blueDetected = True
                             
                     for c in contoursRed:
                         if cv2.contourArea(c) > maxRarea:
                             maxRarea    = cv2.contourArea(c)
                             rContour    = c
                             redDetected = True
                 
                     if greanDetected:    
                         M       = cv2.moments(gContour)
                         gcx,gcy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                         cv2.circle(frame,(gcx,gcy),10,(0,255,0),-1)
                         
                         if(gcy < 0.5 * H):
                             gKey = halfNotes[gcx * nUpperKeys / W]
                         else:
                             gKey = fullNotes[gcx * nLowerKeys / W]
                         
                         
                     if blueDetected:  
                         M       = cv2.moments(bContour)
                         bcx,bcy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                         cv2.circle(frame,(bcx,bcy),10,(255,0,0),-1)
                         
                         if(bcy < 0.5 * H):
                             bKey = halfNotes[bcx * nUpperKeys / W]
                         else:
                             bKey = fullNotes[bcx * nLowerKeys / W]
                         
                     if redDetected:    
                         M       = cv2.moments(rContour)
                         rcx,rcy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                         cv2.circle(frame,(rcx,rcy),10,(0,0,255),-1)
                         
                         if(rcy < 0.5 * H):
                             rKey = halfNotes[rcx * nUpperKeys / W]
                         else:
                             rKey = fullNotes[rcx * nLowerKeys / W]
                         
                         
                     cv2.imshow('RGB Color tracker',frame)
                     cv2.waitKey(1)
                     
                     
                     # Playing the music
                     newTime = time.time()
                     
                     # Yamaha Grand Piano
                     if greanDetected and (self.chan1keyPast != gKey):
                        self.fs.noteon(1, gKey, self.speed)
                        self.chan1keyPast = gKey
                        
                     # Violin
                     if blueDetected:
                        if self.chan2keyPast != bKey:
                           self.fs.noteoff(2, self.chan2keyPast)
                           self.fs.noteon(2, bKey, self.speed)
                           self.chan2keyPast = bKey
                        self.chan2Active  = True
                        self.stime2       = newTime
                     
                     # Ahh Choir
                     if redDetected:
                        self.fs.noteoff(3, self.chan3keyPast)
                        self.fs.noteon(3, rKey, self.speed)
                        self.chan3Active  = True
                        self.chan3keyPast = rKey
                        self.stime3       = newTime
                        
                     # Stop violin loop if timeout reached   
                     if self.chan2Active:
                         if ((newTime - self.stime2) > loopTimeout):
                              self.fs.noteoff(2, self.chan2keyPast)
                              self.chan2Active = False
                        
                     # Stop choir loop if timeout reached
                     if self.chan3Active:
                         if ((newTime - self.stime3) > loopTimeout):
                              self.fs.noteoff(3, self.chan3keyPast)
                              self.chan3Active = False

                     time.sleep(sleepTime)
                          
     def stop(self):
            self.running = False
            self.cap.release()

            
   
if __name__ == '__main__':
    try:
        cSound = colorSound()
        cSound.start()
        
    except KeyboardInterrupt:
        cSound.stop()
        # Clean up everything before leaving
        cv2.destroyAllWindows()
        pass 

