# from user import *
from messages import *
import sqlite3
import csv
import requests
import time
from Crypto.Cipher import AES
import os, random, struct
from subprocess import call
from cryptography.fernet import Fernet
from passlib.hash import bcrypt_sha256
from jinja2 import escape

HEAD_STRUCT = '128sIq32s'
BUFFER_SIZE = 1024
PADDING = 'A' * 1024
KEY = ""
with open("./key.txt", 'r') as file:
    KEY = file.read()

DATABASE_PATH = os.path.join(os.path.dirname(__file__), './../shared_database.db')
invalid_input = "&=+<>-"


def connect_db():
    return sqlite3.connect(DATABASE_PATH)


class User:
    def __init__(self, username, password, connection):
        self.username = username
        self.password = password
        self.loginStatus = False
        self.chatroom = {}  # chat room name - chat room object pairs
        self.blockedUser = []
        self.connection = connection
        self.adminstration = {}  # chat room name - chat room object pairs
        connection.changeUserStatus()
        # update Tuesday
        self.owning_file_list = []
        self.get_file_list = []
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT files FROM `user` WHERE username=?',
                    (username,))
        row_user = cur.fetchone()
        conn.commit()
        conn.close()
        if row_user is not None:
            if row_user[0] is not None:
                temp = row_user[0].split(',')
                for temp_file_name in temp:
                    if temp_file_name != "":
                        self.get_file_list.append(temp_file_name)

    def getUserName(self):
        return self.username

    def getChatRoom(self):
        return self.chatroom

    def change_loginStatus(self):
        self.loginStatus = True

    def get_loginStatus(self):
        return self.loginStatus

    def getBlockedUsers(self):
        return self.blockedUser

    # user joins a chat room
    # may need to have a proper error message
    def join_chat_room(self, ChatRoom):
        # check if the user is already in this chat room or not
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT user, banned_list, admin, filesList FROM `channel` WHERE channelname=?',
                    (ChatRoom.getName(),))
        row_channel = cur.fetchone()
        conn.commit()
        conn.close()
        if self.username not in ChatRoom.getUsers().keys():
            # check if the user get banned from the Chat Room
            if row_channel[1] is not None:
                if self.username not in row_channel[1]:
                    # add the chat room to the user's dictionary of chat rooms
                    self.chatroom[ChatRoom.getName()] = ChatRoom
                    if self.username in row_channel[2]:
                        self.adminstration[ChatRoom.getName()] = ChatRoom
                    return True
                else:
                    ErrorMessage(self.username + " is banned from this chatroom.", self.connection).render()
                    return False
            else:
                self.chatroom[ChatRoom.getName()] = ChatRoom
                if self.username in row_channel[2]:
                    self.adminstration[ChatRoom.getName()] = ChatRoom
                return True
        else:
            ErrorMessage(self.username + " is already in this chatroom.", self.connection).render()
            return False

    # user leaves a chat room
    # may need to have a proper error message
    def leave_chat_room(self, ChatRoom):
        # check if the user is in this chat room or not
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT user, banned_list, admin, filesList FROM `channel` WHERE channelname=?',
                    (ChatRoom.getName(),))
        row_channel = cur.fetchone()
        conn.commit()
        conn.close()
        if self.username in row_channel[0]:
            # this needs to be changed after I implement the ChatRoom class
            if ChatRoom.getName() in self.chatroom.keys():
                del self.chatroom[ChatRoom.getName()]
            return True
        ErrorMessage("User is not in this chatroom already.", self.connection).render()
        return False

    # user blocks anther user.
    # user is a type of User class
    def block(self, user):
        """"Let the user block another user"""
        # user is a string type
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT blocked FROM `user` WHERE username=?',
                    (self.username,))
        row_user = cur.fetchone()
        conn.commit()
        conn.close()
        if user not in row_user[0]:
            self.blockedUser.append(user)
            return True
        ErrorMessage(user + " has been blocked by you already.", self.connection).render()
        return False

    def unblock(self, user):
        """Let the user unblock another user"""
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT blocked FROM `user` WHERE username=?',
                    (self.username,))
        row_user = cur.fetchone()
        conn.commit()
        conn.close()
        if user in row_user[0]:
            if user in self.blockedUser:
                self.blockedUser.remove(user)
            return True
        ErrorMessage(user + " is not in your blocked list. Invalid unblock command", self.connection).render()
        return False

    # update Tuesday night
    def file_owning(self, file_name):
        self.owning_file_list.append(file_name)
        for file in self.owning_file_list:
            print("user {} uploads file {}".format(self.username, file))

            # if the file comes from a private message

    def file_getting(self, file_name):
        self.get_file_list.append(file_name)
        for file in self.get_file_list:
            print("user {} gets file {}".format(self.username, file))


class ChatRoom:
    def __init__(self, name, admin):
        self.topic = admin + "'s chat room"
        self.users = {}
        self.adminstrator = admin
        self.name = name
        self.bannedUsers = {}  # username-User class pair
        # update Tueday
        self.get_file_list = []
        self.channel_conversation_count = 0
        self.channel_conversation_timestamp = 0

    def getChannelConversationTimestamp(self):
        return self.channel_conversation_timestamp

    def setChannelConverstationTimestamp(self, number):
        self.channel_conversation_timestamp = number

    def clearChannelConverstationCount(self):
        self.channel_conversation_count = 0

    def incrementChannelConversationCount(self):
        self.channel_conversation_count += 1

    def getChannelConversationCount(self):
        return self.channel_conversation_count

    # for part 3 above

    def getBannedUserDict(self):
        return self.bannedUsers

    def getUsers(self):
        return self.users

    def getName(self):
        return self.name

    def getTopic(self):
        """Get topic for the user"""
        return self.topic

    def setTopic(self, newTopic):
        """Set the topic of the chat room. Only the admin has the right to set a topic"""
        self.topic = newTopic

    def get_admin(self):
        return self.adminstrator

    def add_user(self, user):
        """add the user to the chat room"""
        username = user.getUserName()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT user, banned_list, admin, filesList FROM `channel` WHERE channelname=?',
                    (self.name,))
        row_channel = cur.fetchone()
        conn.commit()
        conn.close()
        if row_channel[1] is not None:
            if username not in row_channel[1]:
                if username not in self.users.keys():
                    self.users[username] = user
                    return True
                # ErrorMessage(username + " is not in this chatroom.",self.connection).render()
                return False
            # ErrorMessage(username + " is banned from this chatroom.",self.connection).render()
            return False
        else:
            if username not in self.users.keys():
                self.users[username] = user
                return True

    def ban(self, user):
        """ban a user from the chat room"""
        self.bannedUsers[user.getUserName()] = user
        return True

    def unban(self, username):
        """unban a user from the chat room"""
        if username in self.bannedUsers:
            del self.bannedUsers[username]
        return True

    def leave(self, username):
        """Let a user leave the chat room"""
        if username in self.users:
            del self.users[username]
        return True

    # update wed
    def file_getting(self, file_name):
        self.get_file_list.append(file_name)
        for file in self.get_file_list:
            print("channel {} has file {}".format(self.name, file))


