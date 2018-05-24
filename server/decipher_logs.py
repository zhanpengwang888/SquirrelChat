import os
import sys
from cryptography.fernet import Fernet

def decipher(channel_name, theKey):
    if len(os.listdir("./logs")) != 0:
        for filename in os.listdir("./logs"):
            filename_string_list = filename.split('-')
            channel_name_extracted = filename_string_list[1]
            if channel_name == channel_name_extracted:
                cipher = Fernet(theKey)
                encrypted_text = ""
                with open(os.path.join('./logs',filename), 'r') as log:
                    encrypted_text = log.read()
                if encrypted_text != "":
                    try:
                        decrypted_text = cipher.decrypt(encrypted_text)
                        with open(os.path.join('./logs',filename), 'w') as output:
                            output.write(decrypted_text)
                        print("Finish decrypting " + filename + "!")
                    except:
                        print("Error: Invalid Token to be decrypted." + filename +" is corrupted or incorrect symmetric key or it has been decrypted already.")
            else:
                print("There is no log for the channel " + channel_name + ".")
        print("Finish log decryption.")
    else:
        print("There is no entry for" + channel_name + " under the logs folder.")

if len(sys.argv) != 3:
    raise Exception("It needs exactly 2 arguments to use this decipher program, channel name and the key.")
elif sys.argv[2].endswith('.txt'):
    channel_name = sys.argv[1]
    logKey_file = sys.argv[2]
    key = ""
    with open(logKey_file, 'rb') as logkey:
        key = logkey.read()
    decipher(channel_name,key)
else:
    raise Exception("You need to run python decipher_logs.py \\<#channel_name> <symmetric key file>")
