import RPi.GPIO as GPIO
import time



if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        #Look up hang Switch
        input_state1 = GPIO.input(20)
        input_state2 = GPIO.input(26)
        if input_state1 == False:
            print "Off the hook"
        if input_state2 == False:
            print "On the hook"

        time.sleep(1)