"""ban: check admin login status and user login status, check the validity of chat room, the existance of the chat room
user is in chat room or not, has user been banned before?, admin is admin?"""
"""unban: all conditions except for that user does not have to be in the chat room"""
"""block: two users have to log in, the existance of the blocked user, the user who will get banned gets banned before? """
"""and chat"""


class State:
    """"Class for managing the global state of the server"""

    def __init__(self, password_file):
        self.users = {}  # No current users
        self.channels = {}  # No current channels, chatroom name - chatroom object pair
        self.loggedin_usernames = []
        self.connections = {}  # Map from usernames to Connection objects
        self.reverse_connections = {}  # Map from connection objects to username
        self.password_file = password_file
        # update Wed
        self.file_secure = {}
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT channelname, admin FROM `channel`')
        row_channel = cur.fetchall()
        conn.commit()
        conn.close()
        for one_channel in row_channel:
            self.channels[one_channel[0]] = ChatRoom(one_channel[0], one_channel[1])

    def exchange_key(self, receiver, key, connection):
        """key exchange from a to b"""
        try:
            from_user = self.reverse_connections[connection]
            # from_user_object = self.users[from_user]
            if receiver in self.loggedin_usernames:
                # to_receiver = self.users[receiver]
                connection_of_to_receiver = self.connections[receiver]
                msg = "exchange_key " + from_user + " " + key
                return self.notify(receiver, msg, connection_of_to_receiver)
            else:
                return ErrorMessage("[exchange_key] Target user is not logged in / does not exist", connection).render()
        except:
            return ErrorMessage("[exchange_key] You have not yet logged in. Please log in first.", connection).render()

    def exchange_key_the_other_side(self, receiver, key, connection):
        """key exchange from a to b"""
        try:
            from_user = self.reverse_connections[connection]
            # from_user_object = self.users[from_user]
            if receiver in self.loggedin_usernames:
                # to_receiver = self.users[receiver]
                connection_of_to_receiver = self.connections[receiver]
                msg = "exchange_key_the_other_side " + from_user + " " + key
                return self.notify(receiver, msg, connection_of_to_receiver)
            else:
                return ErrorMessage("[exchange key the other side] Target user is not logged in / does not exist",
                                    connection).render()
        except:
            return ErrorMessage("[exchange_key_the_other_side] You have not yet logged in. Please log in first.",
                                connection).render()

    def handle_chat(self, fromuser, to, message, connection):
        """Perform the work to notify each user associated with a given channel or private message"""
        try:
            if to.startswith("#"):
                # To a channel
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('SELECT banned_list FROM `channel` WHERE channelname=?', (to,))
                row_channel = cur.fetchone()
                banned_list = row_channel[0]
                if to in self.channels:
                    chan = self.channels[to]
                    if fromuser in chan.getUsers().keys():
                        current_sender = chan.getUsers()[fromuser]
                        if fromuser in banned_list:
                            banned_user_object = self.users[fromuser]
                            if self.channels[to].ban(self.users[fromuser])\
                            and self.channels[to].leave(fromuser):
                                banned_user_object.leave_chat_room(self.channels[to])
                                return ErrorMessage("You cannot send message to this chat room " + to + " because you have been banned from this chat room.", connection).render()
                        # Send the message to each member of this channel
                        msg_object = ChatFromMessage(fromuser, to, message)
                        msg = msg_object.render()
                        for username in chan.getUsers().keys():
                            receiver = chan.getUsers()[username]
                            if username == fromuser:
                                # writing into the log of the channel
                                log_text = fromuser + " > " + message  # log text to be written into the channel's log file
                                # Database encryption for channel message
                                encryption_for_db = ""
                                with open("logKey.txt", 'rb') as file:
                                    encryption_for_db = file.read()
                                cipher = Fernet(encryption_for_db)
                                text_to_encrypt_in_db = log_text
                                log_text_encrypted_in_db = cipher.encrypt(text_to_encrypt_in_db.encode())

                                # store it into the db
                                cur.execute('INSERT INTO `chats` VALUES(NULL, NULL, ?, ?, ?)', (to, fromuser, log_text_encrypted_in_db))
                                conn.commit()
                                conn.close()

                                current_timestampe = chan.getChannelConversationTimestamp()
                                with open(os.path.join("logs", "log-%s-%d.log" % (to, current_timestampe)), 'a') as log:
                                    log.write(log_text)
                                chan.incrementChannelConversationCount()
                                if chan.getChannelConversationCount() >= 20:
                                    # encryption starts
                                    encryption = ""
                                    with open("logKey.txt", 'rb') as file:
                                        encryption = file.read()
                                    cipher = Fernet(encryption)
                                    text_to_encrypt = ""
                                    with open(os.path.join("logs", "log-%s-%d.log" % (to, current_timestampe)), 'r') as log:
                                        text_to_encrypt = log.read()
                                    log_text_encrypted = cipher.encrypt(text_to_encrypt.encode())
                                    with open(os.path.join("logs", "log-%s-%d.log" % (to, current_timestampe)), 'w') as log:
                                        log.write(log_text_encrypted)
                                    # create a new log
                                    timestamp = int(round(time.time() * 1000))
                                    open(os.path.join("logs", "log-%s-%d.log" % (to, timestamp)), 'a').close()
                                    chan.setChannelConverstationTimestamp(timestamp)
                                    chan.clearChannelConverstationCount()
                                self.notify(fromuser, "You have sent " + msg + " successfully.", connection)
                            else:
                                connection_of_to_user = self.connections[username]
                                if username not in chan.getBannedUserDict().keys():
                                    if current_sender.getUserName() not in receiver.getBlockedUsers():
                                        self.notify(username, msg, connection_of_to_user)
                                else:
                                    ErrorMessage(
                                        "You cannot send message to this chat room " + to + " because you have been banned from this chat room.",
                                        connection_of_to_user).render()
                    else:
                        return ErrorMessage("You are not in this chat room " + to + ".", connection).render()
                else:
                    return ErrorMessage("No such channel exists.", connection).render()
            else:
                # To another user
                # Make sure user is logged in
                if to in self.loggedin_usernames:
                    msg_object = ChatFromMessage(fromuser, to, message)
                    msg = msg_object.render()
                    connection_of_to_user = self.connections[to]
                    to_user = self.users[to]
                    if fromuser not in to_user.getBlockedUsers():
                        self.notify(fromuser, "You have sent " + msg + " to " + to + " successfully.", connection)
                        return self.notify(to, msg, connection_of_to_user)
                    else:
                        return self.notify(fromuser, "You have sent " + msg + " to " + to + " successfully.", connection)
                else:
                    return ErrorMessage("Target user is not logged in / does not exist", connection).render()
        except:
            return ErrorMessage("[handle chat] You have not yet logged in. Please log in first.", connection).render()

    def block_user(self, blocked_user, connection):
        """Let the current user block another user"""
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if current_user_object.block(blocked_user):
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (current_username,))
                row_banned_user = cur.fetchone()
                blocked = ""
                if row_banned_user[1] is not None:
                    blocked = row_banned_user[1] + blocked_user + ','
                else:
                    blocked = blocked_user + ','
                cur.execute('UPDATE `user` SET blocked=? WHERE username=?', (blocked, current_username))
                conn.commit()
                conn.close()
                return self.notify(current_username,
                                "You have blocked " + blocked_user + " successfully. You will not receive any message from " + blocked_user + " anymore.",
                                connection)
        except:
            return ErrorMessage("[block user] You have not yet logged in. Please log in first.", connection).render()

    def unblock_user(self, blocked_user, connection):
        """Let the current user unblock another user"""
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if current_user_object.unblock(blocked_user):
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (current_username,))
                row_banned_user = cur.fetchone()
                blocked_list = row_banned_user[1]
                blocked_list = blocked_list.replace(blocked_user + ',', '')
                cur.execute('UPDATE `user` SET blocked=? WHERE username=?', (blocked_list, current_username))
                conn.commit()
                conn.close()
                return self.notify(current_username,
                                "You have unblocked " + blocked_user + " successfully. You resume receiving messages from " + blocked_user + ".",
                                connection)
        except:
            return ErrorMessage("[unblock user] You have not yet logged in. Please log in first.", connection).render()

    def ban_user_helper(self, chatroom, banned_user, connection, current_username):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT admin FROM `channel` WHERE channelname=?', (chatroom,))
        row_channel = cur.fetchone()
        conn.commit()
        conn.close()
        if row_channel[0] is not None and current_username in row_channel[0]:
            banned_user_object = self.users[banned_user]  # this shows that we can only ban a logged in user
            # if (self.channels[chatroom].ban(self.channels[chatroom].getUsers()[banned_user]) # tricky here
            if self.channels[chatroom].ban(self.users[banned_user])\
                    and self.channels[chatroom].leave(banned_user):
                banned_user_object.leave_chat_room(self.channels[chatroom])
                    # and banned_user_object.leave_chat_room(self.channels[chatroom]):
                    # it's ok for us to ban a user that's not in the chatroom
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('SELECT user, banned_list, admin FROM `channel` WHERE channelname=?',
                            (chatroom,))
                row_channel = cur.fetchone()
                cur.execute('SELECT id, banned, channels FROM `user` WHERE username=?', (banned_user,))
                row_banned_user = cur.fetchone()
                banned_list = ""
                if row_channel[1] is not None:
                    banned_list = row_channel[1] + banned_user + ','
                else:
                    banned_list = banned_user + ','
                banned_channel = ""
                if row_banned_user[1] is not None:
                    banned_channel = row_banned_user[1] + chatroom
                else:
                    banned_channel = chatroom
                available_channels_after_ban = row_banned_user[2] # get all the channels that the user is in
                available_channels_after_ban = available_channels_after_ban.replace(chatroom,'')
                users_list = row_channel[0]
                users_list = users_list.replace(banned_user + ',', '')
                cur.execute('UPDATE `channel` SET banned_list=? WHERE channelname=?',
                            (banned_list, chatroom))
                cur.execute('UPDATE `user` SET banned=? WHERE username=?',
                            (banned_channel, banned_user))
                cur.execute('UPDATE `user` SET channels=? WHERE username=?',
                            (available_channels_after_ban, banned_user))
                cur.execute('UPDATE `channel` SET user=? WHERE channelname=?',
                            (users_list, chatroom))
                conn.commit()
                conn.close()
                return self.notify(current_username,
                                    "You have banned " + banned_user + " from the chat room " + chatroom + " successfully.",
                                    connection)
        else:
            return ErrorMessage("You are not the admin of this chat room " + chatroom + ".",
                                connection).render()
    
    def ban_user(self, chatroom, banned_user, connection):
        """Let the admin of the chat room ban the user from the chat room"""
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT user, banned_list, admin, filesList FROM `channel` WHERE channelname=?',
                        (chatroom,))
            row_channel_checking = cur.fetchone()
            conn.commit()
            conn.close()
            current_username = self.reverse_connections[connection]
            # current_user_object = self.users[current_username]
            if row_channel_checking is not None:
                # if the banned list is not Null.
                if row_channel_checking[1] is not None:
                    if banned_user not in row_channel_checking[1]:
                        return self.ban_user_helper(chatroom, banned_user, connection, current_username)
                    else:
                        return ErrorMessage(
                            "The user " + banned_user + " has already been banned from this chat room " + chatroom + ".",
                            connection).render()
                else:
                    return self.ban_user_helper(chatroom, banned_user, connection, current_username)
            else:
                return ErrorMessage("This chat room " + chatroom + " does not exist.", connection).render()
        except:
            return ErrorMessage("[ban user] You have not yet logged in. Please log in first.", connection).render()

    def unban_user(self, chatroom, banned_user, connection):
        """Let the admin of the chat room unban the user"""
        try:
            current_username = self.reverse_connections[connection]
            # current_user_object = self.users[current_username]
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT admin, banned_list FROM `channel` WHERE channelname=?', (chatroom,))
            row_channel = cur.fetchone()
            conn.commit()
            conn.close()
            if row_channel is not None and chatroom in self.channels.keys():
                if row_channel[1] is not None:
                    if banned_user in row_channel[1]:
                        if row_channel[0] is not None and current_username in row_channel[0]:
                            if self.channels[chatroom].unban(banned_user):
                                conn = connect_db()
                                cur = conn.cursor()
                                cur.execute('SELECT user, banned_list, admin FROM `channel` WHERE channelname=?',
                                            (chatroom,))
                                row_channel = cur.fetchone()
                                cur.execute('SELECT id, banned FROM `user` WHERE username=?', (banned_user,))
                                row_banned_user = cur.fetchone()
                                banned_users_list = ""
                                banned_users_list = row_channel[1]
                                banned_users_list = banned_users_list.replace(banned_user + ',', '')
                                banned_channels_list = ""
                                banned_channels_list = row_banned_user[1]
                                banned_channels_list = banned_channels_list.replace(chatroom, '')
                                cur.execute('UPDATE `channel` SET banned_list=? WHERE channelname=?',
                                            (banned_users_list, chatroom))
                                cur.execute('UPDATE `user` SET banned=? WHERE username=?',
                                            (banned_channels_list, banned_user))
                                conn.commit()
                                conn.close()
                                return self.notify(current_username,
                                                    "You have unbanned " + banned_user + " from the chat room " + chatroom + " successfully.",
                                                    connection)
                        else:
                            return ErrorMessage("You are not the admin of this chat room " + chatroom + ".",
                                                connection).render()
                    else:
                        return ErrorMessage(
                            "The user " + banned_user + " is not in the banned list of this chat room " + chatroom + ". Invalid unban command.",
                            connection).render()
                else:
                    return ErrorMessage("There is no one in the banned list.", connection).render()
            else:
                return ErrorMessage("This chat room " + chatroom + " does not exist.", connection).render()
        except:
            return ErrorMessage("[unban user] You have not yet logged in. Please log in first.", connection).render()

    def leave_chat_room(self, chatroom, connection):
        """Let the user leave the channel"""
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT user, banned_list, admin, filesList FROM `channel` WHERE channelname=?',
                        (chatroom,))
            row_channel_checking = cur.fetchone()
            conn.commit()
            conn.close()
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if row_channel_checking is not None and chatroom in self.channels.keys():
                if current_username in self.channels[chatroom].getUsers().keys():
                    if (self.channels[chatroom].leave(current_username) and current_user_object.leave_chat_room(
                            self.channels[chatroom])):
                        conn = connect_db()
                        cur = conn.cursor()
                        cur.execute('SELECT id, channels FROM `user` WHERE username=?', (current_username,))
                        row_user = cur.fetchone()
                        cur.execute('SELECT id, user FROM `channel` WHERE channelname=?', (chatroom,))
                        row_channel = cur.fetchone()
                        user_update = row_user[1]
                        user_update = user_update.replace(chatroom, "")
                        cur.execute('UPDATE `user` SET channels=? WHERE username=?', (user_update, current_username))
                        channel_update = row_channel[1]
                        channel_update = channel_update.replace(current_username + ',', "")
                        cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (channel_update, chatroom))
                        conn.commit()
                        conn.close()
                        return self.notify(current_username,
                                        "You have leaved the chat room " + chatroom + " successfully.", connection)
                    else:
                        return ErrorMessage("You fail to leave the chat room " + chatroom + ".", connection).render()
                else:
                    return ErrorMessage("You are not in this chat room " + chatroom + ".", connection).render()
            else:
                return ErrorMessage("This chat room " + chatroom + " does not exist.", connection).render()
        except:
            return ErrorMessage("[leave chat room] You have not yet logged in. Please log in first.",
                                    connection).render()

    def joinChatRoom(self, channel, connection):
        """Let the user join the chat room"""
        for i in range (len(channel)):
            if channel[i] in invalid_input:
                return ErrorMessage("Invalid chatroom name, try again!", connection).render()
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT user, admin FROM `channel` WHERE channelname=?', (channel,))
            row = cur.fetchone()
            if current_username in self.loggedin_usernames:
                #if channel in self.channels.keys() and row is not None:
                if row is not None and row[0] is not None: # check if the channel exists or not
                    try:
                        chatchatroom = self.channels[channel]
                    except:
                        admin_of_channel = row[1]
                        chatchatroom = ChatRoom(channel, admin_of_channel)
                        self.channels[channel] = chatchatroom
                    if (current_user_object.join_chat_room(chatchatroom) and chatchatroom.add_user(current_user_object)):
                        if current_username not in row[0]:
                            user_list = row[0] + current_username + ","
                            cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (user_list, channel)) # update the list of users of this channel
                        cur.execute('SELECT channels FROM `user` WHERE username=?', (current_username,)) # fetch the list of channels given the user
                        row = cur.fetchone()
                        if row[0] is not None:
                            channel_list = row[0] + channel # append the channel to the channel list
                        else:
                            channel_list = channel
                        if channel not in row[0]:
                            cur.execute('UPDATE `user` SET channels=? WHERE username=?', (channel_list, current_username)) # update the channel list given the username
                        conn.commit()
                        conn.close()
                        return self.notify(current_username, "You have join the chat room " + channel + " successfully.", connection)
                    else:
                        return ErrorMessage("You have failed to join the chat room " + channel + ". You probably get banned from this chat room.", connection).render()
                else:
                    newChatRoom = ChatRoom(channel, current_username)
                    conn = connect_db()
                    cur = conn.cursor()
                    topic = newChatRoom.getTopic()
                    admin = newChatRoom.get_admin()
                    user_list = admin + ","
                    cur.execute('INSERT INTO `channel` VALUES(NULL,?,?,?, ?, ?, ?);', (channel, topic, user_list, '', user_list, ''))
                    cur.execute('SELECT channels FROM `user` WHERE username=?', (current_username,)) # fetch the list of channels given the user
                    row = cur.fetchone()
                    print(row, row[0])
                    channel_list = ""
                    if row[0] is not None:
                        channel_list = row[0] + channel # append the channel to the channel list
                    else:
                        channel_list = channel
                    cur.execute('UPDATE `user` SET channels=? WHERE username=?', (channel_list, current_username)) # update the channel list given the username
                    cur.execute('UPDATE `user` SET adminsOfChannels=? WHERE username=?', (channel_list, current_username)) # update the channel list which he is the admin given the username
                    conn.commit()
                    conn.close()
                    #starting the log for the channel
                    timestamp = int(round(time.time() * 1000))
                    newChatRoom.setChannelConverstationTimestamp(timestamp)
                    if not os.path.exists("logs"):
                        os.mkdir("logs")
                    open(os.path.join("logs","log-%s-%d.log" % (channel, timestamp)), 'a').close()
                    self.channels[channel] = newChatRoom
                    current_user_object.join_chat_room(newChatRoom)
                    newChatRoom.add_user(current_user_object)
                    return self.notify(current_username, "You have join the chat room " + channel + " successfully. You are the admin of the chat room " + channel + ". ", connection)
        except:
            return ErrorMessage("[join chatroom] You have not yet logged in. Please log in first.", connection).render()

    def getTopic(self, chatroom, connection):
        """Let user get the topic of the chat room"""
        try:
            current_username = self.reverse_connections[connection]
            # current_user_object = self.users[current_username]
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT admin, banned_list FROM `channel` WHERE channelname=?', (chatroom,))
            row_channel = cur.fetchone()
            conn.commit()
            conn.close()
            if chatroom in self.channels.keys():
                # if the banned_list has no one in it, i.e. None Type, everyone can get the topic of the channel.
                if row_channel[1] is not None:
                    if current_username in self.channels[chatroom].getUsers().keys() and current_username not in row_channel[1]:
                        return self.channels[chatroom].getTopic()
                    else:
                        return ErrorMessage("You are not in this chat room " + chatroom + ".", connection).render()
                else:
                    if current_username in self.channels[chatroom].getUsers().keys():
                        return self.channels[chatroom].getTopic()
                    else:
                        return ErrorMessage("You are not in this chat room " + chatroom + ".", connection).render()
            else:
                return ErrorMessage("This chat room " + chatroom + " does not exist.", connection).render()
        except:
            return ErrorMessage("[get topic] You have not yet logged in. Please log in first.", connection).render()

    def setTopic(self, chatroom, newTopic, connection):
        """Let admin set the topic of the chat room"""
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if chatroom in self.channels.keys():
                if current_username in self.channels[chatroom].getUsers().keys():
                    conn = connect_db()
                    cur = conn.cursor()
                    cur.execute('SELECT admin FROM `channel` WHERE channelname=?', (chatroom,))
                    row_channel = cur.fetchone()
                    conn.commit()
                    conn.close()
                    if row_channel[0] is not None and current_username in row_channel[0]:
                        self.channels[chatroom].setTopic(newTopic)
                        conn = connect_db()
                        cur = conn.cursor()
                        newTopic = escape(newTopic)
                        cur.execute('UPDATE `channel` SET topic=? WHERE channelname=?', (newTopic, chatroom))
                        conn.commit()
                        conn.close()
                        return self.notify(current_username,
                                        "You have set the topic of the chat room " + chatroom + " successfully.",
                                        connection)
                    else:
                        return ErrorMessage("You are not the admin of this chat room " + chatroom + ".",
                                            connection).render()
                else:
                    return ErrorMessage("You are not in this chat room " + chatroom + ".", connection).render()
            else:
                return ErrorMessage("This chat room " + chatroom + " does not exist.", connection).render()
        except:
           return ErrorMessage("[set topic] You have not yet logged in. Please log in first.", connection).render()

    def register(self, username, password, connection):
        """Register a new user with a specified username and password."""
        if connection.getUserStatus():
            return ErrorMessage("You can only register 1 user at a single time.", connection).render()
        # Can't add a user to the set of users that's already there.
        # check if the user is already existed.
        # with open(self.password_file, 'rb') as csvfile:
        #     reader = csv.DictReader(csvfile)
        #     for row in reader:
        #         if username == row['username']:
        #             return ErrorMessage("Error: trying to register an account that already exists.", connection).render()
        for i in range (len(username)):
            if username[i] in invalid_input:
                return ErrorMessage("Invalid username, try again!", connection).render()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM `user` WHERE username=?', (username,))
        row = cur.fetchone()
        conn.commit()
        conn.close()

        if row is not None:
            return ErrorMessage("Error: trying to register an account that already exists.", connection).render()
        if username[0] != "#" and password != "":
            if username not in self.users.keys():
                password = bcrypt_sha256.hash(password)
                # with open(self.password_file, 'a') as csvfile:
                #     writer = csv.writer(csvfile)
                #     writer.writerow((username, password))
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('INSERT INTO `user` VALUES(NULL,?,?, ?, ?, ?, ?, ?);', (username, password, '', '', '', '', '',))
                conn.commit()
                conn.close()
                u = User(username, password, connection)
                self.users[username] = u
                self.reverse_connections[connection] = username
                self.loggedin_usernames.append(username)
                self.connections[username] = connection
                self.notify(username, "You have registered successfully", connection)
                return u
            else:
                return ErrorMessage("Error: trying to register an account that already exists.", connection).render()
        else:
            return ErrorMessage("Error: invalid username or password.", connection).render()

    def logoff(self, connection):
        """Log off the user from the chat server."""
        # need to take care of chatroom, if the user is the admin, s/he is still the admin.
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if current_username in self.loggedin_usernames:
                connection.changeUserStatus()
                # keep users in channels when they log out
                # for chatroom in current_user_object.getChatRoom().keys():
                    # del current_user_object.getChatRoom()[chatroom].getUsers()[current_username]
                self.loggedin_usernames.remove(current_username)
                del self.users[current_username]
                del self.reverse_connections[connection]
                msg = current_username + " has successfully logged off."
                return self.notify(current_username, msg, connection)
        except:
            return ErrorMessage("[log out] You have not yet logged in. So logging off does not make any sense.",
                               connection).render()

    def exit(self, connection):
        """Exit the chat server"""
        try:
            current_username = self.reverse_connections[connection]
            current_user_object = self.users[current_username]
            if current_username in self.loggedin_usernames:
                connection.changeUserStatus()
                #for chatroom in current_user_object.getChatRoom().keys():
                #    del current_user_object.getChatRoom()[chatroom].getUsers()[current_username]
                self.loggedin_usernames.remove(current_username)
                del self.users[current_username]
                del self.reverse_connections[connection]
                msg = current_username + " has successfully logged off."
                return self.notify(current_username, msg, connection)
        except:
            pass

    def register_observer(self, username, connection):
        """Add a connection object to the list of observers"""
        self.connections[username] = connection
        # self.reverse_connections[connection] = username

    def update_password(self, connection, password):
        """Let the user update the password"""
        try:
            tmp = {}
            with open(self.password_file, 'rb') as input:
                reader = csv.DictReader(input)
                for row in reader:
                    tmp[row['username']] = row['password']
            current_username = self.reverse_connections[connection]
            if current_username in self.loggedin_usernames:
                password = bcrypt_sha256.hash(password)
                tmp[current_username] = password
                conn = connect_db()
                cur = conn.cursor()
                cur.execute('SELECT id, password FROM `user` WHERE username=?', (current_username,))
                cur.execute('UPDATE `user` SET password=? WHERE username=?', (password, current_username))
                conn.commit()
                conn.close()
                with open(self.password_file, 'w') as output:
                    fieldnames = ['username', 'password']
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    for read in tmp.keys():
                        writer.writerow({'username': read, 'password': tmp[read]})
                return self.notify(current_username, "You have successfully upated your password.", connection)
        except:
            return ErrorMessage("[update password] You have not yet logged in. You cannot change your password.",
                                connection).render()

    def authenticate(self, username, password, connection):
        """Log in a user that's already registered"""
        # need to take care of chatroom, if the user is the admin, s/he is still the admin.
        if connection.getUserStatus():
            return ErrorMessage("You can only log in at a single time. You need to log off first.", connection).render()
        if username not in self.loggedin_usernames:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT id, password FROM `user` WHERE username=?', (username,))
            row = cur.fetchone()
            if row is not None:
                if bcrypt_sha256.verify(password, row[1]):
                    u = User(username, password, connection)
                    # Log in the user
                    self.loggedin_usernames.append(username)
                    self.users[username] = u
                    self.reverse_connections[connection] = username
                    self.connections[username] = connection
                    u.change_loginStatus()
                    # notify the user about successfully logging in
                    msg = username + " has logged in successfully."
                    self.notify(username, msg, connection)
                    return u
                else:
                    return ErrorMessage("Password incorrect.", connection).render()
            else:
                conn.commit()
                conn.close()
                ErrorMessage("No such user is currently registered.", connection).render()
        else:
            return ErrorMessage("User is already logged in.", connection).render()

    def notify(self, username, msg, connection):
        """Notify the user of a certain message"""
        connection.conn.sendall(msg)
        connection.conn.sendall("\n")
        return None

    # update Tuesday
    def upload_file(self, fromuser, target, file_name, connection):
        if target.startswith("#"):
            # print("I am in correct option")
            # To a channel
            if target in self.channels:
                chan = self.channels[target]
                if fromuser in chan.getUsers().keys():
                    if fromuser not in chan.getBannedUserDict().keys():
                        # print("I am here")
                        current_sender = chan.getUsers()[fromuser]  # why we have this? -- user object?
                        # update the current_sender's owning list
                        current_sender.file_owning(file_name)
                        # update the file information to channel
                        chan.file_getting(file_name)
                        # encrpyt the file here
                        enc_file_name = encrypt_file(KEY, file_name)
                        # here we need to def a function to send file to file server
                        exit_code = call("python3 post_file.py " + enc_file_name, shell=True)
                        # delete the file and encrpyted file on chat server
                        os.remove(file_name)
                        os.remove(enc_file_name)
                        conn = connect_db()
                        cur = conn.cursor()
                        file_user_update = ""
                        cur.execute('SELECT files FROM `user` WHERE username=?',
                                                    (fromuser,))
                        row_file_user = cur.fetchone()
                        if row_file_user[0] is not None:
                            file_user_update = row_file_user[0] + file_name + ','
                        else:
                            file_user_update = file_name + ','
                        cur.execute('UPDATE `user` SET files=? WHERE username=?', (file_user_update, fromuser))
                        file_channel_update = ""
                        cur.execute('SELECT filesList FROM `channel` WHERE channelname=?',
                                                       (target,))
                        row_file_channel = cur.fetchone()
                        if row_file_channel[0] is not None:
                            file_channel_update = row_file_channel[0] + file_name + ','
                        else:
                            file_channel_update = file_name + ','
                        cur.execute('UPDATE `channel` SET filesList=? WHERE channelname=?',
                                    (file_channel_update, target))
                        conn.commit()
                        conn.close()
                        # notify user you have sent successfully
                        self.notify(fromuser, "You have sent " + file_name + " successfully.", connection)
                    else:
                        os.remove(file_name)
                        return ErrorMessage(
                            "You cannot send file to this chat room " + target + " because you have been banned from this chat room.",
                            connection).render()
                else:
                    os.remove(file_name)
                    return ErrorMessage("You are not in this chat room " + target + ".", connection).render()
            else:
                os.remove(file_name)
                return ErrorMessage("No such channel exists.", connection).render()
        else:
            # To another user
            # Make sure user is logged in
            if target in self.loggedin_usernames:
                target_user = self.users[target]
                if fromuser not in target_user.getBlockedUsers():
                    current_sender = self.users[fromuser]
                    current_sender.file_owning(file_name)
                    # connection_of_target = self.connections[target]
                    target_user.file_getting(file_name)
                    # encrypt file here
                    enc_file_name = encrypt_file(KEY, file_name)
                    # send file to file server
                    exit_code = call("python3 post_file.py " + enc_file_name, shell=True)
                    # delete the file here
                    os.remove(file_name)
                    os.remove(enc_file_name)
                    self.notify(fromuser, "You have sent " + file_name + " successfully.", connection)
                else:
                    os.remove(file_name)
                    return self.notify(fromuser, "You are blocked by " + target + " .", connection)
            else:
                os.remove(file_name)
                return ErrorMessage("Target user is not logged in / does not exist", connection).render()

    def list_files(self, fromuser, target, connection):
        if target.startswith("#"):
            if target in self.channels:
                chan = self.channels[target]
                if fromuser in chan.getUsers().keys():
                    if fromuser not in chan.getBannedUserDict().keys():
                        # print("I am here")
                        self.notify(fromuser, target + "has these files: ", connection)
                        for file in chan.get_file_list:
                            self.notify(fromuser, file, connection)
                    else:
                        ErrorMessage(
                            "You cannot get file list from this chat room " + target + " because you have been banned from this chat room.",
                            connection).render()
                else:
                    return ErrorMessage("You are not in this chat room " + target + ".", connection).render()
            else:
                return ErrorMessage("No such channel exists.", connection).render()
        else:
            # user can only check the file they got
            if target == fromuser:
                me = self.users[target]
                self.notify(fromuser, target + "has these files: ", connection)
                for file in me.get_file_list:
                    self.notify(fromuser, file, connection)

            else:
                ErrorMessage("You can not get other users' file lists", connection)

    def update_file(self, fromuser, target, file_name, connection):
        current_sender = self.users[fromuser]
        if file_name in current_sender.owning_file_list:
            if target.startswith("#"):
                # print("I am in correct option")
                # To a channel
                if target in self.channels:
                    chan = self.channels[target]
                    if fromuser in chan.getUsers().keys():
                        if fromuser not in chan.getBannedUserDict().keys():
                            # encrpyt the file here
                            enc_file_name = encrypt_file(KEY, file_name)
                            # here we need to def a function to send file to file server
                            # do we need to delete the encrpyted file before we send it again? ******
                            exit_code = call("python3 post_file.py " + enc_file_name, shell=True)
                            # delete the file and encrpyted file on chat server
                            os.remove(file_name)
                            os.remove(enc_file_name)
                            # notify user you have sent successfully
                            self.notify(fromuser, "You have updated " + file_name + " successfully.", connection)
                        else:
                            os.remove(file_name)
                            return ErrorMessage(
                                "You cannot send file to this chat room " + target + " because you have been banned from this chat room.",
                                connection).render()
                    else:
                        os.remove(file_name)
                        return ErrorMessage("You are not in this chat room " + target + ".", connection).render()
                else:
                    os.remove(file_name)
                    return ErrorMessage("No such channel exists.", connection).render()
            else:
                # To another user
                # Make sure user is logged in
                if target in self.loggedin_usernames:
                    target_user = self.users[target]
                    if fromuser not in target_user.getBlockedUsers():
                        # no need to update information in state just need to send file
                        # encrypt file here
                        enc_file_name = encrypt_file(KEY, file_name)
                        # send file to file server
                        exit_code = call("python3 post_file.py " + enc_file_name, shell=True)
                        # delete the file here
                        os.remove(enc_file_name)
                        os.remove(file_name)
                        self.notify(fromuser, "You have updated " + file_name + " successfully.", connection)
                    else:
                        os.remove(file_name)
                        return self.notify(fromuser, "You are blocked by " + target + " .", connection)
                else:
                    os.remove(file_name)
                    return ErrorMessage("Target user is not logged in / does not exist", connection).render()
        else:
            os.remove(file_name)
            return ErrorMessage("You are not the owner of the file you want to update", connection).render()
            # we update the state and each user and channel

    def remove_file(self, fromuser, target, file_name, connection):
        current_sender = self.users[fromuser]
        enc_file_name = file_name + '.enc'
        if target.startswith("#"):
            # print("I am in correct option")
            # To a channel
            if target in self.channels:
                chan = self.channels[target]
                if (file_name in current_sender.owning_file_list) or fromuser == target.adminstration:
                    # update information in state
                    if fromuser == chan.administration:
                        for user in self.users.keys():
                            if file_name in self.users[user].owning_file_list:
                                self.users[user].owning_file_list.remove(file_name)
                                break
                    else:
                        current_sender.owning_file_list.remove(file_name)
                    target.get_file_list.remove(file_name)
                    # encrpyt the file here

                    # do we need to delete the encrpyted file before we send it again? ******
                    exit_code = call("python3 delete_file.py " + enc_file_name, shell=True)

                    # delete the file and encrpyted file on chat server
                    # os.remove(file_name)
                    # exit_code = call("python3 delete_file.py " + file_name, shell=True)
                    # notify user you have sent successfully
                    self.notify(fromuser, "You have deleted " + file_name + "from " + target + " successfully.",
                                connection)
                else:
                    return ErrorMessage("You are not the owner of the file you want to update", connection).render()
            else:
                return ErrorMessage("No such channel exists.", connection).render()
        else:
            # To another user
            # Make sure user is logged in
            if file_name in current_sender.owning_file_list:
                target_user = self.users[target]
                if fromuser not in target_user.getBlockedUsers():
                    current_sender.owning_file_list.remove(file_name)
                    target_user = self.users[target]
                    target_user.get_file_list.remove(file_name)
                    # encrypt file here

                    # send file to file server
                    exit_code = call("python3 delete_file.py " + enc_file_name, shell=True)
                    # delete the file here
                    # os.remove(file_name) #later we will send request to file server to delete the file there
                    # exit_code = call("python3 delete_file.py " + file_name, shell=True)
                    self.notify(fromuser, "You have deleted " + file_name + "from " + target + " successfully.",
                                connection)
                else:
                    return self.notify(fromuser, "You are blocked by " + target + " .", connection)
            else:
                return ErrorMessage("You are not the owner of the file you want to update", connection).render()

    def download_file(self, fromuser, target, file_name, connection):
        enc_file_name = file_name + '.enc'
        if target.startswith("#"):
            # print("I am in correct option")
            # To a channel
            if target in self.channels:
                chan = self.channels[target]
                if fromuser in chan.getUsers().keys():
                    if fromuser not in chan.getBannedUserDict().keys():
                        current_sender = chan.getUsers()[fromuser]  # why we have this? -- user object?
                        # send request to get file from file server
                        exit_code = call("python3 get_file.py " + enc_file_name, shell=True)
                        # decrypt the file here
                        tmp = decrypt_file(KEY, file_name)
                        # send file to user
                        sent_file_name, file_name_len, file_size, md5 = self.get_file_info(file_name)
                        file_head = struct.pack(HEAD_STRUCT, bytes(sent_file_name), file_name_len, file_size,
                                                bytes(md5))
                        print "file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size),
                                                                                        str(md5))
                        # try:
                        # tell server to ready for the file
                        connection.conn.sendall("downloading data now...\n")
                        time.sleep(.2)
                        connection.conn.send(file_head)  # send the head to tell chat server how much to recv
                        # time.sleep(.2) #rest to avoid race condition
                        sent_size = 0  # keep track of the how much we have sent

                        with open(file_name, 'r') as file:
                            while sent_size < file_size:
                                remained_size = file_size - sent_size
                                send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                                send_file = file.read(send_size)
                                sent_size += send_size
                                connection.conn.send(send_file)
                        # delete the file here
                        os.remove(enc_file_name)
                        os.remove(file_name)
                        self.notify(fromuser, "You have downloaded " + file_name + " successfully.", connection)
                    else:
                        return ErrorMessage(
                            "You cannot download files from this chat room " + target + " because you have been banned from this chat room.",
                            connection).render()
                else:
                    return ErrorMessage("You are not in this chat room " + target + ".", connection).render()
            else:
                return ErrorMessage("No such channel exists.", connection).render()
        else:
            # To another user
            # Make sure user is logged in
            target_user = self.users[target]
            if fromuser not in target_user.getBlockedUsers():
                current_sender = self.users[fromuser]
                if file_name in current_sender.get_file_list:
                    # send request to get file from file server
                    exit_code = call("python3 get_file.py " + enc_file_name, shell=True)
                    # decrypt the file here
                    tmp = decrypt_file(KEY, file_name)
                    # send file to user
                    sent_file_name, file_name_len, file_size, md5 = self.get_file_info(file_name)
                    print "file_name is {}, file_size is {}, md5_recv is {}".format(file_name, str(file_size), str(md5))
                    file_head = struct.pack(HEAD_STRUCT, bytes(sent_file_name), file_name_len, file_size, bytes(md5))
                    # print(str(file_head))
                    # print(len(file_head))
                    # try:
                    # tell server to ready for the file
                    padding = "downloading data now...\n"
                    connection.conn.sendall(padding)
                    time.sleep(.2)
                    connection.conn.sendall(file_head)  # send the head to tell chat server how much to recv
                    # time.sleep(.2) #rest to avoid race condition
                    sent_size = 0  # keep track of the how much we have sent

                    with open(sent_file_name, "r") as file:
                        # print ("open file shows: " + file.read())
                        while sent_size < file_size:
                            remained_size = file_size - sent_size
                            send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
                            send_file = file.read(send_size)
                            # print("file content is :" + str(send_file) + "   end of file content")
                            sent_size += send_size
                            connection.conn.sendall(send_file)
                    # delete the file here
                    os.remove(enc_file_name)
                    os.remove(file_name)
                    self.notify(fromuser, "You have downloaded " + file_name + " successfully.", connection)
                else:
                    return ErrorMessage("No such file sent to you, please check it again", connection).render()
            else:
                return self.notify(fromuser, "You are blocked by " + target + " .", connection)

    # helper to pack information into header
    def cal_md5(self, file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def get_file_info(self, file_path):
        file_name = os.path.basename(file_path)
        file_name_len = len(file_name)
        file_size = os.path.getsize(file_path)
        md5 = self.cal_md5(file_path)
        return file_name, file_name_len, file_size, md5

    # two public function to encrypt and decrypt


def encrypt_file(key, in_filename, chunksize=16):
    out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
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
