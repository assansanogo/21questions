from datetime import datetime

#
class Stats:
    def __init__(self, command, id):
        '''
        this function is the initialization function
        
        '''
        # store the initial command
        self.command = command
        # initial value of the response is None
        self.response = None
        # store the command id
        self.id = id
        # set a timestamp for the command
        self.start_time = datetime.now()
        # set end time to None
        self.end_time = None
        # # set end time to None
        self.duration = None

    def add_response(self, response):
        self.response = response
        self.end_time = datetime.now()
        self.duration = self.get_duration()
        # prints the identifier of the command
        # prints the  command itself
        # prints the response to the command
        # prints beginning time of the command
        # prints ending time of the command
        self.print_stats()

    def get_duration(self):
        # calculate the delta time between
        # beginning commands & ending commands
        diff = self.end_time - self.start_time
        return diff.total_seconds()

    def got_response(self):
        '''
        this helper function returns a boolean as 
        whether the response has been received or not
        '''
        # if self.response is None
        # it means no answer/response has been received
        if self.response is None:
            return False
        else:
            return True

    def return_stats(self):
        '''
        this function RETURNS to your terminal
        a series of stats
        '''

        # you concatenate the results into a long string
        # Tello EDU
        str = ''
        str +=  '\nid: %s\n' % self.id
        str += 'command: %s\n' % self.command
        str += 'response: %s\n' % self.response
        str += 'start time: %s\n' % self.start_time
        str += 'end_time: %s\n' % self.end_time
        str += 'duration: %s\n' % self.duration

        return str

    def print_stats(self):
        '''
        this function PRINTS to your terminal
        a series of stats
        '''
        # prints lines with relevant information
        # Tello EDU
        print('\nid: %s' % self.id)
        print('command: %s' % self.command)
        print('response: %s' % self.response)
        print('start time: %s' % self.start_time)
        print('end_time: %s' % self.end_time)
        print('duration: %s\n' % self.duration)