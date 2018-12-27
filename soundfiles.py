import pathlib
from pathlib import Path

class SoundFiles:
    indoorfile = None
    outdoorfolder = None
    outdoorfiles = None

    def __init__(self, indoorsoundfile, outdoorsoundsfolder):
        """
        define the location of the the sound files
        :param indoorsoundfile: string giving the path to the sound file used for indoor speakers
        :param outdoorsoundsfolder: string giving the path of the folder which contains sound files for outdoor speakers
        """
        indoorfile = Path(indoorsoundfile)
        outdoorfolder = Path(outdoorsoundsfolder)
        if not indoorfile.is_file():
            raise ValueError("Indoor sound file not found:{}".format(indoorfile))
        if not outdoorfolder.is_dir():
            raise ValueError("Outdoor sounds folder not found:{}".format(outdoorsoundsfolder))

        https: // www.pygame.org / docs / ref / mixer.html  # pygame.mixer.Sound

        https: // nerdparadise.com / programming / pygame / part3
