from threading import Thread
from parser import *
from messages import *

class Connection(Thread):
    """Connections object represent a single client connected to the server"""
    def __init__(self,conn,state):
        Thread.__init__(self)
        self.parser = Parser()
        self.conn = conn
        self.PACKET_LENGTH = 1024
        self.state = state
        self.user_status = False

    def getUserStatus(self):
        return self.user_status
    
    def changeUserStatus(self):
        self.user_status = not self.user_status

    def run(self):
        print("Initiated connection to a client!!!")
        print("Let's chat!!!")
        while True:
            try:
                data = self.conn.recv(self.PACKET_LENGTH)
                # Do something with the data here..
                if not data:
                    self.conn.close()

                try:
                    command = self.parser.parse_packet(data,self)
                    command.render()
                except KeyboardInterrupt:
                    self.conn.sendall(data)
                    break
                print data
            except:
                pass
