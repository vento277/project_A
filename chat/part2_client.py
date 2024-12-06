# Group#: G5
# Student Names: Weifeng Ke & Peter Kim

from tkinter import *
import socket
import threading
from multiprocessing import current_process

class ChatClient():
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    def __init__(self, window: Tk) -> None:
        #store the main window reference for GUI management and set the window title and initial size
        self.window = window
        self.client_name = current_process().name   #generate client name using the current process name
        self.window.title(f"Chat Client - {self.client_name}")
        self.window.geometry("400x400")

        #create a TCP socket for network communication
        #AF_INET specifies IPv4 and SOCK_STREAM specifies TCP connection-oriented socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 65535

        #connect to server
        try:
            self.client_socket.connect((self.host, self.port))  #establish connection to the server using host and port
            self.client_socket.send(self.client_name.encode('utf-8')) #send the client name to the server for identification
        
        except Exception as e:  # handle connection failures
            print(f"Could not connect to server: {e}")
            self.window.quit()
            return

        #GUI Setup
        #add titles as per project specification
        Label(window, text="Client{} @port #{}".format(current_process().name[-1], current_process().pid), font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 5))

        #create a frame for message entry
        self.message_frame = Frame(window)
        self.message_frame.pack(padx=10, pady=5, fill=X)
        Label(self.message_frame, text="Chat Message: ", font=("Arial", 12)).pack(anchor="w", side=LEFT)

        #create a Entry widget to enter chat messages
        self.message_entry = Entry(self.message_frame, width=40)
        self.message_entry.pack(side=RIGHT, expand=True, fill=X, padx=(0,10))
        self.message_entry.bind('<Return>', lambda event: self.send_message()) #bind the Enter key to send message function. Allows sending message by pressing Enter

        #create a frame for chat history
        Label(window, text="Chat History:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(1, 1))
        self.chat_box = Text(window, height=20, width=50, wrap=WORD)    #wrap=WORD ensures text wraps at word boundaries
        self.chat_box.pack(padx=10, pady=10, fill=BOTH, expand=True)
        self.chat_box.config(state=DISABLED)  #disable text editing to prevent user modifications

        # Start receive thread
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon = True)
        self.receive_thread.start()

    def display_message(self, message: str, align: str ="left") -> None:
        """
        Display message with specified alignment.
        """
        self.chat_box.config(state=NORMAL) #enable text widget to make changes

        #insert message with specified alignment
        if align == "right":
            self.chat_box.tag_configure("right", justify="right")
            self.chat_box.insert(END, message + "\n", "right")
        elif align == "center":
            self.chat_box.tag_configure("center", justify="center")
            self.chat_box.insert(END, message + "\n", "center")
        else:
            self.chat_box.tag_configure("left", justify="left")
            self.chat_box.insert(END, message + "\n", "left")

        self.chat_box.config(state='disabled')  #disable text widget to prevent editing 
        self.chat_box.see(END)  #scroll to the bottom to show the most recent message

    def send_message(self) -> None:
        """
        Send message to server
        """
        message = self.message_entry.get()  #retrieve message from entry widget

        if message:
            try:
                self.client_socket.send(message.encode('utf-8')) #encode and send message to server
                self.display_message(f"{self.client_name}: {message}", "right") #display sent message on the right side of chat box
                self.message_entry.delete(0, END) #clear the message entry after sending

            except Exception as e: 
                self.display_message(f"Error sending message: {e}", "center") #display any sending errors
                self.close_connection() #close connection if send fails

    def receive_messages(self) -> None:
        """
        Continuously receive messages from the server.
        Runs in a separate thread to allow non-blocking message reception.
        """
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8') #receive message from server

                #check if the message is empty (indicates disconnection)
                if not message:
                    break
                
                self.display_message(message) #display received messages on left side

            except Exception as e:
                self.display_message(f"Error receiving message: {e}", "center") #display any receving errors
                break
        
        # Close connection if receive thread exits
        self.close_connection()

    def close_connection(self) -> None:
        """
        Close socket connection and quit the window
        Handles cleanup when connection is lost or manually closed
        """
        try:
            self.client_socket.close() #attempt to close the socket
        except:
            pass    #ignore errors while closing

        self.window.quit()  #close the program window

def main() -> None:
    #set up Tk object
    window = Tk()
    #initialize a chat client object pass window in to interact with TKinter
    ChatClient(window)
    #start the whole process 
    window.mainloop()

if __name__ == '__main__':
    main()