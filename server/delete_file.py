import os
import requests
import sys
import socket

if len(sys.argv) != 2:
    raise Exception("It needs to have a file to delete.")
else:
    #session = requests.Session()
    #session.trust_env = False
    path_to_file = sys.argv[1]
    #files = {'file': open(path_to_file, 'rb')}
    print (sys.argv[1])
    r = requests.delete("http://localhost:5000/" + sys.argv[1])
    if (r.ok):
        print("DELETE returned OK result")
    else:
        print("DELETE result not OK")
    exit(1)
