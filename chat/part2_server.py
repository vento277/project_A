from tkinter import *
import socket
import threading

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sends 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    """
    def __init__(self, window):
        self.window = window
        self.window.title("Chat Server")
        self.window.geometry("400x400")

        # Server socket setup
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 12345
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Allow up to 5 connections

        # Client connections list
        self.clients = []
        self.client_names = {}

        # GUI Setup
        Label(window, text="Chat Server", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 5))

        Label(window, text="Chat History:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(1, 1))
        self.chat_display = Text(window, height=20, width=50)
        self.chat_display.pack(padx=10, pady=10)
        self.chat_display.config(state=DISABLED)

        # Start accepting connections
        self.accept_connections_thread = threading.Thread(target=self.accept_connections)
        self.accept_connections_thread.daemon = True
        self.accept_connections_thread.start()

    def accept_connections(self):
        """
        Continuously accept incoming client connections
        """
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                
                # Start a thread to handle this client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                self.update_display(f"Error accepting connection: {e}")
                break

    def handle_client(self, client_socket):
        """
        Handle individual client communication
        """
        try:
            # Receive client name
            client_name = client_socket.recv(1024).decode('utf-8')
            self.client_names[client_socket] = client_name
            self.update_display(f"{client_name} has joined the chat")

            while True:
                # Receive message from client
                message = client_socket.recv(1024).decode('utf-8')
                
                # Check for disconnection
                if not message:
                    break

                # Broadcast message to all other clients
                self.broadcast(message, client_socket)
        except Exception as e:
            self.update_display(f"Error handling client: {e}")
        finally:
            # Remove the client and close socket
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_name = self.client_names.get(client_socket, "Unknown")
            self.update_display(f"{client_name} has left the chat")
            client_socket.close()

    def broadcast(self, message, sender_socket):
        """
        Broadcast message to all clients except the sender
        """
        sender_name = self.client_names.get(sender_socket, "Unknown")
        full_message = f"{sender_name}: {message}"
        self.update_display(full_message)

        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(full_message.encode('utf-8'))
                except:
                    # Remove client if unable to send
                    self.clients.remove(client)

    def update_display(self, message):
        """
        Update the server's chat display
        """
        self.chat_display.config(state=NORMAL)
        self.chat_display.insert(END, message + "\n")
        self.chat_display.config(state=DISABLED)
        self.chat_display.see(END)

def main():
    window = Tk()
    ChatServer(window)
    window.mainloop()

if __name__ == '__main__':
    main()