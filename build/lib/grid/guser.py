import platform
import os


class GUser():
    """
    """
    def __init__(self):
        """
        """
        self.platform = platform.system()
        self.architecture = platform.architecture()[0]
        self.release = platform.release()
        self.machine = platform.machine()
        self.dirHome = os.path.expanduser("~")
        self.dirGrid = os.path.split(__file__)[0]

    def print_conflict_info(self):
        None

    def printInfo(self):
        print("GRID User's Info")
        print("----------------")
        print("Platform:      ",  self.platform)
        print("Architecture:  ",  self.architecture)
        print("Release:       ",  self.release)
        print("Machine:       ",  self.machine)
        print("Home Dir:      ",  self.dirHome)
        print("GRID Dir:      ",  self.dirGrid)


# print conflict message if Mac users
user = GUser()

if user.platform == "Darwin":
    print("For Mac OS users, please ignore the messages below relating to duplicated implementations. \n\
It's due to the conflict of OpenCV and PyQt5, but it won't affect the performance and the results.\n")
