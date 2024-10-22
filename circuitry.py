from gpiozero import LED, Button
import time
import shutdownflag

LED_BLINK_DELAY = 1.0   # blinks on and off at this rate; eg DELAY = 1.0 -> on for 1 s, off for 1 s, etc.
BUTTON_HOLD_TIME = 0.1  # debounce for this length of time (s)
doorbell_button = Button(pin=17, hold_time=BUTTON_HOLD_TIME)  #Connect one side of the button to a ground pin and the other to the pin
speakers_relay = LED(pin=18)  # output is 0V or 3.3 V
status_led = LED(pin=27)

def waitForButtonPress(shutdownflag : ShutdownFlag):
    """
    Wait until the doorbell button has been held for at least BUTTON_HOLD_TIME.
    Blinks the status led while waiting.
    :return:
    """
    global button_has_been_released
    while not shutdownflag.shutdown_triggered:
        status_led.toggle()
        doorbell_button.wait_for_press(timeout=LED_BLINK_DELAY)
        while (doorbell_button.is_pressed):
            if doorbell_button.is_held:
                return

def isButtonPressed():
    return doorbell_button.is_pressed

def turnOnSpeakers():
    """
    turns on the speakers and wait for a short time for them to power up
    :return: none
    """
    speakers_relay.on()
    time.sleep(0.5)

def turnOffSpeakers():
    speakers_relay.off()
