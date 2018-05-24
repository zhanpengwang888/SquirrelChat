"""
Our web server for squirrel chat 
"""
import os
import sqlite3
import sys
import random
import struct
import werkzeug
from passlib.hash import bcrypt_sha256
from subprocess import call
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
import ssl

from flask import Flask, redirect, jsonify, request, session, render_template, send_from_directory, flash,url_for
from jinja2 import Template, escape

app = Flask(__name__)
# jsglue = JSGlue()
# jsglue.init_app(app)
app.secret_key = 'shinba inu' # temporary secret key, we need to change it later.

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'shared_database.db')

ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'rtf', 'html', 'zip', 'mp3', 'wma', 'mpg',
                          'flv', 'avi', 'jpg', 'jpeg', 'png', 'gif'])
KEY = ""
with open("./server/key.txt", 'r') as file:
    KEY = file.read()

CERT = './cert.pem'
THEKEY = './key.pem'
ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain(CERT, THEKEY)

loggedin_users_list = []

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    # for each user
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32),
            channels TEXT,
            banned TEXT,
            blocked TEXT,
            adminsOfChannels TEXT,
            files TEXT
            )''')
    # for each channel
    cur.execute('''
            CREATE TABLE IF NOT EXISTS channel(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channelname VARCHAR(32),
            topic VARCHAR(32),
            user TEXT,
            banned_list TEXT,
            admin TEXT,
            filesList TEXT
            )''')
    # for log message
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel TEXT,
        user TEXT,
        content TEXT,
        FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
        )''')
    conn.commit()
    conn.close()

def init():
    create_tables()

# the code from Kris' app.py
def get_user_by_username_and_password(username, password):
    conn = connect_db()
    cur = conn.cursor()
    print(username)
    cur.execute('SELECT id, password FROM `user` WHERE username=?', (username,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if row is not None:
        if bcrypt_sha256.verify(password, row[1]):
            print(row)
            loggedin_users_list.append(username)
            return {'id': row[0], 'username': username} if row is not None else None
        else:
            flash('Incorrect Password.', 'error')
            return None
    else:
        message = "This user " + username + " does not exists."
        flash(message, 'error')
        return None

# login the user
def login_the_user(user):
    if user is not None:
        session['uid'] = user['id']
        return redirect('/channels')
    else:
        return redirect('/login')

# the codes from Kris'app
def create_user(username, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO `user` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (username, password, '', '', '', '','',))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row is not None else None

# our home page
@app.route('/')
def index():
    if 'username' in session:
        return render_template('chats.html') # need to change later
    return redirect('/login')

# the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if the flask gets a get request, go to login page
    if request.method == 'GET':
        return render_template('login.html')   
    # if the flask gets post request, try to log in the user
    elif request.method == 'POST':
        print("here!")
        username = request.form['username']
        password = request.form['password']
        if username not in loggedin_users_list:
            print("login method: ",username,password)
            user = get_user_by_username_and_password(username, password)
            return login_the_user(user)
        else:
            msg = username + ' has already logged in'
            flash(msg, 'error')
            return redirect('/login')

@app.route('/refresh/<channel_name>', methods=['GET'])
def refresh_web_page(channel_name):
    return url_for('chats', channel_name=channel_name)

@app.route('/chatroom/<channel_name>', methods=['GET'])
def chats(channel_name):
    if 'uid' in session:
        print("I get in!")
        #channel_name = "#" + channel_name
        print(channel_name)
        channel_name = '#' + channel_name
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username, channels, banned FROM `user` WHERE id=?', (session['uid'],)) # fetch the username
        row_username = cur.fetchone()
        if row_username is None:
            conn.commit()
            conn.close()
            flash('You have not logged in yet. Please log in.')
            return redirect('/login')
        username = row_username[0] # now we have the username
        cur.execute('SELECT admin, user, filesList, topic, banned_list FROM `channel` WHERE channelname=?', (channel_name,)) # fetch admin, users list, topic, banned list from the table channel.
        row_of_channel = cur.fetchone()
        if row_of_channel is None:
            conn.commit()
            conn.close()
            return redirect('/channels')
        isAdmin = False
        channels_list = row_username[1] # get the list of channels given by the user.
        # check if the user is one of the admins of this channel
        admin_list = row_of_channel[0]
        print('line 157', admin_list)
        users_list = row_of_channel[1]
        if users_list is not None and username not in users_list:
            print("line 153, it comes here to update the user list")
            users_list = users_list + username + ',' # add the current user into the user list
        elif users_list is None:
            users_list = username + ','
        cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (users_list, channel_name)) # update the user list in the table of channel
        
        if channels_list is not None and channel_name not in channels_list:
            channels_list = channels_list + channel_name
        elif channels_list is None:
            channels_list = channel_name
        print('line 164, ',channels_list)
        cur.execute('UPDATE `user` SET channels=? WHERE username=?', (channels_list, username)) # update the channel list given by the username
        print('line 159', users_list)
        list_of_file = row_of_channel[2]
        print('line 161', list_of_file)
        the_topic = row_of_channel[3]
        print('line 163', the_topic)
        banned_list = row_of_channel[4]
        print('line 165', banned_list)
        if username in admin_list:
            isAdmin = True
            conn.commit()
            conn.close()
            return render_template("chatroom.html", username=username, admin=isAdmin, users=users_list, files=list_of_file, channel_name=channel_name, channel_topic=the_topic)
        else:
            # else, check if this user gets banned from this channel
            if banned_list is not None:
                if username in banned_list:
                    users_list = users_list.replace(username + ',', '') # delete it from the users list
                    channels_list = channels_list.replace(channel_name, '') # delete the channel from the channel list of the user.
                    users_get_banned_list = row_username[2]
                    if users_get_banned_list is not None:
                        users_get_banned_list += channel_name
                    else:
                        users_get_banned_list = channel_name
                    cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (users_list, channel_name))
                    cur.execute('UPDATE `user` SET channels=? WHERE username=?', (channels_list, username))
                    conn.commit()
                    conn.close()
                    return redirect('/channels')
                else:
                    conn.commit()
                    conn.close()
                    return render_template("chatroom.html", username=username, admin=isAdmin, users=users_list, files=list_of_file, channel_name=channel_name, channel_topic=the_topic)
            else:
                conn.commit()
                conn.close()
                return render_template("chatroom.html", username=username, admin=isAdmin, users=users_list, files=list_of_file, channel_name=channel_name, channel_topic=the_topic)
    else:
        flash('You have not logged in yet. Please log in.')
        return redirect('/login')

