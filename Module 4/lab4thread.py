### James Pham ###
###   CIS41B   ###
# Lab 4 : Thread #

# A GUI program that provides real time weather updates of Major College Towns/Cities in California
#   also demonstrates:
#       - REST 
#       - threading. Program speed will be tested with threads

import tkinter as tk                
import tkinter.messagebox as tkmb
import tkinter.filedialog
import requests     # REST api
import threading
import os

import time

## REST ##
APIKEY = 'c0ac390bc07fd8f76d79182fc3edf8f9'
ZIPLIST = [92093, 90013, 95192, 94132, 94720, 95064, 95819, 92697, 93940, 94544]
##########

class MainWin(tk.Tk):
    '''A list box window that stores weather information for select cities. Gives option to save selections made 
    to local disk'''

    def __init__(self):
        '''constructor for window. sets up widgets and instance variabels to store information'''
        super().__init__()      # call parent constructor of tk.Tk

        self._dataDict = {}             # stores cities (key) and their current temperature and weather descriptions (value) in a nested dictionary
        self._selections = []           # stores user selections in a list of strings (to be written in a file)

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

        self.update()   # pull up window after widgets are set up. gives a feel for faster load. don't have to wait for API GET

        ## run api calls ##
        start = time.time()

        threads = []
        for zipcode in ZIPLIST:
            t = threading.Thread(target = self._restCall, args = (zipcode,))
            threads.append(t)
            t.start()
            # self._restCall(zipcode)

        for t in threads:
            t.join()

        print("Total elapsed time: {:.2f}s".format(time.time()-start))

        ## closing event ##
        self.protocol('WM_DELETE_WINDOW', self._saveData)


    def _dialogSpawn(self):
        '''call back for creating child dialog window'''
        
        dialogWin = DialogWin(self, self._dataDict.keys())  # dialog window. Pass only a list of keys to dialog window. Names will be used for button and value
        self.wait_window(dialogWin)

    def _restCall(self, zipcode):
        '''REST call with zipcode. Data will be stored an passed to instance variable'''

        url = 'http://api.openweathermap.org/data/2.5/weather?zip='+ str(zipcode) + ',us&units=imperial&APPID=' + APIKEY

        page = requests.get(url)
        jsonDict = page.json()      # convert JSON to python dictionary format

        # take out needed info from json and store as dictionary for each city #
        city = jsonDict["name"]
        temp = int( round( jsonDict['main']['temp'] ) )
        sky = jsonDict['weather'][0]['description']

        # city will be key. value is information stored as dictionary
        self._dataDict[city] = {'temp' : temp, 'sky' : sky}

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

        # prompt user to save if there is one or more selections
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


    

def main():
    app = MainWin()
    app.mainloop()

main()    


'''
It took about 2.22s, 1.95s, 1.76s on 3 different try when making the 10 API calls without threading or processing.
With multithreading, it took only 0.45s, 0.33s, and 0.20s for the calls to be finished.
With multiprocessing, it took 0.87s, 0.98s, and 0.82s for the calls to be finished.

No Threading/Processing:
    Pros:
        - no additional code to the program
        - uses less resource memory and hardware (cpu, cache, etc.)
    Cons:
        - have to wait longer, can be very costly for a large program.

Threading:
    Pros:
        - very fast. The winner of the three in this program.
        - not as memory intensive as MP since memory is shared
    Cons:
        - can be limited since it is not truly MP. only uses one CPU core

Multprocessing:
    Pros:
        - faster than the original runs
        - can do true parallel processing
    Cons:
        - does not work with tkinter
        - can cause a lot of overhead since each independent process has its own memory space
'''
