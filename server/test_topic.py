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
register(sock,"kristest","kristestpwd")
print(join_message(sock,"#foo"))
print(set_topic(sock,"#foo","here is the example topic"))
print(get_topic(sock,"#foo"))
result = "topic #foo here is the example topic\n"
assert result == get_topic(sock,"#foo")
print("You pass the test!")