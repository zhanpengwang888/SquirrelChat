from connection import *
from socket import *
from state import *
import ssl
import sys
CERT, KEY = './cert.pem', './key.pem' # part 1

DATABASE_PATH = os.path.join(os.path.dirname(__file__), './../shared_database.db')

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

class Server:
    """Toplevel server implementation"""
    
    def run(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((gethostbyname("localhost"),self.port))
        s.listen(5)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH) # part 1
        context.load_cert_chain(certfile=CERT, keyfile=KEY) # part 1
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 # part 1
        context.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH') # part 1
        while 1:
            #try:
            print("Waiting for new connections..")
            (client,address) = s.accept()
            client = context.wrap_socket(client, server_side=True) # part 1
            connection = Connection(client,self.state)
            print("Running thread for connection..")
            connection.start()
            #except:
                #pass

    def __init__(self,port, password_file):
        self.port = port
        self.state = State(password_file)
        self.passwordDatabase = password_file

if len(sys.argv) != 2:
    raise Exception("It needs to have a password database file.")
elif sys.argv[1].endswith('.csv'):
    # Main code entry: build a server and start it
    s = Server(4000, sys.argv[1])
    s.run()
elif sys.argv[1] == 'init':
    init()
else:
    raise Exception("Invalid password database file. It should be .csv file")
