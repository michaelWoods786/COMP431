import re
import sys

def check():
    print("hello world")


def parse_ftp_input_user_command(ftp_input_data):
    """
    Parses FTP input to extract the username from the USER command (case-insensitive).
    
    Args:
        input_data (str): The raw FTP input string.
    
    Returns:
        str: Extracted username if the USER command is valid, else an error message.
    """
    # Regular expression to match the USER command (case-insensitive)
    
    logged = False
    port = False
    comPat = re.compile(r'^(USER|PASS|TYPE|SYST|NOOP|QUIT|PORT|RETR)( .*)?\r\n$', re.IGNORECASE)
    PORT_PATTERN = re.compile(r'^(\d{1,3}),(\d{1,3}),(\d{1,3}),(\d{1,3}),(\d{1,3}),(\d{1,3})$')
    
    match = re.match(comPat, ftp_input_data, re.IGNORECASE)
    com = match.group(1)
    parameter = match.group(2)
    if match:
        
        if com == "USER":
            if not parameter:
                print("501 Syntax error in parameter.")
            else:
                print("331 Guest access OK, send password.")
        elif com == "PASS":
            if not parameter:
                print("501 Syntax error in parameter.")
            else:
                logged = True
                print("230 Guest login OK.")
        elif com == "TYPE":
            if parameter and parameter.strip() in ["A", "I"]:
                print(f"200 Type set to {parameter.strip()}.")

            if not parameter:
                print("501 Syntax error in parameter.")
        elif com == "SYST":
            print("215 UNIX Type: L8.")

        elif com == "NOOP":
            print("200 Command OK.")

        elif com == "QUIT":
            print("200 Command OK.")
            sys.exit(0)
        
        elif com == "RETR":
            if not logged:
                print("530 Not logged in.")
            elif not port:
                print("503 Bad sequence of commands.")
            elif not parameter:
                print("501 Syntax error in parameter.")
            else:
                retrs_count+=1
                print("150 File status okay.")
                print("250 Requested file action completed.")
                port = False

        return "501 Syntax error in parameter.\r\n"

for line in sys.stdin:
    parse_ftp_input_user_command(line)