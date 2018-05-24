from threading import *
from socket import *
import time
import sys
import ssl
#update Monday night
import os
import hashlib
import struct
import nacl.utils
from nacl.public import PrivateKey, Box, PublicKey
BUFFER_SIZE = 1024
HEAD_STRUCT = '128sIq32s'
info_size = struct.calcsize(HEAD_STRUCT) #header size are predefined


channels = {}


class RecvLoop(Thread):
    def __init__(self, socket, client):
        Thread.__init__(self)
        self.socket = socket
        self.client = client

    def run(self):
        print("Accepting data from server.")
        while True:
            d = self.socket.recv(1024)
            self.client.handle(d)

class Client(Thread):
    def __init__(self, server, port):
        Thread.__init__(self)
        self.server = server
        self.port = port
        self.start()
        self.channels = {}
        self.current_channel = None
        self.shared_key = {}
        self.private_key = PrivateKey.generate() #generate private key
        self.public_key_encoded = self.private_key.public_key.encode(encoder=nacl.encoding.Base64Encoder)
        self.public_key = self.private_key.public_key #use private key to get public key

    def run(self):
        print("Connecting to server...")
        self.connection = socket(AF_INET, SOCK_STREAM)
        ##context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_verify_locations("./../server/cert.pem")
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        self.connection = context.wrap_socket(self.connection, server_hostname='chatserver')
        self.connection.connect((self.server, self.port))
        print("Welcome to SquirrelChat!")
        print("Not logged in yet, either /authenticate or /register\n")
        print("Commands:\n")
        print("/join #channel")
        print("/register <username> <password>")
        print("/authenticate <username> <password>")
        print("/update_pw <password>")
        print("/settopic #channel <new topic> <-- Sets topic for a channel")
        print("/gettopic #channel <-- Gets the current topic from a channel")
        print("/block <username>")
        print("/unblock <username>")
        print("/ban <username> <channel>")
        print("/unban <username> <channel>")
        print("/exchangekey <username> << exchange key with a user")
        print("/chat <username> << open up chat with <username> Note: you have to exchange key with that person in order to have a secure chat")
        print("/leave #channel << leave a channel")
        print("/logout << log out SquirrelChat.")
        print("/upload <filename> << upload a file")
        print("/update <filename> << update a file")
        print("/download <username> <filename> << download a file from a user")
        print("/getfiles <filename> << get a file")
        print("/remove <username> <filename> << remove a file from a user's directory")
        self.loop()

    def display_chat(self, entity, chat):
        print("{}> {}".format(entity, chat))

    # Handle a message from the server
    def handle(self, d):
        if d == "\n":
            return
        pieces = d.split()
        if len(pieces) == 0:
            print("error: got empty packet")
            exit(1)
        # These are the only things that should come back from the server
        elif pieces[0] == "chatfrom":
            chat = d.split(' ', 3)
            if pieces[2][0] == "#":
                print("{} said {} in the channel {}".format(chat[1], chat[3],chat[2]))
            else:
                #we need to decrpyt text here
                from_user = chat[1]
                my_box = Box(self.private_key,self.shared_key[from_user]) #since we can't chat with those we don't have public key, no error checking here
                print("chat message is {}".format(chat[3]))
                msg_recv = my_box.decrypt(chat[3])
                print("{} said {}".format(from_user, msg_recv))
            # if not chat[2] in self.channels:
            #     # Notify the user of the first chat on a channel
            #     self.channels[chat[2]] = [(chat[1], chat[3])]
            #     print("Attention: First chat on channel {}".format(chat[2]))
            # else:
            #     # Log this in case they go back later
            #     self.channels[chat[2]].append((chat[1], chat[3]))
            # if self.current_channel == chat[2]:
            #     self.display_chat(chat[1], chat[3])
        elif pieces[0] == "topic":
            topic = d.split(' ', 2)
            print("The topic for {} is {}".format(topic[1], topic[2]))
        elif pieces[0] == "error":
            print("Error! {}".format(d.split(' ', 1)[1]))
        elif pieces[0] == "downloading":
            #print (str(info_size))
            file_info_package = self.connection.recv(info_size)
            #print("the header we get is:    " + str(file_info_package))
            #print("the length of header is " + str(len(file_info_package)))
            file_name, file_size, md5_recv = self.unpack_file_info(file_info_package)
            print ("file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5_recv)))
            recved_size = 0
            with open(file_name, 'wb') as fw:
                while recved_size < file_size:
                    remained_size = file_size - recved_size
                    recv_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                    recv_file = self.connection.recv(recv_size)
                    recved_size += recv_size
                    fw.write(recv_file)
            md5 = self.cal_md5(file_name)
            if bytes(md5) != md5_recv:
                print ('MD5 compared fail!')
            else:
                print ('Received successfully')
        elif pieces[0] == "exchange_key":   
            result = d.split(' ', 2)
            from_user = result[1]
            key_received_encoded = result[2]
            key_received = PublicKey(key_received_encoded, encoder=nacl.encoding.Base64Encoder)
            self.shared_key[from_user] = key_received # save the other's public key and return ours
            print("I am exchanging!")
            print("the key we got is {} from {}".format(key_received,from_user))
            #print("the shared_key dic is {}".format(self.shared_key))
            self.send("exchange_key_the_other_side {} {}".format(from_user, self.public_key_encoded))  #b received a key from a, and need to send its key back to a
        elif pieces[0] == "exchange_key_the_other_side": # from b to a
            result = d.split(' ', 2)
            from_user = result[1]
            key_received_encoded = result[2]
            key_received = PublicKey(key_received_encoded, encoder=nacl.encoding.Base64Encoder)
            print("I am in exchange the other side!")
            print("we got the key {}".format(key_received))
            self.shared_key[from_user] = key_received
        else:
            #print("The server has sent back a response I can't parse:")
            print("handle " + d)
            #print('>')

    # Note: Doesn't check whether channel login was successful
    def change_to(self, channel):
        self.current_channel = channel
        print("Changed to channel {}".format(self.current_channel))
        # To all you students: perhaps think about showing the sent
        # since the last time that the user logged into this channel.

    # Note: No checking on the client end
    def handle_input(self, i):
        #print("Here!")
        cmd = i.split()
        if (cmd[0] == "/join"):
            if len(cmd) >= 2:
                print("Joining {}..".format(cmd[1]))
                self.send("join {}".format(cmd[1]))
                time.sleep(.2)
                self.send("gettopic {}".format(cmd[1]))
                self.change_to(cmd[1])
            else:
                print("Invalid join command. Should be /join <#channel>")
        elif (cmd[0] == "/register"):
            if len(cmd) >= 3:
                print("Registering...")
                self.send("register {} {}".format(cmd[1], cmd[2]))
                self.current_user = cmd[1]
            else:
                print("Invalid register command. Should be /register <username> <password>")
        elif (cmd[0] == "/authenticate"):
            if len(cmd) >=3:
                self.send("authenticate {} {}".format(cmd[1], cmd[2]))
                self.current_user = cmd[1]
            else:
                print("Invalid authenticate command. Should be /authenticate <username> <password>")
        elif (cmd[0] == "/gettopic"):
            if len(cmd) >= 2:
                self.send("gettopic {}".format(cmd[1]))
            else:
                print("Invalid gettopic command. Should be /gettopic <#channel>")
        elif (cmd[0] == "/settopic"):
            if len(cmd) >= 3:
                self.send("settopic {} {}".format(cmd[1], i.split(' ', 2)[2]))
            else:
                print("Invalid settopic command. Should be /settopic <#channel> <topic>")
        elif (cmd[0] == "/block"):
            if len(cmd) >= 2:
                self.send("block {}".format(cmd[1]))
            else:
                print("Invalid block command. Should be /block <username>")
        elif (cmd[0] == "/unblock"):
            if len(cmd) >= 2:
                self.send("unblock {}".format(cmd[1]))
            else:
                print("Invalid block command. Should be /unblock <username>")
        elif (cmd[0] == "/ban"):
            if len(cmd) >= 3:
                self.send("ban {} {}".format(cmd[1], cmd[2]))
            else:
                print("Invalid ban command. Should be /ban <#channel> <username>")
        elif (cmd[0] == "/privmsg"):
            if len(cmd) >= 2:
                print("Now in private message with user {}".format(cmd[1]))
                self.change_to(cmd[1])
            else:
                print("Invalid privmsg command. Should be /privmsg <username>")
        elif (cmd[0] == "/update_pw"):
            if len(cmd) >= 2:
                print("Changing the password...")
                self.send("update_pw {}".format(cmd[1]))
            else:
                print("Invalid update_pw command. Should be /update_pw <password>")
        elif (cmd[0] == "/unban"):
            if len(cmd) >= 3:
                self.send("unban {} {}".format(cmd[1], cmd[2]))
            else:
                print("Invalid unban command. Should be /unban <#channel> <username>")
        elif (cmd[0] == "/leave"):
            if len(cmd) >= 2:
                self.send("leave {}".format(cmd[1]))
            else:
                print("Invalid leave command. Should be /leave <#channel>")
        elif (cmd[0] == "/logout"):
            self.send("logout")
        elif (cmd[0] == "/exit"):
            self.send("exit")
        #Monday night update
        elif (cmd[0] == "/upload"):
            if len(cmd) >= 2:
                #self.send("upload {}".format(cmd[1]))
                file_path = self.get_path()
                print(file_path)
                #try:
                file_name, file_name_len, file_size, md5 = self.get_file_info(file_path)
                file_head = struct.pack(HEAD_STRUCT, file_name, file_name_len, file_size, md5)
                print ("file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5)))
                print ("file head is {}".format(str(file_head)))
                #try:
                print("start connecting")
                #tell server to ready for the file
                self.send("upload {}".format(cmd[1]))
                time.sleep(.2) #rest to avoid race condition
                self.send(file_head) #send the head to tell chat server how much to recv
                sent_size = 0 #keep track of the how much we have sent

                with open(file_path) as file:
                    while sent_size < file_size:
                        remained_size = file_size - sent_size
                        send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                        send_file = file.read(send_size)
                        sent_size += send_size
                        self.send(send_file)
            else:
                print("Invalid upload command. Should be /upload <filename>")
        elif (cmd[0] == "/update"):
            if len(cmd) >= 2:
                file_path = self.get_path()
                #print(file_path)
                #try:
                file_name, file_name_len, file_size, md5 = self.get_file_info(file_path)
                file_head = struct.pack(HEAD_STRUCT, file_name, file_name_len, file_size, md5)
                print ("file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5)))
                #try:
                print("start connecting")
                #tell server to ready for the file
                self.send("update {}".format(cmd[1]))
                time.sleep(.2) #rest to avoid race condition
                self.send(file_head) #send the head to tell chat server how much to recv
                sent_size = 0 #keep track of the how much we have sent

                with open(file_path) as file:
                    while sent_size < file_size:
                        remained_size = file_size - sent_size
                        send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                        send_file = file.read(send_size)
                        sent_size += send_size
                        self.send(send_file)
            else:
                print("Invalid update command. Should be /update <filename>")
        elif (cmd[0] == "/getfiles"):
            if len(cmd) >= 2:
                self.send("getfiles {}".format(cmd[1]))
            else:
                print("Invalid getfiles command. Should be /getfiles <filename>")
        elif(cmd[0] == "/download"):
            if len(cmd) >= 3:
                self.send("download {} {}".format(cmd[1],cmd[2]))
            else:
                print("Invalid download command. Should be /download <username> <filename>")
        elif (cmd[0] == "/remove"):
            if len(cmd) >= 3:
                self.send("remove {} {}".format(cmd[1], cmd[2]))
            else:
                print("Invalid remove command. Should be /remove <username> <filename>")
        elif (cmd[0] == "/chat"):
            if len(cmd) >= 3:
                if cmd[1][0] != "#":
                    if cmd[1] not in self.shared_key.keys():   # if there's no shared keys, then we simply don't send the chat command. Instead, we exchange keys
                        print("you can not chat with someone without exchanging key with him/her.")
                    else:
                        temp = i.split(' ',2)
                        pub_key = self.shared_key[cmd[1]]
                        #print("pub_key of {} is {}".format(cmd[1], pub_key))
                        msg_to_send = bytes(temp[2])
                        #encrypt text here
                        user_box = Box(self.private_key, pub_key)
                        encrypted_msg = user_box.encrypt(msg_to_send)
                        self.send("chat {} {}".format(cmd[1], encrypted_msg))
                else:
                    temp = i.split(' ',2)
                    self.send("chat {} {}".format(cmd[1], temp[2]))
            else:
                print("Invalid chat command. Should be /chat <username or channel> <message>")
        elif (cmd[0] == "/exchangekey"):
            if len(cmd) == 2:
                if cmd[1][0] != "#":
                    #if cmd[1] not in self.shared_key.keys():   # if there's no shared keys, then we simply don't send the chat command. Instead, we exchange keys
                    #print ("{} is public key, {} is private key".format(self.public_key, self.private_key))
                    key_exchange_encoded = self.public_key_encoded
                    #key_exchange_encoded = key_exchange.encode()
                    #print("{} is key_exchange".format(str(key_exchange_encoded)))
                    self.send("exchange_key {} {}".format(cmd[1], key_exchange_encoded))
                    #else:
                    #    print ("{} has already changed keys with you".format(cmd[1]))
                else:
                    print("can not exchange key to a channel!")
            else:
                print("Invalid exchangekey command. Should be /exchangekey <username>")
        else:
            print("Invalid Commands.")

    def send(self, msg):
        self.connection.send(msg)

    def loop(self):
        x = RecvLoop(self.connection, self)
        x.start()
        while True:
            #print('>')
            #x.join()
            try:
                i = raw_input('>')
                self.handle_input(i)
                time.sleep(.2)
            except:
                print("You have successfully exited.")
                return
            
    #all functions below updated on Monday
    def get_path(self):
        file_path = raw_input('Type the path to a file you would like to upload or update:')
        return file_path

    def cal_md5(self,file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5


    def get_file_info(self,file_path):
        file_name = os.path.basename(file_path)
        file_name_len = len(file_name)
        file_size = os.path.getsize(file_path)
        md5 = self.cal_md5(file_path)
        return file_name, file_name_len, file_size, md5

    def unpack_file_info(self,file_info):
        file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
        file_name = file_name[:file_name_len]
        return file_name, file_size, md5


if (len(sys.argv) == 3):
    client = Client(sys.argv[1], int(sys.argv[2]))
else:
    raise Exception("python textclient.py <server> <port> <-- If running on same machine, <server> is localhost")
