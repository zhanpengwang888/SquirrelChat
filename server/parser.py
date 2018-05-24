from messages import *

class Parser():
    """Parser for messages sent via the SquirrelChat protocol"""
    def __init__(self):
        self.current_input = ""

    # Parse a simple packet
    def parse_packet(self,data, connection):
        #string = data.decode("utf-8")
        string = data
        split = string.split()
        if split[0] == "authenticate":
            if len(split) == 3:
                return AuthenticateMessage(split[1],split[2], connection)
            else:
                return ErrorMessage("Error: authenticate needs to have exactly 2 arguments, username and password.", connection)
        elif split[0] == "register":
            if len(split) == 3:
                return RegisterMessage(split[1],split[2],connection)
            else:
                return ErrorMessage("Error: register needs to have exactly 2 arguments, username and password.", connection)
        elif split[0] == "chat":
            msg = string.split(' ', 2)
            if len(split) >= 3:
                return ChatMessage(msg[1],msg[2],connection)
            else:
                return ErrorMessage("Error: chat needs to have exactly 2 arguments, username or channel, and message.", connection)
        elif split[0] == "join":
            if len(split) == 2:
                if split[1][0] == "#":
                    return JoinMessage(split[1],connection)
                else:
                    return ErrorMessage("Invalid chat room name.", connection)
            else:
                return ErrorMessage("Error: join needs to have exactly 1 argument, valid chat room name.", connection)
        elif split[0] == "update_pw":
            if len(split) == 2:
                return UpdatePasswordMessage(split[1], connection)
            else:
                return ErrorMessage("Error: updatePassword needs to have exactly 1 argument, valid password.", connection)
        elif split[0] == "chatfrom":
            if len(split) >= 4:
                if split[1][0] != "#":
                    return ChatFromMessage(split[1], split[2], split[3])
                else:
                    return ErrorMessage("Invalid chat room name.", connection)
            else:
                return ErrorMessage("Error: chatfrom needs to have exactly 3 arguments, sender, chat room or receiver, and message .", connection)
        elif split[0] == "gettopic":
            if len(split) == 2:
                if split[1][0] == "#":
                    return GetTopicMessage(split[1],connection)
                else:
                    return ErrorMessage("Invalid chat room name.", connection)
            else:
                return ErrorMessage("Error: gettopic needs to have exactly 1 argument, valid chat room name.", connection)
        elif split[0] == "topic":
            if len(split) >= 3:
                return TopicMessage(split[1], split[2], connection)
            else:
                return ErrorMessage("Error: topic needs to have exactly 2 arguments, valid chat room name and topic.", connection)
        elif split[0] == "settopic":
            msg = string.split(' ', 2)
            if len(split) >= 3:
                if split[1][0] == "#":
                    return SetTopicMessage(msg[1], msg[2],connection)
                else:
                    return ErrorMessage("Invalid chat room name.", connection)
            else:
                return ErrorMessage("Error: settopic needs to have exactly 2 arguments, valid chat room name and topic.", connection)
        elif split[0] == "leave":
            if len(split) == 2:
                if split[1][0] == "#":
                    return LeaveMessage(split[1],connection)
                else:
                    return ErrorMessage("Invalid chat room name.", connection)
            else:
                return ErrorMessage("Error: leave needs to have exactly 1 argument, chat room name.", connection)
        elif split[0] == "ban":
            if len(split) == 3:
                if split[1][0] == "#" and split[2][0] != "#":
                    return BanMessage(split[1], split[2], connection)
                else:
                    return ErrorMessage("Invalid chat room name or invalid user name.", connection)
            else:
                return ErrorMessage("Error: ban needs to have exactly 2 arguments, valid chat room name and banned user.", connection)
        elif split[0] == "unban":
            if len(split) == 3:
                if split[1][0] == "#" and split[2][0] != "#":
                    return UnbanMessage(split[1], split[2], connection)
                else:
                    return ErrorMessage("Invalid chat room name or invalid user name.", connection)
            else:
                return ErrorMessage("Error: unban needs to have exactly 2 arguments, valid chat room name and banned user.", connection)
        elif split[0] == "block":
            if len(split) == 2:
                if split[1][0] != "#":
                    return BlockMessage(split[1], connection)
                else:
                    return ErrorMessage("Invalid user name.", connection)
            else:
                return ErrorMessage("Error: block needs to have exactly 1 argument, blocked user.", connection)
        elif split[0] == "unblock":
            if len(split) == 2:
                if split[1][0] != "#":
                    return UnblockMessage(split[1], connection)
                else:
                    return ErrorMessage("Invalid user name.", connection)
            else:
                return ErrorMessage("Error: unblock needs to have exactly 1 argument, blocked user.", connection)
        elif split[0] == "logout":
            if len(split) == 1:
                return LogoffMessage(connection)
            else:
                return ErrorMessage("Error: logout accepts no argument.", connection)
        elif split[0] == "exit":
            if len(split) == 1:
                return ExitMessage(connection)
            else:
                return ErrorMessage("Error: exit accepts no argument.", connection)
        #update wed
        elif split[0] == "upload":
            if len(split) == 2:
                return UploadMessage(split[1],connection)
            else:
                return ErrorMessage("Error: upload accepts 2 arguments.", connection)
        elif split[0] == "getfiles":
            if len(split) == 2:
                return ListfilesMessage(split[1],connection)
            else:
                return ErrorMessage("Error: getfiles accepts 2 arguments.", connection)
        elif split[0] == "update":
            if len(split) == 2:
                return UpdateMessage(split[1],connection)
            else:
                return ErrorMessage("Error: update accepts 2 arguments.", connection)  
        elif split[0] == "remove":
            if len(split) == 3:
                return RemoveMessage(split[1],split[2],connection)
            else:
                return ErrorMessage("Error: remove accepts 3 arguments.", connection) 
        elif split[0] == "download":
            if len(split) == 3:
                return DownloadMessage(split[1],split[2],connection)
            else:
                return ErrorMessage("Error: download accepts 3 arguments.", connection)
        elif split[0] == "exchange_key":   # from a to b 
            msg = string.split(' ', 2)
            if split[1][0] != "#":
                return KeyexchangeMessage(msg[1], msg[2], connection)
            else:
                return ErrorMessage("Invalid user name.", connection)
        elif split[0] == "exchange_key_the_other_side":   # from b to a
            msg = string.split(' ', 2)
            if split[1][0] != "#":
                return KeyexchangeTheOtherSideMessage(msg[1], msg[2], connection)
            else:
                return ErrorMessage("Invalid user name.", connection)              
        else:
            return ErrorMessage(split[0]+ " is not supported", connection)
