import os
import sys
import random
import struct
from Crypto.Cipher import AES


KEY = ""
with open("./server/key.txt", 'r') as file:
    KEY = file.read()


def encrypt_file(key, in_filename, chunksize=16):
    out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 255)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))

    return out_filename


if len(sys.argv) != 2:
    raise Exception("It needs to have a file to send.")
else:
    # session = requests.Session()
    # session.trust_env = False
    encrypt_file(KEY, sys.argv[1])
    exit(1)

