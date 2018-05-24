"""
This test suite tests that a user creates a chat room, become its admin, set the topic, get the topic, and leave the chat room.
Then the same user tries to set and get topic but should fail because s/he is not in the chat room. It should
print a proper error message indicating that s/he is not in the chat room. Then s/he joins the chat room and
should be still the admin of the chat room. S/he can set and get topic without receiving error messages.
"""

import os
import socket
import atexit
import signal
import subprocess
from time import sleep
from parser import *
from subprocess import Popen

address = "localhost"
port = 4000
SIZE = 1024
pid = None

def rest():
    sleep(.2)

def start_server():
    with open("outfile", "w") as outfile:
        with open("errfile","w") as errfile:
            pid = subprocess.Popen("python server.py passwords.csv".split(),stderr=errfile,stdout=outfile)
            return pid

def copy_pwds(): 
    os.system("cp passwords.csv thepasswords.csv")

def cleanup():
    pid.kill()
    os.system("rm thepasswords.csv 2>err")
    os.system("rm out err 2>err")

def leave_channel(socket, channel_name):
    socket.send("leave {}".format(channel_name))
    rest()

def register(socket,uname,password):
    socket.send("register {} {}".format(uname,password))
    rest()

def join_message(socket,channel_name):
    socket.send("join {}".format(channel_name))
    get = socket.recv(SIZE)
    rest()
    return get

def set_topic(socket,channel_name,content):
    socket.send("settopic {} {}".format(channel_name,content))
    get = socket.recv(SIZE)
    rest()
    return get

def get_topic(socket,channel_name):
    socket.send("gettopic {}".format(channel_name))
    get = socket.recv(SIZE)
    rest()
    return get


p = Parser()

def expect(s,m1):
    d = s.recv(SIZE)
    m2 = p.parse_packet(d)
    assert m1 == m2

copy_pwds()
pid = start_server()
atexit.register(cleanup)
rest()
sock = socket.socket()
sock.connect((address, port))
if sock == None:
    raise "Could not connect to server!"
register(sock,"myTest","my_test")
print(join_message(sock,"#fool"))
print(set_topic(sock,"#fool","Let's set topic!"))
print(get_topic(sock,"#fool"))
result = "topic #fool Let's set topic!\n"
assert result == get_topic(sock,"#fool")
leave_channel(sock, "#fool")
print(set_topic(sock,"#fool","You shouldn't set topic since you leave the chat room #fool!"))
assert "error You are not in this chat room #fool.\n" == set_topic(sock,"#fool","You shouldn't set topic since you leave the chat room #fool!")
print(get_topic(sock,"#fool"))
assert "error You are not in this chat room #fool.\n" == get_topic(sock,"#fool")
print(join_message(sock,"#fool"))
print(set_topic(sock,"#fool","Let's set topic2!"))
print(get_topic(sock,"#fool"))
result1 = "topic #fool Let's set topic2!\n"
assert result1 == get_topic(sock,"#fool")
leave_channel(sock, "#fool")
print("You pass the test!")