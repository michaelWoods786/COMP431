###################################
#             COMP 431            #
#        FTP Client Program       #
#           Starter Code          #
###################################

import sys
import os
import socket
from socket import *
import time
import re
# Define dictionary of useful ASCII codes
# Use ord(char) to get decimal ascii code for char
ascii_codes = {
    "A": ord("A"), "Z": ord("Z"), 
    "a": ord("a"), "z": ord("z"), 
    "0": ord("0"), "9": ord("9"),
    "min_ascii_val": 0, "max_ascii_val": 127}

##############################################################################################
#                                                                                            # 
#     This function is intended to manage the command processing loop.                       #
#     The general idea is to loop over the input stream, identify which command              #
#     was entered, and then delegate the command-processing to the appropriate function.     #
#                                                                                            #
##############################################################################################
def formatStr(myStr):
    myStr.strip()
    splitted = myStr.split(" ", 1)
    myStr = f"FTP reply {splitted[0]} accepted. Text is: {splitted[1]}"
    sys.stdout.write(myStr + "\r\n") 


#TODO: make changes here if you have to
def initialize_client_ip():
      
    return gethostbyname(gethostname())  
        

def create_control_connection(server_host, server_port):
        ftp_control_connection = None
        ftp_control_connection = socket(AF_INET, SOCK_STREAM)
        ftp_control_connection.connect((server_host, int(server_port)))

        server_response = ftp_control_connection.recv(1024).decode()
        formatStr(server_response.strip())

        return ftp_control_connection
      
                

        
regMatchGet = r"^GET\s(.+)\r?\n$"
regMatchCon = r"^CONNECT\s+([a-zA-Z0-9.-]+)\s+(\d{1,5})\r?\n$"

client_ip = None
connection_active = False
numCopied =1
def read_commands():
    welcoming_port = 0
    global client_ip
    connection_active = False
    # Initially, only the CONNECT command is valid
    # Commands are case-sensitive
    #print("IN READ_Commands")
    expected_commands = ["CONNECT", "GET", "QUIT"]

    # Initial port number for a “welcoming” socket 
    welcoming_port = int(sys.argv[1])                     # sys.argv[0] is the filename
    global numCopied
    hostName = ""
    ftp_control_connection = None
    quit = False
    #print("at the top again")
 
    for command in sys.stdin:
    # Echo command exactly as it was input

        #print("this is the command:" + str(command))
        sys.stdout.write(command) 

       
        tokens = command.split()
        #print("these are the tokens:" + str(tokens))
        if len(tokens) > 0 and tokens[0] in expected_commands:
           # print("entered the parser") 
            tokenStuff = "".join(tokens)
            if "CONNECT" in tokens[0]:
                #sys.stdout.write("CONNECT")
      
                try:
                    (response, welcoming_port, hostName) = parse_connect(command)                     
                    print(response)
                    if ftp_control_connection is not None:
                        ftp_control_connection.close()
                                     
                    ftp_control_connection = create_control_connection(hostName, str(welcoming_port))  
                    process_connect(ftp_control_connection) 
                    connection_active = True
                except Exception as e:
                    print("CONNECT failed") 
                    
            elif "GET" in tokens[0]: 
                if (connection_active):    
                    get_command, filePath = parse_get(command)
                    #print("this is the get_command:" + str(get_command)) 
                    if "ERROR" in get_command:
                        print(get_command)

                    else:
                    
                    
                        print(get_command)
                        welcoming_port= str(int(welcoming_port))
                        check = process_get(ftp_control_connection, filePath, int(welcoming_port) + 1, numCopied)
                        welcoming_port = str(int(welcoming_port)+1)
                        numCopied += check
                        #print("Amount of files copied:" + str(numCopied-1))
                
                else:
                    print("ERROR -- Command Unexpected/Unknown")
                   


            elif "QUIT" in tokens[0]:
                if (connection_active):
                    print(parse_quit(command))
                    quit = process_quit(ftp_control_connection)
                    if quit:
                        connection_active = False
                    
                else:
                     print("ERROR -- Command Unexpected/Unknown")
                                  
        else:
            print("ERROR -- Command Unexpected/Unknown")
     