# the sign up page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        print("it comes here.")
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM `user` WHERE username=?', (username,))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        if row is not None:
            flash('Error: trying to register an account that already exists.', 'error')
            return redirect('/create_account')
        print (username, password)
        count_for_period = 0
        for i in range(len(username)):
            if username[i] in "&=<>+-?" or count_for_period >= 2:
                flash('Illegal username.', 'error')
                return redirect('/login')
            elif username[i] == '.':
                count_for_period += 1
                
        encrypted_password = bcrypt_sha256.hash(password)
        user = create_user(username, encrypted_password)
        flash('You have registered successfully', 'info')
        return login_the_user(user)


@app.route('/change_pwd', methods=['GET','POST'])
def change_password():
    if request.method == 'GET':
        return render_template('change_pwd.html')
    # if user is not in session, redirect to login page
    elif request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM `user` WHERE username=?', (username,))
        row = cur.fetchone()
        # if username is not in database, redirect to login page
        if row is None:
            flash('This user does not exist. Please check again.','error')
            return redirect('/login')
        else:
            message = ""
            if bcrypt_sha256.verify(old_password, row[1]):
                encrypted_password = bcrypt_sha256.hash(new_password)
                cur.execute('UPDATE `user` SET password=? WHERE username=?', (encrypted_password, username))
                message = "You have successfully changed your password."
                #print ("I am here")
            else:
                message = "You fail to change your password."
            conn.commit()
            conn.close()
            flash(message, 'info')
            return redirect('/login')


