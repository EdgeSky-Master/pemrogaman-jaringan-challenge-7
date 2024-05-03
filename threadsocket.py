import socket
import select
import sys
import threading
import re

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_address = '127.0.0.1'
port = 8081
server.bind((ip_address, port))
server.listen(100)
list_of_client = []
counter = 0

def clientthread(conn, addr):
    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                print(f"Received message from <{addr[0]}>: {message}")
                print(message)
                
                match = re.match(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", message)
                if match:
                    num1 = int(match.group(1))
                    operator = match.group(2)
                    num2 = int(match.group(3))
                    result = None
                    if operator == '+':
                        result = num1 + num2
                    elif operator == '-':
                        result = num1 - num2
                    elif operator == '*':
                        result = num1 * num2
                    elif operator == '/':
                        result = num1 / num2  
                    
                    if result is not None:
                        
                        message_to_send = f"{num1}{operator}{num2}={result}\n".encode()
                    else:
                        message_to_send = "Invalid operation.\n".encode()
                #elif message == "changeID": #added changeID
## trying to add something here where the server will ask the client what unique ID the client want
                elif message == "list":
## if list, then I want to print all the stored ID in idlist which I've made below
                    client_list = get_list_of_client()
                    conn.send(str(client_list).encode())
               #elif message == "private": I'm thinking maybe place this on top so they can check for prIvate first
               ##in ordder to do that, we do something similar to the arithmetic part where it checks for the signs but with "private"
                else:                    
                    message_to_send = message.encode()
                
                
                print(f"Sending: {message_to_send.decode()}")
                broadcast(message_to_send, conn)

            else:
                remove(conn)
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

def broadcast(message, connection):
    for clients in list_of_client:
        if clients[0] != connection:
            try:
                clients[0].send(message)
            except:
                clients[0].close()
                remove(clients[0])
def remove(connection):
    if connection in list_of_client:
        list_of_client.remove(connection)

def generate_clientID():
    global counter
    counter +=1
    client_id = f"client{counter}"
    
    return client_id
def get_list_of_client():
    return [nickname for _, nickname in list_of_client]

while True:
    conn, addr = server.accept()
    client_id = generate_clientID()
    #idlist = [] ##added idlist for saving all the client IDs
    #idlist.append(client_id) ## using append to save in the next available space in the array
    list_of_client.append((conn, client_id))
    conn.send(f"Your assigned client ID is {client_id}\n".encode())
    
    print(addr[0] + " connected")
    threading.Thread(target=clientthread,args=(conn,addr)).start()

conn.close()