##############################################################################################
#                                                                                            # 
#     This function is intended to handle processing valid CONNECT commands.                 #
#     This includes generating the four-command sequence to send to the server and           #
#     parsing any responses the server returns                                               #
#                                                                                            #
##############################################################################################

def settingSocketUp(portNum):
    """Sets up a server socket that listens on the specified port."""
    
    try:
        # Ensure portNum is an integer
        portNum = int(portNum)
        #print("Listening on port:", portNum)

        # Create a socket using the correct syntax
        server_socket = socket(AF_INET, SOCK_STREAM)

        # Allow reusing the address
               # Bind the socket to the port
        server_socket.bind(("", portNum))

        # Start listening for incoming connections
        server_socket.listen(5)  # Allow up to 5 pending connections
        return server_socket

    except OSError as e:
        print(f"Error: Unable to bind to port {portNum}: {e}")
        return None  # Return None so caller knows the setup failed

    except error as e:
        print(f"Socket error: {e}")
        return None





def process_connect(ftp_control_connection): 
    global connection_active
    
    

    #print("in process_connect") 
    """
    Handles processing of a valid CONNECT command.
    - Reads the server's initial greeting message.
    - Sends required FTP commands (USER, PASS, SYST, TYPE I).
    - Parses and prints server responses.
    """
    try:
        # Step 1: Receive and print server greeting
        
        #print("Recieving the greeting")

        #formatStr(server_response) 

        #if "220" in server_response:
            #print("FTP reply 220 accepted. Test is 
            #print(parse_output)  # Print parsed output

        # Step 2: Generate and send the required FTP commands
        connect_commands = generate_connect_output()
        #print("these are the connect_commands we are generating" + str(connect_commands))



        for command in connect_commands:
              #print("this is the command we are dealing with:" + str(command))
            sys.stdout.write(command) 
            ftp_control_connection.sendall(command.encode())  # Send command
            #print("sent connection")
            response = ftp_control_connection.recv(1024).decode().strip()  # Receive response
            formatStr(response)
     
            #print(str(response))

            #print("recieved response")
            #parse_output, reply_code = parse_reply(response)  # Parse response
            #print(parse_output)  
        #print("we are done with connect")

        connection_active = True
    except Exception as e:
        sys.stdout.write("CONNECT failed\r\n")
        ftp_control_connection.close()