@app.route('/ban_user/<channel>/<username>/<banned_username>', methods=['GET'])
def ban_user(channel, username, banned_username):
    old_channel = channel #need to used in url
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT user, banned_list, admin FROM `channel` WHERE channelname=?', (channel,))
    row_channel = cur.fetchone()
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    cur.execute('SELECT id, blocked, channels FROM `user` WHERE username=?', (banned_username,))
    row_user2 = cur.fetchone()
    if row_user is not None:
        if row_user2 is not None:
            if row_channel is None:
                message = "Channel does not exist. Try again!"
                conn.commit()
                conn.close()
                flash(message, 'info')
                #return redirect('/chatroom')
                return url_for('chats', channel_name=old_channel)
            else:
                user_in_channel = row_channel[0].split(',')
                if banned_username not in user_in_channel:
                    message = "{} is not in channel {}".format(banned_username, channel)
                    conn.commit()
                    conn.close()
                    flash(message, 'info')
                    #return redirect('/chatroom')
                    return url_for('chats', channel_name=old_channel)
                else:
                    admin_list = row_channel[2].split(',')
                    if username not in admin_list:
                        message = "You're not an admin in channel {}".format(channel)
                        conn.commit()
                        conn.close()
                        flash(message, 'info')
                        #return redirect('/chatroom')
                        return url_for('chats', channel_name=old_channel)
                    else:
                        banned_username_list = row_channel[1].split(',')
                        if banned_username in banned_username_list:
                            message = "You cannot ban {} twice.".format(banned_username)
                            conn.commit()
                            conn.close()
                            flash(message, 'info')
                            #return redirect('/chatroom')
                            return url_for('chats', channel_name=old_channel)
                        else:
                            user_list = row_channel[0]
                            user_list = user_list.replace(banned_username + ',','')
                            cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (user_list, channel,))
                            banned_username_list = row_channel[1]
                            banned_username_list += banned_username + ','
                            cur.execute('UPDATE `channel` SET banned_list=? WHERE channelname=?',
                                        (banned_username_list, channel))
                            channels_list_of_banned_user = row_user2[2]
                            channels_list_of_banned_user = channels_list_of_banned_user.replace(channel, '')
                            cur.execute('UPDATE `user` SET channels=? WHERE username=?',
                                        (channels_list_of_banned_user, banned_username))
                            cur.execute('SELECT id, banned FROM `user` WHERE username=?', (banned_username,))
                            row_banned_user = cur.fetchone()
                            banned_channel_list = row_banned_user[1]
                            banned_channel_list += channel
                            cur.execute('UPDATE `user` SET banned=? WHERE username=?',
                                        (banned_channel_list, banned_username))
                            conn.commit()
                            conn.close()
                            message = "You successfully banned {} from channel {}.".format(banned_username, channel)
                            flash(message, 'info')
                            #return redirect('/chatroom')
                            return url_for('chats', channel_name=old_channel)
        else:
            conn.commit()
            conn.close()
            message = "{} does not exist! Try again!".format(banned_username)
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)
    else:
        conn.commit()
        conn.close()
        message = "{} does not exist! Log in again!".format(username)
        flash(message, 'info')
        #return redirect('/login')
        return url_for('login')

@app.route('/unban_user/<channel>/<username>/<banned_username>', methods=['GET'])
def unban_user(channel, username, banned_username):
    old_channel = channel #need to used in url
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT user, banned_list, admin FROM `channel` WHERE channelname=?', (channel,))
    row_channel = cur.fetchone()
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (banned_username,))
    row_user2 = cur.fetchone()
    if row_user is not None:
        if row_user2 is not None:
            if row_channel is None:
                message = "Channel does not exist. Try again!"
                conn.commit()
                conn.close()
                flash(message, 'info')
                #return redirect('/chatroom')
                return url_for('chats', channel_name=old_channel)
            else:
                admin_list = row_channel[2].split(',')
                if username not in admin_list:
                    message = "You're not an admin in channel {}".format(channel)
                    conn.commit()
                    conn.close()
                    flash(message, 'info')
                    #return redirect('/chatroom')
                    return url_for('chats', channel_name=old_channel)
                else:
                    banned_username_list = row_channel[1].split(',')
                    if banned_username in banned_username_list:
                        banned_list = row_channel[1]
                        banned_list = banned_list.replace(banned_username + ',', '')
                        cur.execute('UPDATE `channel` SET banned_list=? WHERE channelname=?', (banned_list, channel))
                        cur.execute('SELECT id, banned FROM `user` WHERE username=?', (banned_username,))
                        row_banned_user = cur.fetchone()
                        banned_channel_list = row_banned_user[1]
                        banned_channel_list = banned_channel_list.replace(channel, '')
                        cur.execute('UPDATE `user` SET banned=? WHERE username=?',
                                    (banned_channel_list, banned_username))
                        conn.commit()
                        conn.close()
                        message = "You successfully unbanned {} from channel {}.".format(banned_username, channel)
                        flash(message, 'info')
                        #return redirect('/chatroom')
                        return url_for('chats', channel_name=old_channel)
                    else:
                        message = "You cannot unban a user that hasn't been blocked."
                        conn.commit()
                        conn.close()
                        flash(message, 'info')
                        #return redirect('/chatroom')
                        return url_for('chats', channel_name=old_channel)
        else:
            conn.commit()
            conn.close()
            message = "{} does not exist! Try again!".format(banned_username)
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)
    else:
        conn.commit()
        conn.close()
        message = "{} does not exist! Log in again!".format(username)
        flash(message, 'info')
        #return redirect('/login')
        return url_for('login')


