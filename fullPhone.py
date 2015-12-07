#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import pygame

playing = False

if __name__ == '__main__':
    pygame.init()
    beautifulSunday = pygame.mixer.Sound('Beautiful-Sunday.ogg')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        #Look up hang Switch
        input_state1 = GPIO.input(20)
        input_state2 = GPIO.input(26)
        if input_state1 == False:
            print "Off the hook"
            if playing == False:
                playing = True
                beautifulSunday.play()

        if input_state2 == False:
            print "On the hook"
            if playing == True:
                playing = False
                beautifulSunday.stop()

        time.sleep(1)