#the port should not increment if it's not successful
def process_get(ftp_control_connection, file_path, welcoming_port, retr_count):
    #print("I am in process_get") 
    """
    Handles the GET request in the FTP client.
    - Sends the `PORT` command using the welcoming port.
    - Sends `RETR` and waits for responses.
    - Validates all FTP responses using `validate_ftp_response()`.
    - Creates a listening socket for file retrieval.
    - Saves the received file into `retr_files/`.
    """
    #print("********************This is the data port:" + str(welcoming_port))
    client_ip = initialize_client_ip()
    #print("this is welclomgin port" + str(welcoming_port)) 
    # Calculate the correct port for data transfer
    data_port = int(welcoming_port)  # Increment for each GET
    port_high = data_port // 256
    port_low = data_port % 256
    port_command = f"PORT {client_ip.replace('.', ',')},{port_high},{port_low}\r\n"
    # Create and bind a listening socket for data transfer
    try:
                

        data_socket =  socket(AF_INET, SOCK_STREAM)
        #print("this is client_ip" + str(client_ip))
        data_socket.bind((client_ip, data_port))
        data_socket.listen(1)  # Prepare for server connection
        #print(f"Listening on {client_ip}:{data_port} for FTP-data connection")
    except Exception as e:
        print("GET failed, FTP-data port not allocated.")
        return 0
    

    #print("ATA PROT")
    # Send the `PORT` command
    

    #print will just have a new line character
    

    sys.stdout.write(port_command)
    ftp_control_connection.sendall(port_command.encode())

    # Receive and validate `PORT` response
    received = ftp_control_connection.recv(1024).decode()
    #print("this is the str:" + str(received))
    #print("I have recieved it back")
    parsed,code= parse_reply(received)
    #print(int(code))
    #print("1")
    print(parsed)
    #we expect an EOL for parsed
    if int(code) != 200:       
        return 0
       
    #print("past code block")
    # Send `RETR` command
    retr_command = f"RETR {file_path}\r\n"
    #print("this is the retr_command:" + str(retr_command))
    sys.stdout.write(retr_command)
    ftp_control_connection.sendall(retr_command.encode())
    #print("SENT")
    
    try:
     
        server_response = ftp_control_connection.recv(1024).decode()
        parsed,code = parse_reply(server_response)
        #print("2")
        print(parsed)
        if not code == ("150"):
            return 0



    except Exception as e:
        return 0

    # Accept FTP-data connection
    try:
        #TODO: make sure the same file is not read multiple times
        conn, addr = data_socket.accept()
        filename = f"retr_files/file{retr_count}"
        os.makedirs("retr_files", exist_ok=True)
        
        with open(filename, "wb") as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        conn.close()
        data_socket.close()

        final_response = ftp_control_connection.recv(1024).decode()
        parsed,code = parse_reply(final_response)
        #print("3")
        print(parsed)
        if int(code) == 250:


            return  1
        else:
            return 0
    except:
        print("GET failed, FTP-data port not allocated.")
        return retr_count




##############################################################################################
#                                                                                            # 
#     This function is intended to handle processing valid GET commands.                     #
#     The client will try to create a "welcoming" socket, and if successful, will            #
#     then send the PORT/RETR commands to the server and process the received data.          #
#                                                                                            #
##############################################################################################



#YOUR CODE HERE

##############################################################################################
#                                                                                            # 
#     This function is intended to handle processing valid QUIT commands.                    #
#     The client will send the necessary commands to the server and print any server         #
#     responses. It will then close the ftp_control_conneciton and terminate execution.      #
#                                                                                            #
##############################################################################################
def process_quit(ftp_control_connection):
    try:

        if not ftp_control_connection:
            sys.stdout.write("ERROR -- No active connection\n")
            return
        
        quit_command = "QUIT\r\n"
        sys.stdout.write(quit_command)  
        ftp_control_connection.sendall(quit_command.encode())
     
        server_response = ftp_control_connection.recv(1024).decode()
        parsed,code = parse_reply(server_response)
        print(parsed)
        #print("this is the server_response for the quit command:" + str(server_response))
        #print(f"FTP reply {server_response}")
        ftp_control_connection.close()
        #print("FTP client disconnected.")
    except error as e:
        print(f"Socket error while quitting: {e}")
        return False
    return True



##############################################################
#       The following two methods are for generating         #
#       the appropriate output for each valid command.       #
##############################################################

def increment_client_port(client_port):
    client_port +=1
    if client_port > 65535:
        client_port = 1024
    deconstructed_port = f"{int(client_port / 256)},{client_port % 256}"
    return client_port,deconstructed_port


# Example usage


def generate_connect_output():
    connect_commands = ["USER anonymous\r\n",
                      "PASS guest@\r\n",
                      "SYST\r\n",
                      "TYPE I\r\n"]
    return connect_commands



def generate_get_output(port_num, file_path):
    file_name = file_path.split("/")[-1]
    get_accepted_message = f"GET accepted for {file_path}"
    port_high = port_num // 256
    port_low = port_num % 256

    port_command_message = f"PORT 127,0,0,1,{port_high},{port_low}"

    return (get_accepted_message ,port_command_message)
 