@app.route('/block_user/<channel>/<username>/<blocked_username>', methods=['GET'])
def block_user(channel,username, blocked_username):
    old_channel = channel #need to used in url
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    blocked_list = row_user[1].split(',')
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (blocked_username,))
    row_banned_user = cur.fetchone()
    if row_user is None:
        conn.commit()
        conn.close()
        message = "{} does not exist! Log in again!".format(username)
        flash(message, 'info')
        #return redirect('/login')
        return url_for('login')

    elif row_banned_user is None:
        conn.commit()
        conn.close()
        message = "{} does not exist! Try again!".format(blocked_username)
        flash(message, 'info')
        #return redirect('/chatroom')
        return url_for('chats', channel_name=old_channel)
    else:
        if blocked_username in blocked_list:
            conn.commit()
            conn.close()
            message = "You cannot block {} twice".format(blocked_username)
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)
        else:
            to_update_user = row_user[1] + blocked_username + ','
            cur.execute('UPDATE `user` SET blocked=? WHERE username=?', (to_update_user, username))
            conn.commit()
            conn.close()
            message = "You have successfully blocked user {}!".format(blocked_username)
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)

@app.route('/unblock_user/<channel>/<username>/<blocked_username>', methods=['GET'])
def unblock_user(channel, username, blocked_username):
    old_channel = channel #need to used in url
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    blocked_list = row_user[1].split(',')
    cur.execute('SELECT id, blocked FROM `user` WHERE username=?', (blocked_username,))
    row_banned_user = cur.fetchone()
    if row_user is None:
        conn.commit()
        conn.close()
        message = "{} does not exist! Log in again!".format(username)
        flash(message, 'info')
        #return redirect('/login')
        return url_for('login')
    elif row_banned_user is None:
        conn.commit()
        conn.close()
        message = "{} does not exist! Try again!".format(blocked_username)
        flash(message, 'info')
        #return redirect('/chatroom')
        return url_for('chats', channel_name=old_channel)
    else:
        if blocked_username in blocked_list:
            to_update_user = row_user[1]
            to_update_user = to_update_user.replace(blocked_username + ',', '')
            cur.execute('UPDATE `user` SET blocked=? WHERE username=?', (to_update_user, username))
            conn.commit()
            conn.close()
            message = "You have successfully unblock user {}!".format(blocked_username)
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)
        else:
            conn.commit()
            conn.close()
            message = "You cannot unblock a user that hasn't been blocked!"
            flash(message, 'info')
            #return redirect('/chatroom')
            return url_for('chats', channel_name=old_channel)

@app.route('/channels', methods=['GET'])
def go_into_channel():
    if 'uid' in session:
        print("[go_into_channel] It comes here.")
        print(session['uid'])
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username, banned FROM `user` WHERE id=?', (session['uid'],)) # fetch the username
        row_user = cur.fetchone()
        if row_user is not None:
            username = row_user[0]
            print('line 402', username)
            conn.commit()
            conn.close()
            return render_template('channels.html', username=username)
        else:
            flash("You have not logged in yet. Please log in first", 'error')
            return redirect('/login')
    else:
        flash("You have not logged in yet. Please log in first", 'error')
        return redirect('/login')


