from tkinter import *
import socket
import threading
from multiprocessing import current_process
import sys

class ChatClient:
    def __init__(self, window):
        self.window = window
        self.window.title(current_process().name)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI setup
        self.chat_box = Text(self.window, state='disabled', wrap='word', bg='lightyellow')
        self.chat_box.pack(padx=10, pady=10, fill=BOTH, expand=True)

        self.entry = Entry(self.window)
        self.entry.pack(padx=10, pady=(0, 10), fill=X)
        self.entry.bind("<Return>", self.send_message)

        self.client_socket = None
        self.connect_to_server()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(("127.0.0.1", 12345))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.display_message("Connected to server.")
        except ConnectionError:
            self.display_message("Failed to connect to server.")

    def send_message(self, event=None):
        message = self.entry.get()
        if message and self.client_socket:
            try:
                self.client_socket.sendall(message.encode("utf-8"))
                self.entry.delete(0, END)
            except ConnectionError:
                self.display_message("Failed to send message.")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                self.display_message(message)
            except ConnectionError:
                self.display_message("Disconnected from server.")
                break

    def display_message(self, message):
        self.chat_box.config(state='normal')
        self.chat_box.insert(END, message + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.see(END)

    def on_close(self):
        if self.client_socket:
            self.client_socket.close()
        self.window.destroy()
        sys.exit()

def main():
    window = Tk()
    ChatClient(window)
    window.mainloop()