##############################################################
#         Any method below this point is for parsing         #
##############################################################

############################################
#        Following methods are for         #
#         parsing input commands           #
############################################
# CONNECT<SP>+<server-host><SP>+<server-port><EOL>
def parse_connect(command):

    #print("in formatStr")
    #print("In parse_connect")
    server_host = ""
    server_port = -1

    if command[0:7] != "CONNECT" or len(command) == 7:
        return "ERROR -- request", server_port, server_host
    command = command[7:]
    
    command = parse_space(command)
    if len(command) > 1:
        command, server_host = parse_server_host(command)
    else:
        command = "ERROR -- server-host"

    if "ERROR" in command:
        return command, server_port, server_host

    command = parse_space(command)
    if len(command) > 1:
        command, server_port = parse_server_port(command)
    else:
        command = "ERROR -- server-port"

    server_port = int(server_port)    

    if "ERROR" in command:
        return command, server_port, server_host
    elif command != '\r\n' and command != '\n':
        return "ERROR -- <CRLF>", server_port, server_host
    return f"CONNECT accepted for FTP server at host {server_host} and port {server_port}", server_port, server_host

# GET<SP>+<pathname><EOL>
def parse_get(command):
    if command[0:3] != "GET":
        return "ERROR -- request"
    command = command[3:]
    
    command = parse_space(command)
    command, pathname = parse_pathname(command)

    if "ERROR" in command:
        return command
    elif command != '\r\n' and command != '\n':
        return "ERROR -- <CRLF>"
    return f"GET accepted for {pathname}", pathname

# QUIT<EOL>
def parse_quit(command):
    if command != "QUIT\r\n" and command != "QUIT\n":
        return "ERROR -- <CRLF>"
    else:
        return "QUIT accepted, terminating FTP client"

# <server-host> ::= <domain>
def parse_server_host(command):
    command, server_host = parse_domain(command)
    if command == "ERROR":
        return "ERROR -- server-host", server_host
    else:
        return command, server_host

# <server-port> ::= character representation of a decimal integer in the range 0-65535 (09678 is not ok; 9678 is ok)
def parse_server_port(command):
    port_nums = []
    port_string = ""
    for char in command:
        if ord(char) >= ascii_codes["0"] and ord(char) <= ascii_codes["9"]:
            port_nums.append(char)
            port_string += char
        else:
            break
    if len(port_nums) < 5:
        if ord(port_nums[0]) == ascii_codes["0"] and len(port_nums) > 1:
            return "ERROR -- server-port"
        return command[len(port_nums):], port_string
    elif len(port_nums) == 5:
        if ord(port_nums[0]) == ascii_codes["0"] or  int(command[0:5]) > 65535:
            return "ERROR -- server-port"
    return command[len(port_nums):], port_string

# <pathname> ::= <string>
# <string> ::= <char> | <char><string>
# <char> ::= any one of the 128 ASCII characters
def parse_pathname(command):
    pathname = ""
    if command[0] == '\n' or command[0:2] == '\r\n':
        return "ERROR -- pathname", pathname
    else:
        while len(command) > 1:
            if len(command) == 2 and command[0:2] == '\r\n':
                return command, pathname
            elif ord(command[0]) >= ascii_codes["min_ascii_val"] and ord(command[0]) <= ascii_codes["max_ascii_val"]:
                pathname += command[0]
                command = command[1:]
            else:
                return "ERROR -- pathname", pathname
        return command, pathname

# <domain> ::= <element> | <element>"."<domain>
def parse_domain(command):
    command, server_host = parse_element(command)
    return command, server_host