@app.route('/get_channel_list', methods=['GET'])
def get_channel_list():
    if 'uid' in session:
        print("[get_channel_list] It comes here.")
        print(session['uid'])
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username, banned FROM `user` WHERE id=?', (session['uid'],)) # fetch the username
        row_user = cur.fetchone()
        if row_user is not None:
            username = row_user[0]
            print('line 419', username)
            channels_that_banned_user = row_user[1] # a list of channels where the user gets banned
            channel_list = []
            topics = []
            adminsOfChannels = []
            cur.execute('SELECT channelname, topic, admin FROM `channel`')
            all_of_them = cur.fetchall()
            all_channels_list = []
            all_topics_list = []
            all_admins_list = []
            print('line 429', all_of_them)
            for channel in all_of_them:
                all_channels_list.append(channel[0])
            print('line 432', all_channels_list)
            for topic in all_of_them:
                all_topics_list.append(topic[1])
            print('line 435', all_topics_list)
            for admin in all_of_them:
                all_admins_list.append(admin[2])
            print('line 438', all_admins_list)
            # filter out the channels that the user get banned from
            if all_channels_list == None:
                conn.commit()
                conn.close()
                return jsonify({'channel_list': None, 'topic': None, 'admin': None})
            new_channels_that_banned_user = []
            if channels_that_banned_user != None:
                channels_that_banned_user = channels_that_banned_user.split('#')
                for channel in channels_that_banned_user:
                    temp = '#'+ channel
                    new_channels_that_banned_user.append(temp)
            for index in range(len(all_channels_list)):
                channel = all_channels_list[index]
                if channel not in new_channels_that_banned_user:
                    channel_list.append(channel)
                    topics.append(werkzeug.unescape(all_topics_list[index]))
                    adminsOfChannels.append(all_admins_list[index])
            conn.commit()
            conn.close()
            print('line 458', channel_list)
            print('line 459', topics)
            print('line 460', adminsOfChannels)
            return jsonify({'channel_list': channel_list, 'topic': topics, 'admin': adminsOfChannels})
        else:
            conn.commit()
            conn.close()
            flash("You have not logged in yet. Please log in first", 'error')
            return redirect('/login')
    else:
        flash("You have not logged in yet. Please log in first", 'error')
        return redirect('/login')


@app.route('/get_chats/<channel_name>', methods=['GET'])
def display_chats(channel_name):
    if 'uid' in session:
        print('[display chat] it comes here')
        channel_name = '#' + channel_name
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username, blocked FROM `user` WHERE id=?', (session['uid'],)) # fetch the username
        row_user = cur.fetchone()
        if row_user is None:
            conn.commit()
            conn.close()
            flash("You have not logged in yet. Please log in first", 'error')
            return redirect('/login')
        username = row_user[0] # get the username
        blocked_user_list = row_user[1] # get the blocked list

        # start the decryption procedure
        key = ""
        with open('./server/logKey.txt', 'rb') as logkey:
            key = logkey.read()
        cipher = Fernet(key)

        cur.execute('SELECT channel, user, content FROM `chats`') # fetch the channel, user, and content from db
        row_chat = cur.fetchall() # a list of tuples, i.e. [(channel, user, content)]
        if row_chat is None:
            conn.commit()
            conn.close()
            return redirect('/channels')
        users_list_from_chat = []
        contents_list_from_chat = []
        # iterate through each entry of the chats table
        for entry in row_chat:
            channel = entry[0]
            user = entry[1]
            content = entry[2]
            decrypted_content = ""
            if channel == channel_name:
                if user not in blocked_user_list:
                    users_list_from_chat.append(escape(user))
                    decrypted_content = cipher.decrypt(str.encode(content)).decode()
                    contents_list_from_chat.append(escape(decrypted_content))
        conn.commit()
        conn.close()
        return jsonify({'users':users_list_from_chat, 'contents':contents_list_from_chat})
    else:
        flash("You have not logged in yet. Please log in first", 'error')
        return redirect('/login')


