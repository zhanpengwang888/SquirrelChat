import sys
import requests
import socket
import os
import filecmp
session = requests.Session()
session.trust_env = False
recv = session.get('http://localhost:5000/' + sys.argv[1])
print(recv.text)
open(sys.argv[1], "wb").write(recv.content)
exit(1)
