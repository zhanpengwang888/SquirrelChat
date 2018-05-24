import os
import sys
import struct
from Crypto.Cipher import AES


KEY = ""
with open("./server/key.txt", 'r') as file:
    KEY = file.read()


def decrypt_file(key, in_filename, chunksize=16):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    in_filename = in_filename + '.enc'
    out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)
    return out_filename


if len(sys.argv) != 2:
    raise Exception("It needs to have a file to send.")
else:
    # session = requests.Session()
    # session.trust_env = False
    decrypt_file(KEY, sys.argv[1])
    exit(1)

