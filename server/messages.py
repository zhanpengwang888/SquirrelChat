#update Wed for new import
#the upload inspired by https://blog.csdn.net/thare_lam/article/details/49506565
import hashlib
import struct
import os
BUFFER_SIZE = 1024
HEAD_STRUCT = '128sIq32s'
info_size = struct.calcsize(HEAD_STRUCT) #header size are predefined



class Message:
    """Abstract base class for representing messages sent to clients"""
    def __init__(self):
        pass
    
    def render(self):
        """Expected to return bytes"""
        pass

class JoinMessage(Message):
    def __init__(self,channel,connection):
        self.channel = channel
        self.connection = connection

    def render(self):
        self.connection.state.joinChatRoom(self.channel, self.connection)
        m = "join {}".format(self.channel)
        return m.encode()

class UpdatePasswordMessage(Message):
    def __init__(self,newpassword, connection):
        self.newpassword = newpassword
        self.connection = connection

    def render(self):
        m = "updatepassword {}".format(self.newpassword)
        self.connection.state.update_password(self.connection, self.newpassword)
        return m.encode()

class BlockMessage(Message):
    def __init__(self,user, connection):
        self.blockeduser = user
        self.connection = connection

    def render(self):
        self.connection.state.block_user(self.blockeduser, self.connection)
        m = "block {}".format(self.blockeduser)
        return m.encode()

class UnblockMessage(Message):
    def __init__(self,user, connection):
        self.blockeduser = user
        self.connection = connection

    def render(self):
        self.connection.state.unblock_user(self.blockeduser, self.connection)
        m = "unblock {}".format(self.blockeduser)
        return m.encode()

class BanMessage(Message):
    def __init__(self,channel,user, connection):
        self.channel = channel
        self.banneduser = user
        self.connection = connection

    def render(self):
        self.connection.state.ban_user(self.channel, self.banneduser, self.connection)
        m = "ban {} {}".format(self.banneduser,self.channel)
        return m.encode()

class UnbanMessage(Message):
    def __init__(self,channel,user, connection):
        self.banneduser = user
        self.channel = channel
        self.connection = connection

    def render(self):
        self.connection.state.unban_user(self.channel, self.banneduser, self.connection)
        m = "unban {} {}".format(self.banneduser,self.channel)
        return m.encode()

class GetTopicMessage(Message):
    def __init__(self,channel,connection):
        self.channel = channel
        self.connection = connection

    def render(self):
        current_topic = self.connection.state.getTopic(self.channel, self.connection)
        TopicMessage(self.channel, current_topic, self.connection).render()
        m = "gettopic {}".format(self.channel)
        return m.encode()

class SetTopicMessage(Message):
    def __init__(self,channel,topic,connection):
        self.channel = channel
        self.topic = topic
        self.connection = connection

    def render(self):
        self.connection.state.setTopic(self.channel, self.topic, self.connection)
        m = "settopic {} {}".format(self.channel,self.topic)
        return m.encode()

class TopicMessage(Message):
    def __init__(self,channel,topic,connection):
        self.channel = channel
        self.topic = topic
        self.connection = connection

    def render(self):
        string = self.topic.split()
        if "error" not in string:
            m = "topic {} {}".format(self.channel,self.topic)
            self.connection.conn.sendall(m)
            self.connection.conn.sendall("\n")
            return m.encode()
        else:
            return False
    
class AuthenticateMessage(Message):
    def __init__(self,username,password, connection):
        self.username = username
        self.password = password
        self.connection = connection

    def render(self):
        self.connection.state.authenticate(self.username, self.password, self.connection)
        m = "authenticate {} {}".format(self.username, self.password)
        return m.encode()

class RegisterMessage(Message):
    def __init__(self,username,password, connection):
        self.username = username
        self.password = password
        self.connection = connection

    def render(self):
        self.connection.state.register(self.username, self.password, self.connection)
        self.connection.state.register_observer(self.username, self.connection)
        m = "register {} {}".format(self.username, self.password)
        return m.encode()

class ChatMessage(Message):
    def __init__(self,user_or_channel,message,connection):
        self.user_or_channel = user_or_channel
        self.message = message
        self.connection = connection
    
    def render(self):
        try:
            self.connection.state.handle_chat(self.connection.state.reverse_connections[self.connection] ,self.user_or_channel, self.message, self.connection)
            m = "chat {} {} {}".format(self.user_or_channel,len(self.message),self.message)
            return m
        except:
            return ErrorMessage("[chat message] You have not yet logged in. Please log in first.", self.connection).render()

class ChatFromMessage(Message):
    """A reply from the server notifying a client that they have received a message from either a user or a channel"""
    def __init__(self,fromuser,channel,message):
        self.fromuser = fromuser
        self.channel = channel
        self.message = message
    
    def render(self):
        string = self.message.split()
        if "error" not in string:
            m = "chatfrom {} {} {}".format(self.fromuser,self.channel,self.message)
            return m
        else:
            return False

class ErrorMessage(Message):
    """Indicates that some error has occurred"""
    def __init__(self,message,connection):
        self.message = message
        self.connection = connection
    
    def render(self):
        m = "error {}".format(self.message)
        self.connection.conn.sendall(m)
        self.connection.conn.sendall("\n")
        return m.encode()

class LeaveMessage(Message):
    """The sender will now stop receiving chatfrom messages sent to #channel"""
    def __init__(self,channel,connection):
        self.channel = channel
        self.connection = connection
    
    def render(self):
        self.connection.state.leave_chat_room(self.channel, self.connection)
        m = "leave {}".format(self.channel)
        return m.encode()

