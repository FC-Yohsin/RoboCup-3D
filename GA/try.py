import os

# running terminal command in python
stream = os.popen('ls -l')
output = stream.read()
print(output)