@app.route('/channels', methods=['POST'])
def create_channels():
    new_channel = request.json['name']
    new_topic = request.json['topic']
    new_topic = escape(new_topic)
    new_admin = request.json['admin']
    user_name = new_admin
    new_admin += ','
    print("Test for creating a channel: ",new_channel, new_topic, new_admin)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT channelname FROM `channel` WHERE channelname=?', (new_channel,))
    row = cur.fetchone()
    print("line 409",row)
    # check if the channel has already existed, if not, create one.
    if row is not None:
        message = "This channel " + new_channel + " has already existed."
        flash(message, 'error')
        conn.commit()
        conn.close()
        return redirect('/channels')
    else:
        # channelname, topic, users, banned_list, admin, fileList
        userlist = new_admin
        count_for_period = 0
        for i in range(len(new_channel)):
            if new_channel[i] in "&=<>+-?" or count_for_period >= 2:
                flash('Illegal channels.', 'error')
                return redirect('/channels')
            elif new_channel[i] == '.':
                count_for_period += 1
        
        cur.execute('INSERT INTO `channel` VALUES(NULL,?,?,?, ?, ?, ?);', (new_channel, new_topic, userlist,'', new_admin,''))
        cur.execute('SELECT channels FROM `user` WHERE username=?', (user_name,)) # fetch the list of channels given the user
        row = cur.fetchone()
        #print(row, row[0])
        channel_list = ""
        if row is not None and row[0] != None:
            channel_list = row[0] + new_channel # append the channel to the channel list
        else:
            channel_list = new_channel
        cur.execute('UPDATE `user` SET channels=? WHERE username=?', (channel_list, user_name)) # update the channel list given the username
        cur.execute('UPDATE `user` SET adminsOfChannels=? WHERE username=?', (channel_list, user_name)) # update the channel list which he is the admin given the username
        conn.commit()
        conn.close()
    return jsonify('success')


@app.route('/leave/<channel>/<username>')
def leave_channel(channel, username):
    #add # to channel, can't get from url
    channel = "#" + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, channels FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    cur.execute('SELECT id, user FROM `channel` WHERE channelname=?', (channel,))
    row_channel = cur.fetchone()
    if row_user is None or row_channel is None:
        conn.commit()
        conn.close()
        message = "User or channel doesn't exist"
        flash(message, 'info')
        #return redirect('/login')
        return url_for('login')
    else:
        user_update = row_user[1] # get the channel list according to the username from db
        if row_user[1] is not None and channel in row_user[1]:
            user_update = user_update.replace(channel, "")
        else:
            conn.commit()
            conn.close()
            print('line 617 it comes here')
            message = "You are not in channel {}".format(channel)
            flash(message, 'info')
            #return redirect('/login')
            return url_for('go_into_channel')
        cur.execute('UPDATE `user` SET channels=? WHERE username=?', (user_update, username))
        channel_update = row_channel[1]
        if row_channel[1] is not None and username in row_channel[1]:
            channel_update = channel_update.replace(username + ',', "")
        else:
            conn.commit()
            conn.close()
            print('line 629 it comes here')
            message = "You are not in channel {}".format(channel)
            flash(message, 'info')
            # return redirect('login')
            return url_for('go_into_channel')
        cur.execute('UPDATE `channel` SET user=? WHERE channelname=?', (channel_update, channel))
        conn.commit()
        conn.close()
        message = "You left channel {}". format(channel)
        flash(message, 'info')
        # return redirect('/channels')
        return url_for('go_into_channel')


@app.route('/upload_file/<channel>', methods=['GET', 'POST'])
def upload_file(channel):
    url_channel = channel
    channel = '#' + channel
    f = request.files['myfile']
    enc_file_name = f.filename + '.enc'
    print(f.filename)
    if f and allowed_file(f.filename):
        f.save(werkzeug.utils.secure_filename(f.filename))
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT filesList FROM `channel` WHERE channelname=?', (channel,))
        row_channel = cur.fetchone()
        file_to_update_channel = ""
        if row_channel[0] is not None:
            file_to_update_channel = row_channel[0] + ',' + f.filename + ','
            cur.execute('UPDATE `channel` SET filesList=? WHERE channelname=?', (file_to_update_channel, channel))
        else:
            file_to_update_channel = ',' + f.filename + ','
            cur.execute('UPDATE `channel` SET filesList=? WHERE channelname=?', (file_to_update_channel, channel))
        conn.commit()
        conn.close()
        exit_code = call("python2.7 encrypt.py " + f.filename, shell=True)
        exit_code = call("python3 ./server/post_file.py " + enc_file_name, shell=True)
        os.remove(f.filename)
        os.remove(enc_file_name)
    return redirect(url_for('chats', channel_name=url_channel))


