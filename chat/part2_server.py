from tkinter import *
import socket
import threading
import sys

class ChatServer:
    def __init__(self, window):
        self.window = window
        self.window.title("Server")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI setup
        self.chat_box = Text(self.window, state='disabled', wrap='word', bg='lightblue')
        self.chat_box.pack(padx=10, pady=10, fill=BOTH, expand=True)

        self.clients = []
        self.server_socket = None
        self.start_server()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 12345))
        self.server_socket.listen(5)
        self.display_message("Server started. Waiting for clients...")
        # Start accepting client connections
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            try:
                client_socket, _ = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                self.display_message(f"New client connected. Total clients: {len(self.clients)}")
            except OSError:
                break  # Exit if the server socket is closed

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if message:
                    self.broadcast_message(message, client_socket)
                    self.display_message(message)
            except ConnectionError:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                break

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode("utf-8"))
                except ConnectionError:
                    self.clients.remove(client)

    def display_message(self, message):
        self.chat_box.config(state='normal')
        self.chat_box.insert(END, message + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.see(END)

    def on_close(self):
        self.display_message("Shutting down server...")
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()
        self.window.destroy()
        sys.exit()

def main():
    window = Tk()
    ChatServer(window)
    window.mainloop()
