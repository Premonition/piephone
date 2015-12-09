#!/usr/bin/python2

import RPi.GPIO as GPIO
import time
import sys
import pyglet
from subprocess import Popen
import glob
import random

class keypad():
    # CONSTANTS
    KEYPAD = [
    ["*",7,1,4],
    [0,8,2,5],
    ["Down","EMPTY","EMPTY","Up"],
    ["#",9,3,6]
    ]
    ROW         = [25,24,23,18]
    COLUMN      = [4,17,27,22]

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def getKey(self):

        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)

        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i

        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0  or rowVal>3:
            self.exit()
            return

        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 3.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j

        # if colVal is not 0 thru 3 then no button was pressed and we can exit
        if colVal <0 or colVal>3:
            self.exit()
            return

        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)


button_press_timeout = 1500

if __name__ == '__main__':
    pyglet.options['audio'] = ('openal')
    kp = keypad()
    
    # GPIO for hangup switch
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Global state
    hangup = True
    playing = False
    number = ''
    lastpress = None

    dialtone_pid = None
    ring_pid = None
    music_pid = None

    ring_start_time = None
    ring_duration = None

    track = None

    # Keypress history
    history = []

    while True:
        # Loop while waiting for a keypress
        hangup = GPIO.input(20)
        if hangup:
            # The phone is on the hook
            history = []
            print 'Phone on hook'
            # Safety
            Popen(['killall', 'mpg123'])
            dialtone_pid = None
            ring_pid = None
            music_pid = None
            number = ''
            lastpress = None
            track = None
            time.sleep(0.01)
            continue

        # Nothing playing? Play the dialtone
        if not dialtone_pid and not ring_pid and not music_pid:
            dialtone_pid = Popen(['mpg123', '--smooth', '--quiet', 'dialtone.mp3'])

        # The dialtone has stopped. Start it again
        if dialtone_pid and dialtone_pid.poll() != None:
            dialtone_pid = Popen(['mpg123', '--smooth', '--quiet', 'dialtone.mp3'])

        digit = kp.getKey()
        if digit != None:
            if isinstance(digit, int): 
                if dialtone_pid:
                    # Restart the dialtone to prevent the annoying cutoff
                    dialtone_pid.kill()
                    dialtone_pid = Popen(['mpg123', '--smooth', '--quiet', 'dialtone.mp3'])
                Popen(['mpg123', '--quiet', str(digit) + 'press.mp3'])

            while (kp.getKey() == digit):
                time.sleep(0.01)

        if digit not in [None, 'Up', 'Down']:
            lastpress = int(round(time.time() * 1000))
            history += [digit]

        if (lastpress and lastpress + button_press_timeout < int(round(time.time() * 1000))):
            number = ''.join([str (h) for h in history])
            history = []
            tracks = glob.glob('tracks/' + number + '_*')
            if tracks:
                if dialtone_pid:
                    dialtone_pid.kill()
                    dialtone_pid = None
                if music_pid:
                    music_pid.kill()
                    music_pid = None
                track = tracks[0]
                ring_pid = Popen(['mpg123', '--smooth', '--quiet', 'ring.mp3'])
                ring_start_time = int(round(time.time() * 1000))
                ring_duration = random.randint(500, 2000)

        if ring_pid and ring_start_time + ring_duration < int(round(time.time() * 1000)):
            ring_pid.kill()
            ring_pid = None
            music_pid = Popen(['mpg123', '--smooth', '--quiet', track])

        # Print the result
        print digit, history, number
        sys.stdout.flush()

        # Loop
        time.sleep(0.01)

#if __name__ == '__main__':
    #pygame.init()
    #beautifulSunday = pygame.mixer.Sound('Beautiful-Sunday.ogg')
