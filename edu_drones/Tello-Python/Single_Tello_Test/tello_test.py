from tello_old import Tello
import sys
from datetime import datetime
import time

# beginning time
start_time = str(datetime.now())

# capture commands from a file
# the file is supplied
file_name = sys.argv[1]

# open the file
f = open(file_name, "r")

# reach eachline where a command is written/supplied
commands = f.readlines()

# instantiate a Tello object
# defined 
tello = Tello()
for command in commands:
    if command != '' and command != '\n':
        command = command.rstrip()
        print(command)
        # checks if 'delay' is in the list of commands
        if command.find('delay') != -1:
            # The partition() method searches for a specified string, and splits the string into a tuple containing three elements.
            # The first element contains the part before the specified string.
            # The second element contains the specified string.
            # The third element contains the part after the string.
            sec = float(command.partition('delay')[2])
            # print the amount of delay
            print('delay %s' % sec)
            # enforce the delay via time.sleep()
            time.sleep(sec)
            pass
        else:
            #if no delay send the command right away
            tello.send_command(command)

# get the log information 
log = tello.get_log()

# open a file to write to the file
# the file is opened to be written in
out = open('log/' + start_time + '.txt', 'w')

# iteration over each line of the log
for stat in log:
    # print statistics of the communication with the drone
    stat.print_stats()

    # store the results of the function in my_str
    my_str = stat.return_stats()

    # write to a file
    out.write(my_str)
