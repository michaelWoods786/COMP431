

import re

import sys

import shutil

import os

import socket
"""

For this project, I used a state-based approach where variables like logIn and portSet track the state session. 


I used regular expressions to validate the syntax, maintained my state variables, and reset variables like login PortSet to enforce the protocol outlined

in the project description


If the user input was ever wrong, I returned an error message.

"""


#logIn will track if a user is given 

#retr count will keep track of what the current file name will be

#if a RETR command is recieved without a valid preceding PORT command, the server will reply with (503 bad sequence of commands)

#when we quit the program

# if we quit we terminate the parser

logIn = False

portSet = False

retr_count = 0


quit = False

maxPort = 65535

maxIP = 255


#the purpose of these regular expressions is to see if the input data matches it or not. If it does,


#this regular expression checks if it aligns with any of the given FTP commands, one or more spaces(optional) and ending with \r\n

comPat = re.compile(r'^(USER|PASS|TYPE|SYST|NOOP|QUIT|PORT|RETR)( +.*)?$', re.IGNORECASE)


#a given port address we will seee if it matches 

portPat = re.compile(r'^(\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3})$', re.IGNORECASE)




#this function will take ftp_input_data and execute the appropiate protocol depending on the input data







def settingSocketUp(port_number):
   #print("setting the socket up...") 
   server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
   #print("this is the ftp_input_data:" + str(ftp_input_data))
   server_socket.bind(("", int(port_number)))
   server_socket.listen(1)


   while (True):
       #accept client control

       client_socket, foop = server_socket.accept()
       #print("accepted_control")
       #communicate with client
       sys.stdout.write("220 COMP 431 FTP server ready.\r\n") 
       client_socket.sendall(b"220 COMP 431 FTP server ready.\r\n")
       
       ret = handle_client(client_socket)
       #print("got the ret:") 
       

IpPort = ""

def send_file(client_socket, filename, data_host, data_port):
    """Handles sending a file to the client over the FTP-data connection."""
    print(f"i am in send file, with port{data_port} and host {data_host}")
    try:
        # Step 1: Ensure the file exists
        with open(filename, "rb") as f:
            print("successfully opened the file")
            # Step 2: Create a new FTP-data connection
            #print("getting a data socket")
            print("before data socket:")
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("after data socket:")
            try:
                print("this is the port:" + str(data_port))
                data_socket.connect((data_host, int(data_port)))  # Connect to client
                #print("got the data socket")
            except socket.error as e:
                #print(f"Error connecting to client: {e}")
                sys.stdout.write("550 Can not open data connection.\r\n")
                client_socket.sendall(b"550 Can not open data connection.\r\n")
                return

            # Step 3: Notify client that file transfer is starting
            client_socket.sendall(b"150 File status okay.\r\n")
            #print(f"Sending file: {filename} to {data_host}:{data_port}")

            # Step 4: Send file in chunks
            while chunk := f.read(1024):
                try:
                    data_socket.sendall(chunk)
                except BrokenPipeError:
                    #print("Broken Pipe: Client disconnected during transfer.")
                    sys.stdout.write("550 Can not open data connection.\r\n")
                    client_socket.sendall(b"550 Can not open data connection.\r\n") 
                    data_socket.close()
                    return

            # Step 5: Close data connection and notify client of success
            data_socket.close()
            sys.stdout.write("250 Requested file action completed.\r\n")
            #sys.stdout.write("550 Can not open data connection.\r\n")
            client_socket.sendall(b"250 Requested file action completed.\r\n")
            #print(f"File {filename} sent successfully.")

    except FileNotFoundError:
        sys.stdout.write("550 File not found.\r\n")
        client_socket.sendall(b"550 File not found.\r\n")
        #print(f"File {filename} not found.")

    except socket.error as e:
        sys.stdout.write("550 File not found.\r\n")
        client_socket.sendall(b"550 Can not open data connection.\r\n")
        #print(f"Error sending file: {e}")



filename = ""
portNum = 0

def handle_client(client_socket):
    #print("i am handling the client")
    

    global logIn, portSet, retr_count, quit

    


    while True:
       
        try:
            command = client_socket.recv(1024).decode("utf-8").strip()
            
     #       print("---------------------------this is the command:------------------------" + str(command))

            if not command:
                break
            com, ret = parse_ftp_input_user_command(command)
            #print("this is com: " + str(com))
            #print("thsi is ret:" + str(ret))
            #print("i have returned")
            filename = ""
            if "|" in ret:
                #print("in there")
                splitted = ret.split("|")
                ret = splitted[0]
                filename = splitted[1]
                
            #print("-------------------------------")
            #print ("this is ret:"  +str(ret))
            #print("-------------------------------")
            #print("this is filename:" + str(filename))
                       #print("we are parsing the command: " + str(command))
            #print("this is com" + str(com))
            #print("this is retr" + str(ret))
            if ret:
                sys.stdout.write(ret +"\r\n")
                 

                if com == "RETR" and "150" in ret:
                    #client_socket.sendall((ret + "\r\n").encode())
                    #client_socket.sendall(("portNum:" + portNum))
                    #print("WE ARE ENTERING Send file")
                    
                    #client_socket.sendall( (ret+"\r\n").encode())
                    send_file(client_socket, filename,ipPort, portNum)
                 
                else:
                    #print("we are sending the response back")
                    #print("this is ret:" + str(ret))
                    

                    #print("--------------SENDING THE FOLLOWING MESSAGE back to the client:" + str(ret + "\r\n"))
                    #print("this is ret:" +str(ret)) 
                    #here we need to make sure \r\n is sent
                    #print("this is ret:" + str(ret))

                    if not ret.endswith("\r\n"):
                         ret += "\r\n"
                    
                    returnStr = ret
                    #print(f"DEBUG: Raw server response --> {repr(returnStr)}")
                    #print("Sending it over")
                    client_socket.sendall(returnStr.encode())
                    #print("-----------------------this is quit:" + str(quit))
                    #print("DONE")

                

                    
            if quit:
                break
        
        except ConnectionResetError:
            #print("Client disconnected abruptly.")

            break
        except Exception as e:

            #TODO: not sure what to put here
            return_str = f"Error processsing client command: {e}"
            client_socket.sendall(returnStr.encode())
            break

    #print("closing the socket")
    client_socket.close()
    logIn = False
    portSet = False
    retr_count = 0
    quit = False
    