@app.route('/download_file/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    enc_file_name = filename + '.enc'
    exit_code = call("python3 ./server/get_file.py " + enc_file_name, shell=True)
    exit_code = call("python2.7 decrypt.py " + filename, shell=True)
    os.remove(enc_file_name)
    return send_from_directory(app.root_path, filename, as_attachment=True)


@app.route('/clean/<filename>', methods=['GET', 'POST'])
def clean_file(filename):
    os.remove(filename)
    return "success"



@app.route('/change_topic/<channel>/<new_topic>', methods=['GET', 'POST'])
def change_topic(channel, new_topic):
    old_channel = channel
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT topic FROM `channel` WHERE channelname=?', (channel,))
    row_channel = cur.fetchone()
    if row_channel is not None:
        cur.execute('UPDATE  `channel` SET topic=? WHERE channelname=?', (new_topic, channel))
    conn.commit()
    conn.close()
    return url_for('chats', channel_name=old_channel)


@app.route('/set_admin/<channel>/<username>/<adminned>', methods=['GET'])
def set_admin(channel, username, adminned):
    url_channel = channel
    channel = '#' + channel
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT adminsOfChannels FROM `user` WHERE username=?', (username,))
    row_user = cur.fetchone()
    cur.execute('SELECT admin FROM `channel` WHERE channelname=?', (channel,))
    row_channel = cur.fetchone()
    cur.execute('SELECT adminsOfChannels FROM `user` WHERE username=?', (adminned,))
    row_user2 = cur.fetchone()
    if row_user is None and channel not in row_user[0]:
        conn.commit()
        conn.close()
        message = "User {} does not exist or is not the admin of channel {}. Try again!".format(username, channel)
    elif row_channel is None and username not in row_channel[0]:
        conn.commit()
        conn.close()
        message = "Channel {} does not exist or user {} is not the admin. Try again!".format(channel, username)
    elif row_user2 is None and channel in row_user2[0]:
        conn.commit()
        conn.close()
        message = "User {} does not exist or is already the admin of channel {}. Try again!".format(adminned, channel)
    else:
        to_be_update_user = ""
        if row_user2[0] is None:
            to_be_update_user = channel
        else:
            to_be_update_user = row_user2[0] + channel
        to_be_update_channel = row_channel[0] + adminned + ','
        cur.execute('UPDATE `user` SET adminsOfChannels=? WHERE username=?', (to_be_update_user, adminned))
        cur.execute('UPDATE `channel` SET admin=? WHERE channelname=?', (to_be_update_channel, channel))
        conn.commit()
        conn.close()
        message = "You've successfully added user {} as an admin of channel {}".format(adminned, channel)
    flash(message, "info")
    return url_for('chats', channel_name=url_channel)


# the log out
@app.route('/logout')
def logout():
    # close the client socket and pop out the session id
    if 'uid' in session:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT username FROM `user` WHERE id=?', (session['uid'],)) # fetch the username
        row_user = cur.fetchone()
        username = row_user[0]
        loggedin_users_list.remove(username)
        session.pop('uid', None)
        conn.commit()
        conn.close()
        flash('You have successfully logged out.', 'info')
    return redirect('/login')

# Static files
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/CSS/<path:path>')
def serve_css(path):
    return send_from_directory('CSS', path)

@app.route('/images/<path:path>')
def serve_images(path):
    return send_from_directory('images', path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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


if len(sys.argv) > 1 and sys.argv[1] == "init":
    init()
    exit(0)

if __name__ == '__main__':
    #app.run(threaded=True, debug=True, port=8000)
    app.run(threaded=True, debug=True, port=8000, ssl_context=ctx)