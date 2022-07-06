import subprocess
import os

class AutomationScript:
    
    @staticmethod
    def startServer():
        subproces = subprocess.Popen(['gnome-terminal', '-e', 'rcssserver3d'], stdout=subprocess.PIPE)

    @staticmethod
    def killServer():
        os.system("killall -9 rcssserver3d")