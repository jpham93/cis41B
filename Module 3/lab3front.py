## James Pham and Nick Lewis ##
### CIS 41B : lab3front ###

# fetches data from database and turns into a GUI movie guide. GUI provides 
# allows users to search by genre or rating. Selected movie will display information.


import tkinter as tk
import tkinter.messagebox as tkmb
import sqlite3
import numpy as np      # used for half step in rating values.

DBFile = 'fandangoData.db'

class MovieRecord:
    '''MovieRecord objects that retrieves table in a python format. Will maintain same format as as DB tables'''

    def __init__(self, dbFile):
        '''reads in data from DB and stores it in data structures that resembles the tables'''

        self._genreList = []
        self._movieList = []

        conn = sqlite3.connect(dbFile)  # connect to existing db
        cur = conn.cursor()             # set up for sql commands

        ## retrieve genre table first ##
        for record in cur.execute('SELECT genre FROM Genre'):
            self._genreList.append(record[0])

        ## retrieve central table ##
        for record in cur.execute('SELECT * FROM MoviesDB'):
            newRecord = list(record)                        # convert tuple to list for mutation
            genre = self._genreList[ newRecord[3] - 1 ]     # retrieve genre from list. Must - 1 because of 0 position index
            newRecord[3] = genre                            # replace foreign key with actual genre name
            self._movieList.append(newRecord)               

        conn.close()        


    def getMovieList(self):    
        '''returns the movie list'''
        return self._movieList

    def getGenreList(self):
        '''returns the genre list'''
        return self._genreList


class MainWin(tk.Tk):
    '''main window. presents genre and ratings categories that provides a dialog (child) window. Depending on 
    dialog window choice, MainWin's listBox will fill up'''

    def __init__(self):    
        '''creates and retrieves data from MovieRecord object'''
        super().__init__()  

        ## create dataObj and read it into instance variables ##
        dataObj = MovieRecord(DBFile)
        self._genreList = dataObj.getGenreList()
        self._ratingsList = []
        self._movieList = dataObj.getMovieList()

        self._option = ""                       # will detemine which list to use depending on button chosen. genre or rating
        self._displayList = []                  # listbox choice will be used key to retrieve movie title that then


        for rating in np.arange(5.0, -0.5, -0.5):   # create ratings list to pass to dialog window
            if rating > 1:
                self._ratingsList.append(str(rating) + ' stars')
            else:
                self._ratingsList.append(str(rating) + ' star')


        ## set MainWin specs ##
        self.geometry('450x300+500+250')        # set 400 by 600 at 400x 250y
        self.minsize(300,300)
        self.title('Movie Guide')


        ## button group ##
        buttonFrame = tk.Frame(self)
        buttonFrame.pack()

        genreButton = tk.Button(buttonFrame, text='Genre', command=lambda : self._callDialogWin(self._genreList, 'genre'))
        ratingButton = tk.Button(buttonFrame, text='Rating', command=lambda : self._callDialogWin(self._ratingsList, 'rating'))

        genreButton.grid()
        ratingButton.grid(row=0, column=1)
        

        ## listbox + scroll bar ##
        choiceFrame = tk.Frame(self)        # frame for pack() orientaion. allows child widgets for grid() organization
        choiceFrame.pack()

        scroll = tk.Scrollbar(choiceFrame)              # create scroll for listbox
        self._listBox = tk.Listbox(choiceFrame, height=14, width=45, yscrollcommand=scroll.set)        # need to be instance var to be manipulated in another method                       
        scroll.config(command=self._listBox.yview)      # vertical scrollbar

        self._listBox.grid()
        scroll.grid(row=0, column=1, sticky='e')
        
        self._movieLabel = tk.Label(self)
        self._movieLabel.pack()

        self.bind('<<ListboxSelect>>', self._updateMovieLabel)      # bind chosen movie with a label providing movie details 
                                                                    # via callback

        self.protocol('WM_DELETE_WINDOW', self._close)

    def _callDialogWin(self, choiceList, option):
        '''create dialogWin with appropriate options'''

        self._option = option
        DialogWin(self, choiceList, option)


    def fillListBox(self, choiceNum):
        '''creates list of choices based on user choice from dialog window'''

        ### movieRecord format : [ [title, rating, releaseData, genre] , [...], ...] ####

        ## delete from listBox if there is previous data ##
        self._listBox.delete(0, tk.END)

        selectionStr = ''   # will be used to fill movieLabel while user is choosing. Informs user of category chosen

        ## list of movies that match genre #
        if self._option == 'genre':
            genre = self._genreList[choiceNum]                                                          # use genre to find movies that match criteria.
            self._displayList = [record[0] for record in filter(lambda l : l[3] == genre, self._movieList)]     # filter through each record and select lists that contain genre            

            selectionStr = "Genre: " + self._genreList[choiceNum]   # create genre name for bottom description label

        ## list of movies that match rating ##
        else:
            rating = float(self._ratingsList[choiceNum][0:3])       # extract the float value from rating list.                                                                    # index number of rating List == rating / 2
            self._displayList = [record[0] for record in filter(lambda l : l[1] == rating, self._movieList)]    # filter through moviesList and create new list matching rating number

            selectionStr = str(self._ratingsList[choiceNum])

            
        self._listBox.insert( tk.END, *self._displayList )      # insert choices into Listbox
        self._movieLabel.config(text=selectionStr)              # update label with dialog window choice


    def _updateMovieLabel(self, event):
        '''updates moveLabel current movie selection form listBox'''
        
        try:
            listIndex = self._listBox.curselection()[0]   # tuple of selected title index
        except:
            return None   # work around for empty listbox. return empty string

        selectedMovie = self._displayList[listIndex]  # movie title chosen

        record = list(filter(lambda x : x[0] == selectedMovie, self._movieList))    # find movie details in movieList again and store
        
        movieDetails = record[0]    # flatten out 2D list. for some reason couldn't find a way to unpack above filter object

        result = str(movieDetails[1]) + ' stars, released: ' + movieDetails[2] + ' genre: ' + movieDetails[3]    # concactenate string for bottom label

        self._movieLabel.config(text=result)    
        
    def _close(self):
        '''closes window properly. will give a message box warning first'''

        tkmb.askokcancel('Quit', 'Are you sure you want to quit?', parent=self)        
        self.destroy()