# <element> ::= <a><let-dig-hyp-str>
def parse_element(command, element_string=""):
    # Keep track of all elements delimited by "." to return to calling function

    # Ensure first character is a letter
    if (ord(command[0]) >= ascii_codes["A"] and ord(command[0]) <= ascii_codes["Z"]) \
    or (ord(command[0]) >= ascii_codes["a"] and ord(command[0]) <= ascii_codes["z"]):
        element_string += command[0]
        command, let_dig_string = parse_let_dig_str(command[1:])
        element_string += let_dig_string
        if command[0] == ".":
            element_string += "."
            return parse_element(command[1:], element_string)
        elif command[0] == ' ':
            return command, element_string
        else:
            return "ERROR", element_string
    elif command[0] == ' ':
        return command, element_string
    return "ERROR", element_string

# <let-dig-hyp-str> ::= <let-dig-hyp> | <let-dig-hyp><let-dig-hyp-str>
# <a> ::= any one of the 52 alphabetic characters "A" through "Z"in upper case and "a" through "z" in lower case
# <d> ::= any one of the characters representing the ten digits 0 through 9
def parse_let_dig_str(command):
    let_dig_string = ""
    while (ord(command[0]) >= ascii_codes["A"] and ord(command[0]) <= ascii_codes["Z"]) \
    or (ord(command[0]) >= ascii_codes["a"] and ord(command[0]) <= ascii_codes["z"]) \
    or (ord(command[0]) >= ascii_codes["0"] and ord(command[0]) <= ascii_codes["9"]) \
    or (ord(command[0]) == ord('-')):
        let_dig_string += command[0]
        if len(command) > 1:
            command = command[1:]
        else:
            return command, let_dig_string
    return command, let_dig_string

# <SP>+ ::= one or more space characters
def parse_space(line):
    if line[0] != ' ':
        return "ERROR"
    while line[0] == ' ':
        line = line[1:]
    return line


#############################################
#    Any method below this point is for     #
#         parsing server responses          #
#############################################
# <reply-code><SP><reply-text><CRLF> 
def parse_reply(reply):
    # <reply-code>
    reply, reply_code = parse_reply_code(reply)
    if "ERROR" in reply:
        return reply, reply_code
    
    # <SP>
    reply = parse_space(reply)
    if "ERROR" in reply:
        return "ERROR -- reply-code", reply_code
    
    # <reply-text>
    reply, reply_text = parse_reply_text(reply)
    if "ERROR" in reply:
        return reply, reply_code
    
    # <CRLF>
    if reply != '\r\n' and reply != '\n':
        return "ERROR -- <CRLF>", reply_code
    return f"FTP reply {reply_code} accepted. Text is: {reply_text}", reply_code

# <reply-code> ::= <reply-number>  
def parse_reply_code(reply):
    reply, reply_code = parse_reply_number(reply)
    if "ERROR" in reply:
        return "ERROR -- reply-code", reply_code
    return reply, reply_code

# <reply-number> ::= character representation of a decimal integer in the range 100-599
def parse_reply_number(reply):
    reply_number = 0
    if len(reply) < 3:
        return "ERROR", reply_number
    try:
        reply_number = int(reply[0:3])
    except ValueError:
        return "ERROR", reply_number
    reply_number = reply[0:3]
    if int(reply_number) < 100 or int(reply_number) > 599:
        return "ERROR", reply_number
    return reply[3:], reply_number

# <reply-text> ::= <string>
# <string> ::= <char> | <char><string>
# <char> ::= any one of the 128 ASCII characters
def parse_reply_text(reply):
    reply_text = ""
    if reply[0] == '\n' or reply[0:2] == '\r\n':
        return "ERROR -- reply_text", reply_text
    else:
        while len(reply) > 1:
            if len(reply) == 2 and reply[0:2] == '\r\n':
                return reply, reply_text
            elif ord(reply[0]) >= ascii_codes["min_ascii_val"] and ord(reply[0]) <= ascii_codes["max_ascii_val"]:
                reply_text += reply[0]
                reply = reply[1:]
            else:
                return "ERROR -- reply_text", reply_text
        return reply, reply_text

if __name__ == "__main__":
    read_commands()




