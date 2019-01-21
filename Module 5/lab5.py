## James Pham ##
##   Lab 5    ##

# A program that measures the speed between different socket based 
# and multiprocessing object based functions

# highLevel function
'''
- Creates a child process that uses a mp obj to pass data to main process
- Main and child will pass data back and forth in a loop with a timer that 
    begins when loop begins, and ends when loop finishes
- returns: ratio number of 1-way transfer / time difference
'''

# lowLevel function
'''
- Creates a child process that uses a socket to pass data to main process
- loop and timer...
- return : ratio
'''

# data sent back and forth is an int. Intialized as 0 in main, gets inc, then sent
# loops 10,000 times 
# EC appends to a list instead of incrementing. Main appends 0 while child appends 1. Hint --> pickle the list

### used lists for EC ###

import platform
import multiprocessing as mp
import socket
import time
import pickle   # required to send lists via socket

TWOWAYLOOP = 300    # number of tests we want to do starting from main. x2 for number of one way transfers

def highLevel():
    '''creates a child processes that uses a multiprocessing obj to 
    pass data back to this main process. Returns ratio of number of 
    one-way transfer / time difference'''

    ### highLevel function via Multiprocessing Object ###

    sendQ = mp.Queue()     # sendQ in main, but recvQ in child
    recvQ = mp.Queue()     # recvQ in main, but sendQ in child

    ## create child thread ##
    HLchildP = mp.Process(target=highLevelChild, args=(sendQ, recvQ), name='highLevel')

    data = []    # intialize for try/except test
    data.append(0)

    HLchildP.start()      # start highLevel child process.

    ## send first increment and see if returned value is 2. ##
    ## if not raise exception and exit program              ##
    try:
        sendQ.put(data)
        data = recvQ.get()
        if data != [0,1]:
            raise(ValueError)
    
    except:
        print('Main did not receieve the correct value.\nNow Exitting Program...')
        sendQ.put(0)        # so hLchildP does not linger after system exit. finishes process
        HLchildP.join()
        raise(SystemExit)

    # reintialize data
    data = []

    highStart = time.perf_counter()     # start timer right before loop
    
    for loop in range(TWOWAYLOOP):           # loop 300 times
        data.append(0)          # appends 0 to list
        sendQ.put(data)         # send to child
        data = recvQ.get()      # receive from child

    highEnd = time.perf_counter() - highStart   # finish timer after loops are done    
    highRatio = TWOWAYLOOP * 2 / highEnd        # ratio for # of one-way data transfers / time diff

    sendQ.put(0)        # signal to child process to exit loop
    HLchildP.join()     # end highLevel child process

    # verify return data is correct and raise exception if it's not correct
    try:
        if not (len(data) == TWOWAYLOOP * 2 and data[len(data) - 1] == 1):
            raise(ValueError)
    except ValueError as e:
        print('The final expected data is incorrect. Program now shutting down...')
        raise(SystemExit)
    # print(len(data))

    return highRatio

def highLevelChild(recvQ, sendQ):
    '''serves as a child process to mp obj to receive data, 
    increment, and pass back to main process. receives via
    recvQ and places appended list back via sendQ'''

    while True:
        data = recvQ.get()
        if data == 0:       # flag to end child process
            break
        data.append(1)
        sendQ.put(data)     # grab list from queue, append, and place back into shared data


def lowLevel():
    '''creates a child process (server) that uses a socket to 
    pass data back to this main process. Returns ratio of number of
    one-way transfer / time difference''' 
    ### lowLevel function via Socket ###

    event = mp.Event()      # insurance setting up for client connection
    LLchildP = mp.Process(target=lowLevelChild, args=(event,))
    LLchildP.start()

    ## CLIENT ##
    clientHost = '127.0.0.1'
    clientPort = 5551

    event.wait()      # when server is finished setting up, create socket connection with client 
    event.clear()

    with socket.socket() as s :
        s.connect((clientHost, clientPort))
        
        data = []
        data.append(0)
        b = pickle.dumps(data)  # must convert list to binary before sending
        s.send(b)

        try:
            fromServer = s.recv(1024)       # test to make we receive correct data form server
            data = pickle.loads(fromServer) # unpickle binary to python obj
            if data != [0,1]:         # if 1 was not appended to list, raise exception and exit prog
                raise(ValueError)

        except ValueError as e:
            print('Main did not receieve the correct value.\nNow Exitting Program...')
            s.send('0'.encode('utf-8'))     # shut down server
            LLchildP.join()                 # end child process (lowLevel)
            raise(SystemExit)

        data = []   # reintialize list

        lowStart = time.perf_counter()    # start timer right before the loops

        for loop in range(TWOWAYLOOP):
            data.append(0)                              # append to list
            b = pickle.dumps(data)                      # pickle list
            s.send(b)                                   # send data to child (server)

            fromServer = s.recv(2048)                   # receive binary from child NOTE: increased size of packets to fit larger lists
            data = pickle.loads(fromServer)             # convert binary to list

        lowEnd = time.perf_counter() - lowStart     # finish time for lowLevel func
        lowRatio = TWOWAYLOOP * 2 / lowEnd          # ratio for # of one-way data transfers / time diff

        s.send(pickle.dumps(0))         # close connection
        s.shutdown(socket.SHUT_RDWR)    # since last call in loop has data delivery associated (OSError: Address already in use), 
                                            # must call above statement so socket doesn't linger
        LLchildP.join()                 # end child process

        # verify return data is correct and raise exception if it's not correct
        try:
            if not (len(data) == TWOWAYLOOP * 2 and data[len(data) - 1] == 1):
                raise(ValueError)
        except ValueError as e:
            print('The final expected data is incorrect. Program now shutting down...')
            raise(SystemExit)

        # print(len(data))
        return lowRatio

def lowLevelChild(event):
    '''serves as a child process using sockets to send and receive
    data. Acts as a server. Main acts as client'''

    ## SERVER ##
    serverHost = 'localhost'
    serverPort = 5551

    with socket.socket() as s :
        s.bind((serverHost, serverPort))
        s.listen()
        event.set()     # make sure server is set up before sending messages to and from main process (client)

        (conn, addr) = s.accept()
        # print('Server-Client Connection success!')
        while True:
            fromClient = conn.recv(2048)        # increase to 2048 bytes to accommadate larger lists
            data = pickle.loads(fromClient)     # unpickle to load list
            if data == 0:
                # print('Server shutting down')
                break

            data.append(1)          # append 
            b = pickle.dumps(data)  # pickle
            conn.send(b)            # send back


if __name__ == '__main__':
    '''main for running program. Also acts as main process and client for socket. 
    In this format to set this top module as mp_main before spawning child processes'''

    print('\nPlatform: ', end='')    
    print(platform.system())        # name of os

    print('Number of cores: ', end='')
    print(mp.cpu_count())           # number of cpu cores on machinee
    print('Values are repsresented in one-way transfers per second')
    print()

    # run 3 tests
    for tests in range(3):  
        
        multProcObj = highLevel

        highRatio = highLevel()
        lowRatio = lowLevel()

        print("{} {:>16.0f}".format(multProcObj, highRatio) )  
        print("{:<35} {:>16.0f}\n".format("Socket", lowRatio))


'''
CONCLUSION:

Sockets outperformed multiprocessing objects in data transfer in each test (close to 2.5x).
Moving data by the multiprocessing object was slower, because I/O operations between process,
mp.Queue, and process was segmented into separate tasks. Loaded and unloaded data form 
mp.Queue also takes some overhead. However, with sockets, processes form a direct connection
between each other thereby directly transfering data. 
'''