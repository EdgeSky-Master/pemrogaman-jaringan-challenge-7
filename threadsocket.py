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
                    print(f"Sending: {message_to_send.decode()}")
                    broadcast(message_to_send, conn)
                
                elif message.strip().lower() == "list":

                    client_list = get_list_of_client()
                    print(client_list)
                    try:
                        client_list_str = '\n'.join(client_list) +'\n'  
                        sent_bytes = conn.send(client_list_str.encode())
                        print(f"Sent {sent_bytes} bytes back to the sender.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                elif message.startswith("changeid "):
                    
                    new_client_id = message.split("changeid ")[1].strip()
                    for i, client in enumerate(list_of_client):
                        if client[0] == conn:
                            print(f"change {client[0]} to {new_client_id}")
                            list_of_client[i] = (conn, new_client_id)
                            conn.send(f"Your assigned client ID is now {new_client_id}\n".encode())
                            break
                elif message.startswith("private "):
                    for _, client_id in list_of_client:
                        match2 = re.match(fr"^private \s*({client_id}) (.*)$", message)
                        if match2:
                            receiver_id = match2.group(1)
                            content = match2.group(2)
                            print(f"Sending private message to {receiver_id}: {content}")
                            for client_socket,client_id in list_of_client:
                                if client_id == receiver_id:
                                    client_socket.send(f"You receive a message {content}\n".encode())
                                    break
                    
                    
                else:                    
                    message_to_send = message.encode()
                    print(f"Sending: {message_to_send.decode()}")
                    broadcast(message_to_send, conn)
                
                
                

            else:
                remove(conn)
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
def broadcast2(message, connection):
    for clients in list_of_client:
        if clients[0] == connection:
            try:
                clients[0].send(message)
            except:
                clients[0].close()
                remove(clients[0])
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

def change_client_id(conn, new_client_id):
    for i, client in enumerate(list_of_client):
        if client[0] == conn:
            list_of_client[i] = (conn, new_client_id)
            break
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