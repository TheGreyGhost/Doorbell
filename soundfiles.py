import pygame
import random
import errorhandler
import shelve
import os
from enum import Enum
from pathlib import Path

SelectionMethod = Enum("SelectionMethod", "RANDOM SEQUENTIAL")

PERSISTENT_INDEX_SHELF = r"/home/pi/doorbellsavedstate.ini"

class StereoOutputChannel(Enum):
    LEFT =  (1.0, 0.0)
    RIGHT = (0.0, 1.0)
    BOTH =  (1.0, 1.0)
    NONE = (0.0, 0.0)

    def __init__(self, left_channel_volume, right_channel_volume):
        self.left_channel_volume = left_channel_volume
        self.right_channel_volume = right_channel_volume

    @property
    def leftChannelVolume(self):
        return self.left_channel_volume

    @property
    def rightChannelVolume(self):
        return self.right_channel_volume


"""
  SoundFiles is used to select and play the doorbell sounds
    Indoor for the indoor sound (on one of the two stereo channels)
    Outdoor for the outdoor sounds (on the other stereo channel)

    Information needed:
      - Path to the indoor file (mono 16 bit wav)
      - Path to the folder containing the outdoor files
      - which stereo channels the indoor and outdoor sounds play on

Usage:
  (1) Create SoundFiles with the information above
  (2) Optionally: selectNextOutdoor() to choose the next outdoor sound: either randomly, or sequentially
  (3) play() to play both the indoor and outdoor sounds at the same time
  (4) optionally: wait for isFinished to become true
  (5) Repeat from (2) above as desired
  
"""

class SoundFiles:
    indoor_file = None              # Path to the indoor sound file (*.wav)
    outdoor_folder = None           # Path to the folder containing the outdoor sound files (*.wav)
    outdoor_files = None            # collection of Paths, one for each outdoor sound file (*.wav)
    outdoor_file = None             # Path to the next outdoor sound file to be played(*.wav)
    next_outdoor_sound_index = 0    # for sequential playing: the index of the sound that will be selected next
    outdoor_unused = False          # if true; the outdoor sound is unused

    indoor_sound = None             # Sound object for the indoor sound
    outdoor_sound = None            # Sound object for the outdoor sound to be played

    INDOOR_CHANNEL_ID = 0           # mixer channel ID reserved for indoor sound
    OUTDOOR_CHANNEL_ID = 1          # mixer channel ID reserved for outdoor sound
    indoor_channel = None           # mixer channel for indoor sounds
    outdoor_channel = None          # mixer channel for outdoor sounds

    indoor_stereo_output_channel = StereoOutputChannel.LEFT    # which speaker(s) is the indoor sound played on?
    outdoor_stereo_output_channel = StereoOutputChannel.RIGHT   # which speaker(s) is the outdoor sound played on?

    def __init__(self, indoorsoundfile, outdoorsoundsfolder, indoorstereooutputchannel, outdoorstereooutputchannel):
        """
        define the location of the the sound files
        :param indoorsoundfile: string giving the path to the sound file used for indoor speakers
        :param outdoorsoundsfolder: string giving the path of the folder which contains sound files for outdoor speakers
                                    if None, ignore
        """

        os.system("amixer sset PCM -- -20dB")
        self.indoor_file = Path(indoorsoundfile)
        self.outdoor_unused = (outdoorsoundsfolder is None)

        if not self.outdoor_unused:
            self.outdoor_folder = Path(outdoorsoundsfolder)
        errorhandler.logdebug("SoundFiles::__init__")
        errorhandler.loginfo("indoor_file: {}".format(self.indoor_file))
        errorhandler.loginfo("outdoor_folder: {}".format(self.outdoor_folder))

        if not self.indoor_file.is_file():
            raise ValueError("Indoor sound file not found or is not a file:{}".format(indoorsoundfile))
        if not self.outdoor_unused:
            if not self.outdoor_folder.is_dir():
                raise ValueError("Outdoor sounds folder not found or is not a folder:{}".format(outdoorsoundsfolder))

        self.indoor_stereo_output_channel = indoorstereooutputchannel
        self.outdoor_stereo_output_channel = outdoorstereooutputchannel

        self.initialiseMixer()
        self.refreshIndoor()
        self.refreshOutdoor()

