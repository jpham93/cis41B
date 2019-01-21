### James Pham ###
###   CIS41B   ###
# Lab 4 : Process #

# A GUI program that provides real time weather updates of Major College Towns/Cities in California
#   also demonstrates:
#       - REST 
#       - Multiprocessing. Program speed will be tested with process

import tkinter as tk                
import tkinter.messagebox as tkmb
import tkinter.filedialog
import requests     # REST api
import multiprocessing as mp  
import os
import time


## REST ##
APIKEY = 'c0ac390bc07fd8f76d79182fc3edf8f9'
ZIPLIST = [92093, 90013, 95192, 94132, 94720, 95064, 95819, 92697, 93940, 94544]
##########

class MainWin(tk.Tk):
    '''A list box window that stores weather information for select cities. Gives option to save selections made 
    to local disk'''

    def __init__(self, apiData):
        '''constructor for window. sets up widgets and instance variabels to store information'''
        super().__init__()      # call parent constructor of tk.Tk

        self._dataDict = apiData             # stores cities (key) and their current temperature and weather descriptions (value) in a nested dictionary
        self._selections = []

        ## MainWin details ##
        self.geometry('450x300+500+250')        # set 450x300 at starting point 500,250 of screen
        self.minsize(300,300)
        self.title('College Cities Weather App')

        ## center dialog button ##
        dialogB = tk.Button(self, text='Choose A City', command=self._dialogSpawn)     # has callback for creating dialog window
        dialogB.pack()

        ## list box frame ##
        lbFrame = tk.Frame(self)
        lbFrame.pack()

        scroll = tk.Scrollbar(lbFrame)
        self._listBox = tk.Listbox(lbFrame, height=14, width=45, yscrollcommand=scroll.set)     # stored as member variable. will add to it as user selects
        scroll.config(command=self._listBox.yview)

        self._listBox.grid()
        scroll.grid(row=0, column=1, sticky='ns')

        self.update()

        # ## run api calls ##
        # start = time.time()

        # for zipcode in ZIPLIST:
        #     self._restCall(zipcode)
        # print("Total elapsed time: {:.2f}s".format(time.time()-start))

        ## closing event ##
        self.protocol('WM_DELETE_WINDOW', self._saveData)

    def _dialogSpawn(self):
        '''call back for creating child dialog window'''
        
        dialogWin = DialogWin(self, self._dataDict.keys())  # dialog window. Pass only a list of keys to dialog window
        self.wait_window(dialogWin)

    # def _restCall(self, zipcode):
    #     '''REST call with zipcode. Data will be stored an passed to instance variable'''

    #     url = 'http://api.openweathermap.org/data/2.5/weather?zip='+ str(zipcode) + ',us&units=imperial&APPID=' + APIKEY

    #     page = requests.get(url)
    #     jsonDict = page.json()      # convert JSON to python dictionary format

    #     # take out needed info from json and store as dictionary for each city #
    #     city = jsonDict["name"]
    #     temp = int( round( jsonDict['main']['temp'] ) )
    #     sky = jsonDict['weather'][0]['description']

    #     # city will be key. value is information stored as dictionary
    #     self._dataDict[city] = {'temp' : temp, 'sky' : sky}

    def addCity(self, choice):
        '''Method for adding city weather to listbox'''
                
        if len(choice) > 0:     # if a selection was made (not None type)
            result = choice + ': ' + str(self._dataDict[choice]['temp']) + ' degrees, ' + self._dataDict[choice]['sky'] # resuling string
            self._listBox.insert(tk.END, result)     # add to list to be displayed in listbox
            self._selections.append(result)

    def _saveData(self):
        '''if listBox has some entries in it, then give user option to save'''
        filename = 'weather.txt'        # name of the file to be saved
        save = False                    # var used to check if user wants to save

        # prompt user to save if there one or more selections
        if len(self._selections) > 0: 
            save = tkmb.askokcancel('Save', 'Save your search in a directory of your choice?', parent=self)
        
        if save:    # if user confirmed then open window for user to save
            directory = tk.filedialog.askdirectory()            # path. user will chose
            fullPath = os.path.join(directory, filename)        # full path name to file

            with open(fullPath, 'w') as outfile:        # write to file
                for item in self._selections:
                    outfile.write(item+'\n')

            tkmb.showinfo(save, 'File ' + filename + ' will be saved in\n' + directory)     # show where user save their file

        self.destroy()


class DialogWin(tk.Toplevel):
    '''Dialog win that waits for user to add to listbox'''
    
    def __init__(self, master, cities):
        '''Constructor for dialogWin. Provides radio buttons for user to choose. Selection 
        returns weather updates + name of city'''

        super().__init__(master)    # call parent constructor of tk.Toplevel

        self._master = master
        self._cities = cities       # list of cities from MainWin. Dictionary of cities. Values are dictionary containing temp and sky description       


        ## disable master window ##
        self.grab_set()
        self.focus_set()
        self.transient(master)


        ## window specification ##
        self.geometry('175x250+650+250')
        self.title('Choose a city')


        ## radio button frame ##
        rbFrame = tk.Frame(self)
        rbFrame.pack()

        choiceVar = tk.StringVar()

        for city in self._cities:
            tk.Radiobutton(rbFrame, text=city, variable=choiceVar, value=city).grid(sticky='w')


        ## Select button ##
        selectB = tk.Button( self, text='Select', command=lambda : self._select(choiceVar.get()) )
        selectB.pack()    

    def _select(self, cityName):
        '''updates master window with selection. also closes dialog window'''

        self._master.addCity(cityName)    # have master window update list box
        self.destroy()      # close window after selection


### defined as regular function. Will not work with tkinter for multiprocessing ### 

def restCall(zipcode):
        '''REST call with zipcode. Data will be stored an passed to instance variable'''

        url = 'http://api.openweathermap.org/data/2.5/weather?zip='+ str(zipcode) + ',us&units=imperial&APPID=' + APIKEY

        page = requests.get(url)
        jsonDict = page.json()      # convert JSON to python dictionary format

        # take out needed info from json and store as dictionary for each city #
        city = jsonDict["name"]
        temp = int( round( jsonDict['main']['temp'] ) )
        sky = jsonDict['weather'][0]['description']

        # return as tuple to later be put in a new dictionary in main() 
        return (city, temp, sky,) 



if __name__ == '__main__' : # additional child processes from program re-runs will be __multiprocessing_main__ (WINDOWS)
        
    ## using MAC ## 
    # Changing to spawn behavior #
    mp.set_start_method('spawn')

    ### Multiprocessing done outside of Windows obj ###

    dataDict = {}
    procs = []
    
    pool = mp.Pool(processes=10)

    ## run api calls ##
    start = time.time()

    results = pool.map(restCall, ZIPLIST)

    print("Total elapsed time: {:.2f}s".format(time.time()-start))

    for t in results:   # from the pool call, iterate to get each returned tuple and put in dictionary
        dataDict[ t[0] ] = { 'temp' : t[1], 'sky' : t[2] }

    # output queue to store data from mp calls
    # outputQ = mp.Queue()

    # for zipcode in ZIPLIST:
    #     p = mp.Process(target=restCall, args=(zipcode, outputQ,))
    #     # restCall(zipcode)
    #     procs.append(p)
    #     p.start()

    # for p in procs:
    #     p.join()

    # for zips in ZIPLIST:    # retrieve data from mp queue and enter them in dictionary
    #     t = outputQ.get()
    #     dataDict[ t[0] ] = { 'temp' : t[1], 'sky' : t[2] }

    app = MainWin(dataDict) # pass dictionary back to parent window
    app.mainloop()
