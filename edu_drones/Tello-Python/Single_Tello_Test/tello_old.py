import socket
import threading
import time
from stats import Stats

class Tello:
    def __init__(self):
        # ste the metric system
        self.imperial = False

        # you must register your local ip adress
        self.local_ip = '192.168.10.2'
        
        # the port on which  your network will communicate is: 8899
        self.local_port = 8889
        
        # you build the communication socket from your network
        # define the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        # attach your network to the socket
        self.socket.bind((self.local_ip, self.local_port))

        # thread for receiving cmd ack
        # the thread allows this communication to persist
        # and allow you to perform other action
        # we define a thread which role is to listen to the DRONE
        # each command will go to the drone and if successful
        # will trigger a RESPONSE 
        # as an argument of we must specify the target - which is a function
        self.receive_thread = threading.Thread(target=self._receive_thread)
        # the thread will be active in the background
        self.receive_thread.daemon = True
        # we initiate the thread
        self.receive_thread.start()

        # DRONE IP address
        self.tello_ip = '192.168.10.1'
        # DRONE port
        self.tello_port = 8889

        # the tello_adress is composed of the IP address & the port
        # as a TUPLE example:  ('192.168.10.1',8889)
        self.tello_address = (self.tello_ip, self.tello_port)

        # we define a log as an empty list
        self.log = []

        # the timeout is the time after which the command is deemed
        # lost. Timeout can occur because of the network or too many commands
        # or busy CPU

        self.MAX_TIME_OUT = 15.0

    def send_command(self, command):
        """
        Send a command to the ip address. Will be blocked until
        the last command receives an 'OK'.
        If the command fails (either b/c time out or error),
        will try to resend the command
        :param command: (str) the command to send
        :param ip: (str) the ip of Tello
        :return: The latest command response
        """
        # stats are defined in the file Stats
        self.log.append(Stats(command, len(self.log)))

        # the command given in the argument as a STRING
        # is send VIA the socket communication TO the Tello edu DRONE
        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        # output to the TERMINAL (simple string text)
        print('sending command: %s to %s' % (command, self.tello_ip))

        # starting time
        start = time.time()
        
        # will ONLY run if
        # that the last element of the log has NOT received an answer
        # now stores the current time
        # if the time has exceeded the MAX_TIME_OUT constant
        # the command that was sent has timed out.

        while not self.log[-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.MAX_TIME_OUT:
                print('Max timeout exceeded... command %s' % command)
                # TODO: is timeout considered failure or next command still get executed
                # in this section you must code the behaviour when
                # a command times out.
                
                
                # now, next one got executed
                return
        print('Done!!! sent command: %s to %s' % (command, self.tello_ip))

    def set_abort_flag(self):
        """
        Sets self.abort_flag to True.

        Used by the timer in Tello.send_command() to indicate to that a response
        
        timeout has occurred.

        """

        self.abort_flag = True

    def takeoff(self):
        """
        Initiates take-off.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('takeoff')

    def set_speed(self, speed):
        """
        Sets speed.

        This method expects KPH or MPH. The Tello API expects speeds from
        1 to 100 centimeters/second.

        Metric: .1 to 3.6 KPH
        Imperial: .1 to 2.2 MPH

        Args:
            speed (int|float): Speed.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        speed = float(speed)
        
        # imperial system
        if self.imperial is True:
            speed = int(round(speed * 44.704))
        # metrric system
        else:
            speed = int(round(speed * 27.7778))

        return self.send_command('speed %s' % speed)

    def rotate_cw(self, degrees):
        """
        Rotates clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('cw %s' % degrees)

    def rotate_ccw(self, degrees):
        """
        Rotates counter-clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.send_command('ccw %s' % degrees)

    def flip(self, direction):
        """
        Flips.

        Args:
            direction (str): Direction to flip, 'l', 'r', 'f', 'b'.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('flip %s' % direction)

    def get_response(self):
        """
        Returns response of tello.

        Returns:
            int: response of tello.

        """
        response = self.response
        return response

    def get_height(self):
        """Returns height(dm) of tello.

        Returns:
            int: Height(dm) of tello.

        """
        height = self.send_command('height?')
        # converts the response to a string
        height = str(height)
        # filters the height (the height should be numeric)
        height = filter(str.isdigit, height)
        try:
            # converts the height as integer
            height = int(height)
            # store last position
            self.last_height = height
        except:
            # in case of exception, the height is set to the previous height
            height = self.last_height
            pass
        return height

    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            int: Percent battery life remaining.

        """
        
        battery = self.send_command('battery?')

        try:
            battery = int(battery)
        except:
            pass

        return battery

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight.

        Returns:
            int: Seconds elapsed during flight.

        """

        flight_time = self.send_command('time?')

        try:
            flight_time = int(flight_time)
        except:
            pass

        return flight_time

    def get_speed(self):
        """Returns the current speed.

        Returns:
            int: Current speed in KPH or MPH.

        """

        speed = self.send_command('speed?')

        try:
            speed = float(speed)

            if self.imperial is True:
                speed = round((speed / 44.704), 1)
            else:
                speed = round((speed / 27.7778), 1)
        except:
            pass

        return speed

    def land(self):
        """Initiates landing.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('land')

    def move(self, direction, distance):
        """Moves in a direction for a distance.

        This method expects meters or feet. The Tello API expects distances
        from 20 to 500 centimeters.

        Metric: .02 to 5 meters
        Imperial: .7 to 16.4 feet

        Args:
            direction (str): Direction to move, 'forward', 'back', 'right' or 'left'.
            distance (int|float): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        distance = float(distance)

        if self.imperial is True:
            distance = int(round(distance * 30.48))
        else:
            distance = int(round(distance * 100))

        return self.send_command('%s %s' % (direction, distance))

    def move_backward(self, distance):
        """Moves backward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('back', distance)

    def move_down(self, distance):
        """Moves down for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('down', distance)

    def move_forward(self, distance):
        """Moves forward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('forward', distance)

    def move_left(self, distance):
        """Moves left for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('left', distance)

    def move_right(self, distance):
        """Moves right for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        """
        return self.move('right', distance)

    def move_up(self, distance):
        """Moves up for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('up', distance)

    def _receive_thread(self):
        """
        Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """

        # the fonction is runned as a thread (identified with a leading underscore __)
        # infinite loop that is receiving information from the Trello
        # through the command : socket.recvfrom(1024)

        #infinite loop
        while True:
            # try clause
            try:
                # receive data from the Drone as a tuple (response and IP)
                self.response, ip = self.socket.recvfrom(1024)
                
                # display the response and origin of the response (IP) 
                print('from %s: %s' % (ip, self.response))
                
                # add to the last log Stat element 
                # the response received from Tello
                self.log[-1].add_response(self.response)
            
            # execept clause (print exception)
            except socket.error as  exc:
                print("Caught exception socket.error : %s" % exc)

    def on_close(self):
        '''
        function which instructs drones to land given an IP list
        '''
        # loop over an ip list of tello drones
        # send information/instruction to land

        for ip in self.tello_ip_list:
             self.socket.sendto('land'.encode('utf-8'), (ip, 8889))
        self.socket.close()

    def get_log(self):
        '''
        function which returns the log of all instructions so far
        '''
        # returns the stored log 
        return self.log


if __name__ =='__main__':
    tello = Tello()

    tello.send_command('command')
    #tello.rotate_ccw(90)
    #tello.move_up(1)
    #tello.move_forward(1)
    #tello.rotate_ccw(180)
    #tello.move_forward(1)
    #tello.land()
    tello.get_battery()