def parse_ftp_input_user_command(ftp_input_data):
        
    sys.stdout.write(ftp_input_data.strip() +"\r\n")
    #print("ENTERED parser" + str(ftp_input_data))
    ftp_input_data = ftp_input_data.encode().decode("unicode_escape")
    ret_str = ""
    #print("In parse_ftp_input_user_command:" + str(ftp_input_data))
    
    global logIn, portSet, retr_count, quit


    if quit:

        ret_str = ("503 Bad sequence of commands.")

        return


    match = comPat.match(ftp_input_data)


    if not match:
        ret_str = ("Failed first match")
        
        #TODO: is this expected syntax error>
        ret_str = ("500 Syntax error, command unrecognized.")

        return



    #gets command and parameter

    com = match.group(1).upper() 

    parameter = match.group(2).strip() if match.group(2) else None
    
   # print("this is the com: " + str(com) + "this is the parameter:" + str(parameter))


    #identifies user making file request

    if com == "USER":

        if not parameter:

            ret_str = ("501 Syntax error in parameter.")


        #here, we reset login to False, ensuring that our prior login sessions are cleared.

        #Suppose a new USER command is issued during an ongoing session, then the program will invalidate

        #previous logins and expect a new password


        else:
            #print("ENTERED ON USER")
            logIn = False
            
            ret_str = ("331 Guest access OK, send password.")
            #print("**************************This is ret_str:" + str(ret_str))
            logIn = True

    #typecode specification : <type-code>::" "A" | "I"

    elif com == "TYPE":

        if parameter in ["I", "A"]:

            ret_str =(f"200 Type set to {parameter}.")
        else:

            ret_str =("501 Syntax error in parameter.")

        #Password will be of type string (<password> ::= <string>)

    elif com == "SYST":
        ret_str = "215 UNIX Type: L8."

    elif com == "PASS":

        #does not match regular expression

        if not parameter:

            ret_str = ("501 Syntax error in parameter.")

            #makes sure pass command issued after valid user

        elif not logIn:

            ret_str = ("503 Bad sequence of commands.")

            #where login is set to true if a pass command and follows a user command

        else:

            logIn = True

            ret_str = ("230 Guest login OK.")

        #provides info on operating system

    elif com == "SYST":
        #print("the SYST command  has been recieved")
        ret_str = ("215 UNIX TYPE: L8")

        #specifies whether server is still active

    elif com == "NOOP":

        ret_str = ("200 Command OK.")

        #terminates program

    elif com == "QUIT":
        #print("QUIT COmmand has been recieved")
        ret_str = ("221 Goodbye.")

        quit = True

        #tells server which file client wants to recieve


    

    elif com == "RETR":
        base_path = "/home/miwood"

        global retr_count
        
        #TODO: look over this
        if not parameter:
            print("501 Syntax error in parameter.")

        if not portSet:
            ret_str = ("503 bad sequence of commands.")  # Ensures PORT is set before RETR
            return
        
        print("before join")
        fp = os.path.join(base_path, parameter) 
        print("this is the file_path:" + str(fp)) 
        if os.path.exists(fp) and os.path.isfile(fp):
            print("it exists")
            ret_str = "150 File status okay."  # Before copying
            filename = fp 
            ret_str = ret_str + "|" + filename
            print("this si the ret str:"  +str(ret_str))
            portSet = False 
            print("returning...")
            
        
        else:
            ret_str = "550 File not found or access denied."
                
    elif com == "PORT":
        global portNum
        global ipPort 

        #print("I am in PORT:")
            #print("this is the parameter:" + str(portPat))
            #making sure it matches the port pattern

            #print(portPat.match(parameter))
            #print(str(not parameter))
        if not parameter or not portPat.match(parameter):
                #print("ENTERED")
            ret_str = ("501 Syntax error in parameter.")

        else:

            portSet = True

            ips = parameter.split(",")

            #getting the ipAddress

            data_host = '.'.join(ips[:4])
            ipPort=  data_host
            #print("This is the dataHost:" + str(data_host))
            #print("this is the ipPort:" + str(ipPort))
            #getting the port number

            portNum = int(ips[4]) * 256 + int(ips[5])
            #print("this is the portNum:" + str(portNum))
            #makes sure ip and portNum is within range

            if any(int(ip) > maxIP for ip in ips[:4]) or not (0 <= portNum <= maxPort):

                ret_str = ("501 Syntax error in parameter.")

            else:

                ret_str = f"200 Port command successful ({data_host},{portNum})."   


    return (com, ret_str)



def main():
    if len(sys.argv) != 2:
        sys.exit(1)


    try:
        port_number = int(sys.argv[1])
        settingSocketUp(port_number)
        if not (1024 <= port_number <= 65535):
            raise ValueError
    except ValueError:
        print("port number is too large or small")


if __name__ == "__main__":
    main()

