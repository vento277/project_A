#Content of main.py; use as is
from tkinter import *
import multiprocessing
import time

import part2_client 
import part2_server 

if __name__ == "__main__":
    part2_server = multiprocessing.Process(target=part2_server.main)
    part2_server.start()
    time.sleep(1)  #to ensure server is up and running; may be commented out or changed

    numberOfClients = 3  #Change this value for a different number of clients
    for count in range(1, numberOfClients+1):
        multiprocessing.Process(target=part2_client.main, name=f"Client{count}").start()