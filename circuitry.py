from gpiozero import LED, Button
import time

doorbell_button = Button(pin=17, hold_time=0.1)  #Connect one side of the button to a ground pin and the other to the pin
speakers_relay = LED(pin=18)  # output is 0V or 3.3 V

def waitForButtonPress():
    """
    Wait until the doorbell button has been held for at least
    :return:
    """
    while (True):
        doorbell_button.wait_for_press()
        while (doorbell_button.is_pressed()):
            if doorbell_button.is_held():
                return

def isButtonPressed():
    return doorbell_button.is_pressed()

def turnOnSpeakers():
    """
    turns on the speakers and wait for a short time for them to power up
    :return: none
    """
    speakers_relay.on()
    time.sleep(0.5)

def turnOffSpeakers():
    speakers_relay.off()