#        https: // www.pygame.org / docs / ref / mixer.html  # pygame.mixer.Sound
#        https: // nerdparadise.com / programming / pygame / part3

    def initialiseMixer(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=65536)
        pygame.mixer.set_num_channels(2)
        pygame.mixer.set_reserved(2)
        errorhandler.logdebug("SoundFiles::initialiseMixer")

    def refreshIndoor(self):
        errorhandler.logdebug("SoundFiles::refreshIndoor")
        self.indoor_channel = pygame.mixer.Channel(self.INDOOR_CHANNEL_ID)
        self.indoor_sound = pygame.mixer.Sound(str(self.indoor_file))

    def refreshOutdoor(self):
        errorhandler.logdebug("SoundFiles::refreshOutdoor")
        if self.outdoor_unused:
            return
        self.outdoor_channel = pygame.mixer.Channel(self.OUTDOOR_CHANNEL_ID)
        self.outdoor_files = list(self.outdoor_folder.glob("*.wav"))
        errorhandler.loginfo("outdoor files found:{}".format(self.outdoor_files))
        self.selectNextOutdoor(SelectionMethod.SEQUENTIAL)

    def selectNextOutdoor(self, selection_method):
        errorhandler.logdebug("SoundFiles::selectNextOutdoor")
        if self.outdoor_unused:
            return
        errorhandler.logdebug("selection_method:{}".format(selection_method))
        if selection_method == SelectionMethod.RANDOM:
            self.outdoor_file = random.choice(self.outdoor_files)
        elif selection_method == SelectionMethod.SEQUENTIAL:
            with shelve.open(PERSISTENT_INDEX_SHELF) as db:
                if "idx" in db:
                    self.next_outdoor_sound_index = db["idx"]
                    errorhandler.logdebug("retrieved {} from {}".format(db["idx"], PERSISTENT_INDEX_SHELF))
                else:
                    self.next_outdoor_sound_index = 0
                    errorhandler.logdebug("initialised idx to 0")
                if self.next_outdoor_sound_index < 0 or self.next_outdoor_sound_index >= len(self.outdoor_files):
                    self.next_outdoor_sound_index = 0
                self.outdoor_file = self.outdoor_files[self.next_outdoor_sound_index]
                self.next_outdoor_sound_index += 1
                if self.next_outdoor_sound_index >= len(self.outdoor_files):
                    self.next_outdoor_sound_index = 0
                db["idx"] = self.next_outdoor_sound_index
                errorhandler.logdebug("stored {} in {}".format(db["idx"], PERSISTENT_INDEX_SHELF))

        errorhandler.loginfo("outdoor files selected:{}".format(self.outdoor_file))
        self.outdoor_sound = pygame.mixer.Sound(str(self.outdoor_file))


    def playIndoor(self):
        self.indoor_channel.play(self.indoor_sound, loops=0, maxtime=0, fade_ms=0)
        self.indoor_channel.set_volume(self.indoor_stereo_output_channel.leftChannelVolume,
                                       self.indoor_stereo_output_channel.rightChannelVolume)
        errorhandler.logdebug("SoundFiles::playIndoor")

    def playOutdoor(self):
        if self.outdoor_unused:
            return
        self.outdoor_channel.play(self.outdoor_sound, loops=0, maxtime=0, fade_ms=0)
        self.outdoor_channel.set_volume(self.outdoor_stereo_output_channel.leftChannelVolume,
                                        self.outdoor_stereo_output_channel.rightChannelVolume)
        errorhandler.logdebug("SoundFiles::playOutdoor")

    def play(self):
        self.playIndoor()
        self.playOutdoor()

    def isFinished(self):
        return (not self.indoor_channel.get_busy()) and (self.outdoor_unused or not self.outdoor_channel.get_busy())



