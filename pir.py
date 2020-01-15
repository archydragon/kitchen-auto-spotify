import time
from datetime import datetime
import RPi.GPIO as GPIO
from config import read_config
from control import play, pause

class Motion:
    """
    Class to control motion detection logic. Needed just to avoid of using globals.
    """
    def __init__(self, config):
        self.config = config
        self.flush_state()

    def flush_state(self):
        self.now_playing = False
        self.first_detect = None
        self.last_detect = None

    def motion_detected(self, _pir_pin):
        """
        Callback for detected motion event received from GPIO.
        _pir_pin argument is never used, there is the only data pin used.
        """
        self.last_detect = datetime.now()
        # If not playing now, check if we should start.
        if not self.now_playing:
            # If it was the first detect during some time, just record it.
            if not self.first_detect:
                self.first_detect = datetime.now()

            # If it wasn't the first one, check how long ago was the first one.
            presence_time = (self.last_detect - self.first_detect).total_seconds()
            # 10 seconds is PIR sensor margin of error. If someone was detected in the beginning and in the end
            # of presence delay, it means that there is the same person moving nearby constantly. Start playing.
            if presence_time >= self.config['presence_delay'] and presence_time <= self.config['presence_delay'] + 10:
                print(f"Persistent activity for last {self.config['presence_delay']} seconds detected.")
                self.now_playing = True
                play(self.config)
            elif presence_time > self.config['presence_delay'] + 10:
                flush_state()
                self.first_detect = datetime.now()

    def check_inactivity(self):
        """
        Helper function for timed checks if we should stop playing.
        """
        # Need to be checked only if there were any movements before.
        if self.last_detect:
            self.inactivity_time = (datetime.now() - self.last_detect).total_seconds()
            # If last activity was too long ago, stop playing and flush state.
            if self.inactivity_time > self.config['inactivity_delay'] and self.now_playing:
                print("No one is moving around and listening.")
                self.flush_state()
                pause(self.config)


def pir_detector(config=None):
    """
    Main entrypoint.
    """
    # Read config.
    if not config:
        config = read_config()
    # Create a new Motion object.
    motion = Motion(config)

    # Configure GPIO.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config['pir_pin'], GPIO.IN)

    print("Starting application, press Ctrl+C to interrupt.")
    print(f"Using PIR pin number {config['pir_pin']}.")
    time.sleep(1)
    print('Ready.')

    # Main loop.
    try:
        # We only need to detect rising events from this GPIO pin.
        # This detector runs in background so we need an endless foreground loop
        # to not shutdown immediately.
        GPIO.add_event_detect(config['pir_pin'], GPIO.RISING, callback=motion.motion_detected)
        while True:
            motion.check_inactivity()
            time.sleep(5)

    # Cleanup on Ctrl+C.
    except KeyboardInterrupt:
        print('Terminated.')
        GPIO.cleanup()
