from tkinter import *
import socket
import threading
from multiprocessing import current_process

class ChatClient:
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    def __init__(self, window):
        self.window = window
        
        # Get client name from process name
        self.client_name = current_process().name
        self.window.title(f"Chat Client - {self.client_name}")
        self.window.geometry("400x500")

        # Socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 12345

        # Connect to server
        try:
            self.client_socket.connect((self.host, self.port))
            # Send client name to server
            self.client_socket.send(self.client_name.encode('utf-8'))
        except Exception as e:
            print(f"Could not connect to server: {e}")
            self.window.quit()
            return

        Label(window, text="Client{} @port #{}".format(current_process().name[-1], current_process().pid), font=("Arial", 12)).pack(anchor="w", padx=10, pady=(10, 10))

        # Chat Display
        self.chat_box = Text(window, height=20, width=50, wrap=WORD)
        self.chat_box.pack(padx=10, pady=10, fill=BOTH, expand=True)
        self.chat_box.config(state='disabled')

        # Configure tags for different alignments
        self.chat_box.tag_configure("left", justify="left")
        self.chat_box.tag_configure("center", justify="center")
        self.chat_box.tag_configure("right", justify="right")

        # Message Entry
        self.message_frame = Frame(window)
        self.message_frame.pack(padx=10, pady=5, fill=X)

        self.message_entry = Entry(self.message_frame, width=40)
        self.message_entry.pack(side=LEFT, expand=True, fill=X, padx=(0,10))

        self.send_button = Button(self.message_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=RIGHT)

        # Bind Enter key to send message
        self.message_entry.bind('<Return>', lambda event: self.send_message())

        # Start receive thread
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def display_message(self, message, align="left"):
        """
        Display message with specified alignment
        """
        self.chat_box.config(state='normal')
        if align == "right":
            self.chat_box.tag_configure("right", justify="right")
            self.chat_box.insert(END, message + "\n", "right")
        elif align == "center":
            self.chat_box.tag_configure("center", justify="center")
            self.chat_box.insert(END, message + "\n", "center")
        else:
            self.chat_box.tag_configure("left", justify="left")
            self.chat_box.insert(END, message + "\n", "left")
        self.chat_box.config(state='disabled')
        self.chat_box.see(END)

    def send_message(self):
        """
        Send message to server
        """
        message = self.message_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                # Display sent message on right side
                self.display_message(f"You: {message}", "right")
                self.message_entry.delete(0, END)
            except Exception as e:
                self.display_message(f"Error sending message: {e}", "center")
                self.close_connection()

    def receive_messages(self):
        """
        Continuously receive messages from the server
        """
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                # Display received messages on left side
                self.display_message(message)
            except Exception as e:
                self.display_message(f"Error receiving message: {e}", "center")
                break
        
        # Close connection if receive thread exits
        self.close_connection()

    def close_connection(self):
        """
        Close socket connection and quit window
        """
        try:
            self.client_socket.close()
        except:
            pass
        self.window.quit()

def main():
    window = Tk()
    ChatClient(window)
    window.mainloop()

if __name__ == '__main__':
    main()