import argparse
import errorhandler
import logging
import time
import circuitry
from shutdownflag import ShutdownFlag

from soundfiles import SoundFiles
from soundfiles import StereoOutputChannel
from soundfiles import SelectionMethod

DEBUG_LOG_PATH = r"/home/doorbell/doorbell.log"
DEFAULT_TEST_SOUND = r"/home/doorbell/doorbell/data/testsound.wav"

def playTestSoundUntilButtonPressed(shutdownTriggered : ShutdownFlag, testsoundpath):
    errorhandler.loginfo("Playing test sound: {}".format(testsoundpath))
    circuitry.turnOnSpeakers()
    circuitry.status_led.on()
    while not shutdownTriggered.shutdown_triggered:
        sound_files = SoundFiles(testsoundpath, None, StereoOutputChannel.BOTH, StereoOutputChannel.NONE)
        sound_files.play()
        while not sound_files.isFinished() and not shutdownTriggered.shutdown_triggered:
            time.sleep(1)
        if circuitry.isButtonPressed():
            circuitry.turnOffSpeakers()
            errorhandler.loginfo("Stopped test sound.")
            return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        epilog="All sound files should be 16 bit 44.1 kHz mono .wav."\
               " Hold button down during startup to start playing the test sound, press button again to stop."\
               " Errors written to logfile at {}".format(DEBUG_LOG_PATH))
    parser.add_argument("-d", "--debug", help="print debugging information", action="store_true")
    parser.add_argument("-il", "--indoorleftchannel",
                        help="left channel is used for indoor sound (else right channel used)", action="store_true")
    parser.add_argument("-i", "--indoorsoundfile", help="path to indoor sound effect file", default="indoorsound")
    parser.add_argument("-o", "--outdoorsoundsfolder", help="path to outdoor sound effects folder ", default="outdoorsounds")
    parser.add_argument("-t", "--testsound", help="play this sound continuously, if provided", default="")
    args = parser.parse_args()

    errorhandler.initialise("doorbell", DEBUG_LOG_PATH, logging.DEBUG if args.debug else logging.INFO)

    errorhandler.logdebug("Arguments provided:")
    errorhandler.logdebug(args)

    try:
        shutdownTriggered = ShutdownFlag()
        if circuitry.isButtonPressed():
            if len(args.testsound) == 0:
                args.testsound = DEFAULT_TEST_SOUND

        if len(args.testsound) > 0:
            playTestSoundUntilButtonPressed(shutdownTriggered, args.testsound)

        sound_files = SoundFiles(args.indoorsoundfile, args.outdoorsoundsfolder,
                                 indoorstereooutputchannel=(StereoOutputChannel.LEFT if args.indoorleftchannel else StereoOutputChannel.RIGHT),
                                 outdoorstereooutputchannel=(StereoOutputChannel.RIGHT if args.indoorleftchannel else StereoOutputChannel.LEFT))
        while not shutdownTriggered.shutdown_triggered:
            circuitry.waitForButtonPress(shutdownTriggered)
            if not shutdownTriggered.shutdown_triggered:
                circuitry.turnOnSpeakers()
                sound_files.play()
                errorhandler.logdebug("Waiting for sound to finish")
                sleepcount = 60
                while sleepcount > 0 and not sound_files.isFinished() and not shutdownTriggered.shutdown_triggered:
                    sleepcount -= 1
                    time.sleep(1)
                errorhandler.logdebug("Stopped waiting, finished:{}".format(sound_files.isFinished()))
                sound_files.selectNextOutdoor(SelectionMethod.SEQUENTIAL)
                circuitry.turnOffSpeakers()
        if shutdownTriggered.shutdown_triggered:
            errorhandler.loginfo('SIGTERM received...')    
    except IOError as e:
        errorhandler.logwarn("I/O error occurred ({0}): {1}".format(e.errno, e.strerror))
    except ValueError as e:
        errorhandler.logerror(repr(e))
    except:
        errorhandler.exception("Caught exception in main")
        raise
