import socket
import threading
import time
import numpy as np
import libh264decoder

class Tello:
    """Wrapper class to interact with the Tello drone."""

    def __init__(self, local_ip, local_port, imperial=False, command_timeout=.3, tello_ip='192.168.10.1',
                 tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip (str): Local IP address to bind.
        :param local_port (int): Local port to bind.
        :param imperial (bool): If True, speed is MPH and distance is feet.
                             If False, speed is KPH and distance is meters.
        :param command_timeout (int|float): Number of seconds to wait for a response to a command.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """
        # flag to signified the action has been cancelled
        # initialized to zero
        self.abort_flag = False

        # video flux decoder
        self.decoder = libh264decoder.H264Decoder()

        # timeout: time after which the command is cancelled
        self.command_timeout = command_timeout
        
        # unit system
        self.imperial = imperial
        
        # response
        # initialized to None (no answer)
        self.response = None  

        self.frame = None  # numpy array Blue Green Red -- current camera output frame
        self.is_freeze = False  # freeze current camera output
        self.last_frame = None # last frame is None when initialized
        
        # 2 different sockets (command data + video data)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        
        # Tello address composed of IP & port
        self.tello_address = (tello_ip, tello_port)
        self.local_video_port = 11111  # port for receiving video stream
        self.last_height = 0
        
        ## The 2 main flux of data :
        # video and cmd thread -  must be ALWAYS on
        # they must operate in the back ground
        # so they are daemons

        # THREAD 1
        # thread for receiving cmd ack
        # bind the local IP and video port
        self.socket.bind((local_ip, local_port))
        self.receive_thread = threading.Thread(target=self._receive_thread)
        # set the daemon
        self.receive_thread.daemon = True

        self.receive_thread.start()

        # THREAD 2
        # thread for receiving video
        # bind the local IP and video port
        self.socket_video.bind((local_ip, self.local_video_port))
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        # set the daemon
        self.receive_video_thread.daemon = True

        self.receive_video_thread.start()


        # to initiate the
        # receiveal of video data 
        # -- send cmd: command, streamon to the command socket
        self.socket.sendto(b'command', self.tello_address)
        print ('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print ('sent: streamon')

    def __del__(self):
        """Closes the local socketS."""
        # close the command socket
        self.socket.close()
        # close the video socket
        self.socket_video.close()
    
    def read(self):
        """Return the last frame from camera."""
        # self.freeze is a parameter that freezes/pause
        # the camera
        # if the stream is paused return the last frame
        if self.is_freeze:
            return self.last_frame
        # else return the current frame
        else:
            return self.frame

    def video_freeze(self, is_freeze=True):
        """Pause video output -- set is_freeze to True"""
        # self.freeze is a parameter that freezes/pause
        # the camera. if set to True
        # the last frame is  set to the current frame
        self.is_freeze = is_freeze
        if is_freeze:
            self.last_frame = self.frame

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                # receive data from the Tello
                # the responses are command responses
                # (self.socket)
                self.response, ip = self.socket.recvfrom(3000)
                # print(self.response)
            except socket.error as exc:
                print ("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        """
        Listens for video streaming (raw h264) from the Tello.

        Runs as a thread, sets self.frame to the most recent frame Tello captured.

        """
        packet_data = ""
        while True:
            try:
                # receive video data from the Tello
                # data (i.e packet_data) is going to be as a string
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                # we can only decode when there is enough data to decode
                # i.e not reach the end of frame

                if len(res_string) != 1460:
                    # the packet data is going to be decoded in 
                    # some raw h264 data
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = ""

            except socket.error as exc:
                print ("Caught exception socket.error : %s" % exc)
    
    def _h264_decode(self, packet_data):
        """
        decode raw h264 format data from Tello
        
        :param packet_data: raw h264 data array
       
        :return: a list of decoded frame
        """
        res_frame_list = []
        # defined in intialisation
        frames = self.decoder.decode(packet_data)
        # iterate of decoded raw h264 frames
        # this function returns:
        #the number of frames, the width,height  the linesize 

        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)
                # convert from bytes to an array
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                # reshape the image to height, width, channel
                frame = (frame.reshape((h, ls / 3, 3)))
                # keep the information from:
                # h x w x channels
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def send_command(self, command):
        """
        Send a command to the Tello and wait for a response.

        :param command: Command to send.
        :return (str): Response from Tello.

        """

        print (">> send cmd: {}".format(command))
        self.abort_flag = False
        # define a timer which works with threads
        # if time out is more than self.command_timeout
        # defined @ initialisation then the command is aborted
        # by setting the flag to True via the function
        # self.set_abort_flag

        timer = threading.Timer(self.command_timeout, self.set_abort_flag)

        # send command to the socket
        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        
        # the timer runs if the abort_flag is not set to True
        # each command will run until receiving an answer or timeout
        timer.start()
        while self.response is None:
            if self.abort_flag is True:
                break
        timer.cancel()
        
        # the socket is opened
        # the response can eithe be : 
        # none or anything in response to the commands
        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')

        self.response = None

        return response
    
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
