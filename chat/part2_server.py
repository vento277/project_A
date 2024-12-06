# Group#: G5
# Student Names: Weifeng Ke & Peter Kim

from tkinter import *
import socket
import threading

class ChatServer():
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sends 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    """
    def __init__(self, window:Tk) -> None:
        #store the main window reference for GUI management and set the window title and initial size
        self.window = window
        self.window.title("Chat Server")
        self.window.geometry("400x400")

        #create a TCP socket for network communication
        #AF_INET specifies IPv4 and SOCK_STREAM specifies TCP connection-oriented socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #set local host IP.
        #127.0.0.1 is the loopback address (localhost)
        self.host = '127.0.0.1'
        self.port = 65535
        self.server_socket.bind((self.host, self.port)) # Bind the socket to the specific host and port. This prepares the socket to accept incoming connections
        self.server_socket.listen(1000) # The argument 1000 sets the maximum number of queued connections

        #initialize lists to track connected clients
        self.clients = []   #stores the actual socket connections
        self.client_names = {}  #maps sockets to their respective usernames

        #GUI Setup
        #add titles as per project specification
        Label(window, text="Chat Server", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 5))

        #create a Text widget to display chat messages
        Label(window, text="Chat History:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(1, 1))
        self.chat_display = Text(window, height=20, width=50)
        self.chat_display.pack(padx=10, pady=10)
        self.chat_display.config(state=DISABLED)    # Disable text editing to prevent user modifications

        #start a separate thread to continuously accept incoming connections. It prevents blocking the main GUI thread
        self.accept_connections_thread = threading.Thread(target=self.accept_connections, daemon = True) #daemon=True allows the thread to close when the main program exits   
        self.accept_connections_thread.start()

    def accept_connections(self) -> None:
        """
        Continuously accept incoming client connections.
        """
        while True:
            try:
                #accept a new client connection. This method blocks until a client connects and returns a new socket for the client and their network address
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)  #add the new client socket to the list of active clients
                
                #create a new thread to handle this specific client's communication
                #this allows multiple clients to be handled simultaneously
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon = True)  #each client gets its own thread for independent message processing
                client_thread.start()

            except Exception:
                #silently handle any communication errors
                break

    def handle_client(self, client_socket) -> None:
        """
        Handle individual client communication.
        """
        try:
            #receive the client's username 
            client_name = client_socket.recv(1024).decode('utf-8') #decode converts the received bytes to a string (1024 is the maximum number of bytes to receive)
            self.client_names[client_socket] = client_name  #store the client's name associated with their socket
            self.update_display(f"{client_name} has joined the chat") #announce the new client's arrival to the server's chat display

            while True:
                #continuously receive messages from the client
                message = client_socket.recv(1024).decode('utf-8') 
                
                #check if the message is empty (indicates disconnection)
                if not message:
                    break

                #broadcast the received message to all other connected clients
                self.broadcast(message, client_socket)

        except Exception:
            #silently handle any communication errors
            pass

        finally:
            #cleanup procedures when a client disconnects
            if client_socket in self.clients:
                self.clients.remove(client_socket)

            client_name = self.client_names.get(client_socket, "Unknown")   #retrieve the client's name (default to "Unknown" if not found)
            self.update_display(f"{client_name} has left the chat") #announce the client's departure
            client_socket.close() #close the client's socket to free up resources

    def broadcast(self, message: str, sender_socket: socket) -> None:
        """
        Broadcast message to all clients except the sender.
        """
        sender_name = self.client_names.get(sender_socket, "Unknown")   #retrieve the sender's name (default to "Unknown" if not found)
        full_message = f"{sender_name}: {message}"  #combine the sender's name with their message
        self.update_display(full_message)   #update the server's chat display with the full message

        #send the message to all connected clients except the sender
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(full_message.encode('utf-8'))   #encode the message to bytes and send it to the client

                except:
                    self.clients.remove(client) #remove client if unable to send

    def update_display(self, message: str) -> None:
        """
        Update the server's chat display.
        """
        self.chat_display.config(state=NORMAL)  #enable the text widget to make changes
        self.chat_display.insert(END, message + "\n")   #insert the new message at the end of the text widget
        self.chat_display.config(state=DISABLED)    #disable the text widget to prevent user editing
        self.chat_display.see(END)  #scroll to the bottom to show the most recent message

def main():
    #create a TKinter object
    window = Tk()
    #crate a ChatServer object
    ChatServer(window)
    window.mainloop()

if __name__ == '__main__':
    main()