class DialogWin(tk.Toplevel):
    '''dialog window object. Called from MainWin. Will take user choice and fill mainWin choices'''
    
    def __init__(self, master, choiceList, option):
        '''makes dialog window. displays choices depending on button clicked from main window'''
        super().__init__(master)        # inherits from Toplevel, and passes master argument from constructor to inherited constructor

        self._choiceList = choiceList   # list of choices passed on from master window. Can be genreList or ratingList

        ## center window as best as we can ##
        self.geometry('+600+250')
        self.minsize(150,200)

        ## save master win. will be used to pass user choice back to main window ##
        self._masterWin = master

        # disable master window. Keep focus on current window #
        self.grab_set()
        self.focus_set()
        self.transient(master)  # keep current window child to master

        self._addWinDetails(option)

        ## set DialogWin specs ##

    def _addWinDetails(self, option):
        '''creates menu choices and layout based on which button/option was selected'''

        ## Radiobuttons ##
        choiceVar = tk.IntVar(0)
        choiceNum = 0

        ## title for dialog Window depeneding on option var ##
        self.title('Genre') if option == 'genre' else self.title('Rating')

        ## create Radiobutton for dialogWindow ##

        if option == 'genre':   # different formatting for genre dialog menu. because it doesn't center as nicely as ratings
            F = tk.Frame(self)

            for choice in self._choiceList:     
                tk.Radiobutton( F, text=choice, variable=choiceVar, value=choiceNum ).grid(sticky='w')     # try side=tk.BOTTOM later
                choiceNum += 1

            F.pack()

        else:
            for choice in self._choiceList:     
                tk.Radiobutton( self, text=choice, variable=choiceVar, value=choiceNum ).pack()     # try side=tk.BOTTOM later
                choiceNum += 1

        tk.Button( self, text='OK', command=lambda : self._choose(choiceVar.get()) ).pack()     # takes the choiceVar selected by radiobutton
                                                                                                # will pass it back to mainWindow

    def _choose(self, choiceNum):
        '''confirms selection and creates data for listbox in mainWindow'''
        self._masterWin.fillListBox(choiceNum)
        self.destroy()


def main():
    '''DRIVER TO TEST APP'''
    app = MainWin()
    app.mainloop()

main()


### FIXES ON REDO ###

# update label via string var
# sticky=ns so listBox stretches with frame/window

# fetch data from DB in real time, don't just store then work with local data. 
############################ ABOVE IS A BIG FIX ##############################
