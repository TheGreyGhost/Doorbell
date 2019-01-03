import argparse
import errorhandler
import logging
import time
from soundfiles import SoundFiles
from soundfiles import StereoOutputChannel

DEBUG_LOG_PATH = r"/var/tap/doorbelllog.txt"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(epilog="All sound files should be 16 bit 44.1 kHz mono .wav.  Errors written to logfile at {}".format(DEBUG_LOG_PATH))
    parser.add_argument("-d", "--debug", help="print debugging information", action="store_true")
    parser.add_argument("-il", "--indoorleftchannel",
                        help="left channel is used for indoor sound (else right channel used)", action="store_true")
    parser.add_argument("-i", "--indoorsoundfile", help="path to indoor sound effect file", default="indoorsound")
    parser.add_argument("-o", "--outdoorsoundsfolder", help="path to outdoor sound effects folder ", default="outdoorsounds")
    parser.add_argument("-t", "--testsound", help="play this sound continuously, if provided", default="")
#    parser.add_argument("")
    args = parser.parse_args()

    errorhandler.initialise("doorbell", DEBUG_LOG_PATH, logging.DEBUG if args.debug else logging.INFO)

    errorhandler.logdebug("Arguments provided:")
    errorhandler.logdebug(args)

    try:
        sound_files = SoundFiles(args.indoorsoundfile, args.outdoorsoundsfolder,
                                 indoorstereooutputchannel=(StereoOutputChannel.LEFT if args.indoorleftchannel else StereoOutputChannel.RIGHT),
                                 outdoorstereooutputchannel=(StereoOutputChannel.RIGHT if args.indoorleftchannel else StereoOutputChannel.LEFT))
        sound_files.play()

        sleepcount = 10
        while sleepcount > 0 and not sound_files.isFinished():
            sleepcount -= 1
            time.sleep(1)

    except IOError as e:
        errorhandler.logwarn("I/O error occurred ({0}): {1}".format(e.errno, e.strerror))
    except ValueError as e:
        errorhandler.logerror(repr(e))
    except:
        errorhandler.exception("Caught exception in shellinterface")
        raise

"""
    with DBaccess(host=args.host, port=args.port, dbname=args.databasename,
                  username=args.username, dbpassword=args.password) as db:
        ebtables = EbTables(db)
        eblist = ebtables.completeupdate(args.atomiccommitfilename)
"""

"""
    if args.debug:
#        print("wrote temp script to {}".format(DEBUG_LOG_PATH), file=sys.stderr)
#        with open(DEBUG_LOG_PATH, "w+t") as f:
            for singleline in eblist:
                errorhandler.logdebug(singleline)

    for singleline in eblist:
        print(singleline)
"""