class LogoffMessage(Message):
    """The user will log off from the chat server"""
    def __init__(self, connection):
        self.connection = connection
    
    def render(self):
        self.connection.state.logoff(self.connection)
        m = "logout"
        return m.encode()

class ExitMessage(Message):
    """The user will exit from the chat server"""
    def __init__(self, connection):
        self.connection = connection
    
    def render(self):
        self.connection.state.exit(self.connection)
        self.connection.conn.close()
        m = "exit"
        return m.encode()

#update wed
class UploadMessage(Message):
    def __init__(self,target,connection):
        self.target = target
        self.file_path = ""  #initialize the file path, we will find it later
        self.connection = connection
    
    def cal_md5(self,file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def unpack_file_info(self,file_info):
        file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
        file_name = file_name[:file_name_len]
        return file_name, file_size, md5

    def render(self):
        #first we will let user to tell us the file path
        #print(self.connection)
        #self.connection.conn.sendall("Hello my friend")
        if self.connection.getUserStatus:    
            file_info_package = self.connection.conn.recv(info_size)
            print(str(file_info_package))
            print(len(file_info_package))
            file_name, file_size, md5_recv = self.unpack_file_info(file_info_package)
            print "file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5_recv))
            recved_size = 0
            with open(file_name, 'wb') as fw:
                while recved_size < file_size:
                    remained_size = file_size - recved_size
                    recv_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                    recv_file = self.connection.conn.recv(recv_size)
                    recved_size += recv_size
                    fw.write(recv_file)
            md5 = self.cal_md5(file_name)
            if md5 != md5_recv:
                print 'MD5 compared fail!'
            else:
                print 'Received successfully'
            self.connection.state.upload_file(self.connection.state.reverse_connections[self.connection],self.target, file_name,self.connection)
            m = "upload {} {}".format(file_name,self.target)
            return m.encode()
        else:
             return ErrorMessage("[upload file message] You have not yet logged in. Please log in first.", self.connection).render()           
        #update the state and transmit to file server

class ListfilesMessage(Message):
    def __init__(self,target,connection):
        self.target = target
        self.connection = connection
    
    def render(self):
        if self.connection.getUserStatus:
            self.connection.state.list_files(self.connection.state.reverse_connections[self.connection],self.target,self.connection)
            m = "getfiles {}".format(self.target)
            return m.encode()            
        else:
            return ErrorMessage("[Listfiles message] You have not yet logged in. Please log in first.", self.connection).render() 
#ask what is the actual difference...
class UpdateMessage(Message):
    def __init__(self,target,connection):
        self.target = target
        self.connection = connection
    
    def cal_md5(self,file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def unpack_file_info(self,file_info):
        file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
        file_name = file_name[:file_name_len]
        return file_name, file_size, md5

    def render(self):
        #first we will let user to tell us the file path
        #print(self.connection)
        #self.connection.conn.sendall("Hello my friend")
        if self.connection.getUserStatus:    
            file_info_package = self.connection.conn.recv(info_size)
            print(str(file_info_package))
            file_name, file_size, md5_recv = self.unpack_file_info(file_info_package)
            print "file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5_recv))
            recved_size = 0
            with open(file_name, 'wb') as fw:
                while recved_size < file_size:
                    remained_size = file_size - recved_size
                    recv_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                    recv_file = self.connection.conn.recv(recv_size)
                    recved_size += recv_size
                    fw.write(recv_file)
            md5 = self.cal_md5(file_name)
            if md5 != md5_recv:
                print 'MD5 compared fail!'
            else:
                print 'Received successfully'
            self.connection.state.update_file(self.connection.state.reverse_connections[self.connection],self.target, file_name,self.connection)
            m = "update {} {}".format(file_name,self.target)
            return m.encode()
        else:
             return ErrorMessage("[update message] You have not yet logged in. Please log in first.", self.connection).render() 

class RemoveMessage(Message):
    def __init__(self,target,filename,connection):
        self.target = target
        self.connection = connection
        self.file_name = filename
    
    def render(self):
        if self.connection.getUserStatus:
            self.connection.state.remove_file(self.connection.state.reverse_connections[self.connection],self.target,self.file_name,self.connection)
            m = "remove {} {}".format(self.target, self.file_name)
            return m.encode()            
        else:
            return ErrorMessage("[remove message] You have not yet logged in. Please log in first.", self.connection).render()

class DownloadMessage(Message):
    def __init__(self,target,filename,connection):
        self.target = target
        self.connection = connection
        self.file_name = filename
    
    def render(self):
        if self.connection.getUserStatus:
            self.connection.state.download_file(self.connection.state.reverse_connections[self.connection],self.target,self.file_name,self.connection)
            m = "download {} {}".format(self.target, self.file_name)
            return m.encode()            
        else:
            return ErrorMessage("[download messge] You have not yet logged in. Please log in first.", self.connection).render()  

class KeyexchangeMessage(Message):
    """key exchange from a to b"""
    def __init__(self, receiver, key, connection):
        self.receiver = receiver
        self.key = key
        self.connection = connection
    
    def render(self):
        self.connection.state.exchange_key(self.receiver, self.key, self.connection)
        m = "exchange_key {} {}".format(self.receiver, self.key)
        return m

class KeyexchangeTheOtherSideMessage(Message):
    """key exchange from b to a"""
    def __init__(self, receiver, key, connection):
        self.receiver = receiver
        self.key = key
        self.connection = connection
    
    def render(self):
        self.connection.state.exchange_key_the_other_side(self.receiver, self.key, self.connection)
        m = "exchange_key_the_other_side {} {}".format(self.receiver, self.key)
        return m
