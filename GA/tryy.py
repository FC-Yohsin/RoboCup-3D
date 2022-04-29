import os
from re import A
import time
import subprocess

# running terminal command in python
# stream = os.popen('ls -l')
# output = stream.read()
# print(output)

# os.system('rcssserver3d')
# time.sleep(5)
# print("stopping")
# os.system('^C')

def run_server():
    subproces = subprocess.Popen(['gnome-terminal', '-e', 'rcssserver3d'], stdout=subprocess.PIPE)
    output, error = subproces.communicate()
    time.sleep(2)
    subproces.terminate()
    # print(output)
    return output



def kill_server(output):
    target_process = "python"
    for line in output.splitlines():
        if target_process in str(line):
            pid = int(line.split(None, 1)[0])
            print(pid)
            os.kill(pid, 9)

a = run_server()
print(a)
time.sleep(4)
kill_server(a)
# os.system("gnome-terminal -e 'rcssserver3d'")
# time.sleep(3)
# os.system("gnome-terminal -e '^C'")
# os.system("gnome-terminal -e 'exit'")
