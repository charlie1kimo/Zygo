import subprocess
import time

ironpython = 'C:/Program Files (x86)/ironPython 2.7/ipy.exe'
wrapper = 'picomotor_cmdLib_ironpython.py'


# find out the deviceKey
s = subprocess.Popen([ironpython, wrapper, '--GetFirstDevice'], stdout=subprocess.PIPE, shell=True)
s.wait()
deviceKey = s.stdout.readline().rstrip()
print "Found device: ", deviceKey

# set zero position
s = subprocess.Popen([ironpython, wrapper, '--SetZeroPosition', deviceKey, '1'], stdout=subprocess.PIPE, shell=True)
s.wait()
# get position (check if it's 0)
s = subprocess.Popen([ironpython, wrapper, '--GetPosition', deviceKey, '1'], stdout=subprocess.PIPE, shell=True)
s.wait()
pos = s.stdout.readline()
print "Position: %s, should be 0" % pos.rstrip()

# move +60
s = subprocess.Popen([ironpython, wrapper, '--RelativeMove', deviceKey, '1', '60'], stdout=subprocess.PIPE, shell=True)
s.wait()
# get position (check if it's 60)
s = subprocess.Popen([ironpython, wrapper, '--GetPosition', deviceKey, '1'], stdout=subprocess.PIPE, shell=True)
s.wait()
pos = s.stdout.readline()
print "Position: %s, should be 60" % pos.rstrip()

# move -30
s = subprocess.Popen([ironpython, wrapper, '--RelativeMove', deviceKey, '1', '--', '-30'], stdout=subprocess.PIPE, shell=True)
s.wait()
# get position (check if it's 30)
s = subprocess.Popen([ironpython, wrapper, '--GetPosition', deviceKey, '1'], stdout=subprocess.PIPE, shell=True)
s.wait()
pos = s.stdout.readline()
print "Position: %s, should be 30" % pos.rstrip()
