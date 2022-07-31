import random
import json
import socket
import sys
import praw
import csv

from os import system, name
from os.path import exists


def clear():
    """Clear console"""
   # for windows
    if name == 'nt':
        _ = system('cls')

   # for mac and linux
    else:
       _ = system('clear')


def receive_connection():
    """Wait for and then return a connected socket..
 
    Opens a TCP connection on port 8080, and waits for a single client.
 
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client
 
 
def send_message(client, message):
    """Send message to client and close the connection."""
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()
 
 
def gather_app_creds():
    """Provide the program's entry point when directly executed."""
    print(
        "Go here while logged into the account you want to create a token for: "
        "https://www.reddit.com/prefs/apps/"
    )
    print(
        "Click the create an app button. Put something in the name field and select the"
        " script radio button."
    )
    print("Put http://localhost:8080 in the redirect uri field and click create app")
    print("------------------------\n")
    client_id = input(
        "Enter the client ID, it's the line just under Personal use script at the top: "
    )
    client_secret = input("Enter the client secret, it's the line next to secret: ")
    clear()
 
    scopes = ["*"]
 
    reddit = praw.Reddit(
        client_id=client_id.strip(),
        client_secret=client_secret.strip(),
        redirect_uri="http://localhost:8080",
        user_agent="thread maker",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes=scopes, state=state, duration="permanent")
    print(f"Now open this url in your browser: {url}")
    sys.stdout.flush()
 
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }
 
    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return False
    elif "error" in params:
        send_message(client, params["error"])
        return False
 
    refresh_token = reddit.auth.authorize(params["code"])

    with open('creds.json','w') as f:
        json.dump({"client_id":client_id.strip(),
                    "client_secret":client_secret.strip(),
                    "refresh_token":refresh_token,
                    "user_agent":"Thread maker",
                    "redirect_uri":"http://localhost:8080"},f,indent=4)
    return True


def gather_post_info():

    sub = input("Enter the subreddit to post to: ")
    csv_file = input("Enter the csv file to grab structure from: ")
    if not exists(csv_file):
        print(f"{csv_file} is not found in your folder. Please try again.")

    info = {"subreddit":sub,"csv_file":csv_file}

    with open(csv_file,'r') as f:
        reader = csv.reader(f)
        header = next(reader)

    print(f"Found {len(header)} columns, using {len(header)-1} threads")
    clear()

    print("For the following inputs you can use $NAME$ to substitute for the thread identifier")
    title = input("Enter title for threads with no children: \n")
    description = input("Enter description for threads with no children: \n")
    info[-1] = {'title':title,'description':description}


    clear()
    for i in range(len(header)):
        print(f"--------------Thread Level {i}----------------")
        print("For the following inputs you can use $NAME$ to substitute for the thread identifier")
        title = input(f"Enter title for {'master' if i == 0 else header[i]} thread: \n")
        description = input(f"Enter description for {'master' if i == 0 else header[i]} thread: \n")
        info[i] = {'title':title,'description':description}
        clear()

    with open("info.json",'w') as f:
        json.dump(info,f,indent=4)


def main():
    # if gather_app_creds():
    gather_post_info()

if __name__ == '__main__':
    main()

