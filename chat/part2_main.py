# Group#: G5
# Student Names: Weifeng Ke & Peter Kim
from tkinter import *
import multiprocessing
import time

import part2_client 
import part2_server 

# Implementation Done.
# Need detailed code documentation and final check against the requirements

# For Windows
if __name__ == "__main__":
    processes = []
    
    server_process = multiprocessing.Process(target=part2_server.main)
    server_process.start()
    processes.append(server_process)
    
    time.sleep(1)  #to ensure server is up and running; may be commented out or changed

    numberOfClients = 2  #Change this value for a different number of clients
    for count in range(1, numberOfClients+1):
        client_process = multiprocessing.Process(target=part2_client.main, name=f"Client{count}")
        client_process.start()
        processes.append(client_process)

    # Keep the main process running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating processes...")
        for process in processes:
            process.terminate()
            process.join()

    print("All processes terminated.")

# For Mac
# if __name__ == "__main__":
#     server = multiprocessing.Process(target=server.main)
#     server.start()
#     time.sleep(1)  #to ensure server is up and running; may be commented out or changed

#     numberOfClients = 2  #Change this value for a different number of clients
#     for count in range(1, numberOfClients+1):
#         multiprocessing.Process(target=client.main, name=f"Client{count}").start()