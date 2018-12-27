import argparse
import errorhandler
import logging

DEBUG_LOG_PATH = r"/var/tap/doorbelllog.txt"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(epilog="All sound files should be 16 bit 44.1 kHz mono .wav")
    parser.add_argument("-d", "--debug", help="print debugging information", action="store_true")
    parser.add_argument("-il", "--indoorleftchannel",
                        help="left channel is used for indoor sound (else right channel used)", action="store_true")
    parser.add_argument("-i", "--indoorsound", help="path to indoor sound effect file", default="indoorsound")
    parser.add_argument("-d", "--outdoorsounds", help="path to outdoor sound effects folder ", default="")
    parser.add_argument("-t", "--testsound", help="play this sound continuously, if provided", default="")
    parser.add_argument("")
    args = parser.parse_args()

    errorhandler.initialise("doorbell", DEBUG_LOG_PATH, logging.DEBUG if args.debug else logging.INFO)

    errorhandler.logdebug("Arguments provided:")
    errorhandler.logdebug(args)

    with DBaccess(host=args.host, port=args.port, dbname=args.databasename,
                  username=args.username, dbpassword=args.password) as db:
        ebtables = EbTables(db)
        eblist = ebtables.completeupdate(args.atomiccommitfilename)

"""
    if args.debug:
#        print("wrote temp script to {}".format(DEBUG_LOG_PATH), file=sys.stderr)
#        with open(DEBUG_LOG_PATH, "w+t") as f:
            for singleline in eblist:
                errorhandler.logdebug(singleline)

    for singleline in eblist:
        print(singleline)
"""