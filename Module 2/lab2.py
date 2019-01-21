### James Pham && Nick Lewis ###
    # CIS 41B #

# GUI interface for user to choose graphical display based on
# the enrollment module and given csv file 

# there are 3 interdependent GUI classes

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

import tkinter.messagebox as tkmb

import enrollment

FILENAME='students2.csv'    # works for both files

class MainWin(tk.Tk):
    
    '''App class. Allows user to create a GUI object that graphs csv files of CC enrollment data.'''

    def __init__(self, fname):
        '''Constructor. creates an enrollment object that graphs enrollment trend year by year and
        age group enrollments per year. Also provides GUI for user to pick graph type, and year if 
        necessary.'''
        super().__init__()

        self.geometry('400x100')
        self.title('California Community College Enrollment Data')

        self._description =tk.Label(self, text='This application shows the year by year trend of student\n\
        enrollment in California CC\'s')
        self._description.pack()

        try:
            self._enrollmentObj = enrollment.Enrollment(fname) # enrollment obj with plot methods. will be passed to other window obj
        except:
            tkmb.showerror('Invalid File', 'The following file name: ' + fname + ' is invalid. Program now shutting down.', parent=self)
            raise(SystemExit)

        self._choiceFrame = tk.Frame(self)
        self._choiceFrame.pack()

        self._trendButton = tk.Button(self._choiceFrame, text='Enrollment Trend', command=lambda : self._totalEnrollment(self._enrollmentObj))
        self._byAgeButton = tk.Button(self._choiceFrame, text='Enrollment by Age', command=lambda : self._enrollByYear(self._enrollmentObj))

        self._trendButton.grid(row=0, column=0)
        self._byAgeButton.grid(row=0, column=1)

        self.protocol('WM_DELETE_WINDOW', self._endProgram)

    def _totalEnrollment(self, obj):
        '''callback for enrollmentTrend method call. Creates a plot window obj with obj.enrollmentTrend()'''
        PlotWin(self, obj, 1)

    def _enrollByYear(self, obj):
        '''creates a dialog window obj that lets the user choose which year
        to plot enrollment by age groups for that year.'''     
        DialogWin(self, obj)

    def _endProgram(self):
        '''callback for ending program'''
        self.quit()
        self.destroy()

class DialogWin(tk.Toplevel):
    '''DialogWin Class: its own window for selecting the year and plotting a bar graph (a child window)'''

    def __init__(self, masterWin, obj):
        '''constructor: inherits Toplevel constructor and instantiates widgets as member variables'''
        super().__init__()

        self._enrollmentObj = obj   # ernollment obj for calling correct plot method

        self.geometry('300x200')

        # disables main window after dialog window pops up
        self.grab_set()
        self.focus_set()
        self.transient(masterWin)

        # label for dialog window
        self._dialogLabel = tk.Label(self, text='Select the year to view enrollment\n numbers per age group.')
        self._dialogLabel.pack()

        ## Separate radio button organization from label

        self._choiceFrame = tk.Frame(self)      
        self._choiceFrame.pack()

        # list of years. Will be used to create a radio button with its corresponding year
        self._years = self._enrollmentObj.getYears()
        self._radioList = []    # stores the creation of radio buttons in a list
                                # flexibility avoids hard coding

        self._controlVar = tk.IntVar()    # variable for radiobutton selection

        # create radio buttons based on the years provided. (Obtained with getYears method from Enrollment module)
        for year in self._years:
            self._radioList.append( tk.Radiobutton(self._choiceFrame, text=str(year), variable=self._controlVar, value=year) )

        count = 1

        for i in range( len(self._radioList) ):            

            # split year choices in two different columns

            if len(self._radioList) / count >= 2:
                self._radioList[i].grid(row=i, column=0)
            else:
                self._radioList[i].grid(row=(i - len(self._radioList) // 2), column= 1) 

            count += 1
            
        # button that selects the radioButton choice and prints graph
        selectButton = tk.Button( master=self, text='OK', \
        command=lambda : self._byAgeCallback( self, self._enrollmentObj, 2, self._controlVar.get()) )   # self refers to DialogWin to act as masterWin for PlotWin

        selectButton.pack()

    ### edits: ###
    # supposed to close/destory window after selection via self.protocol

    def _byAgeCallback(self, masterWin, o , methodNum, year):
        '''creates PlotWin objects after year selections.
        masterWin: so that FigureCanvasTkAgg can refer back to this class as master
        o: is object passed from MainWin so that Plot win Can refer to
        methodNum: tells plot window which enrollment obj method to call=
        year: is the that will be used to plot enrollment by age groups
        '''
        
        PlotWin(self, o, methodNum, year)



class PlotWin(tk.Toplevel):
    '''creates a plot window depending on the Enrollment Method chosen'''
    def __init__(self, masterWin, obj, methodNum, year=0):
        super().__init__()  # add master
        self._enrollmentObj = obj
        self._year = year   # used for passing year in enrollment by age

        self._fig = plt.figure(figsize=(8,4))

        if methodNum == 1:
            xData = self._enrollmentObj.getYears()
            yData = (self._enrollmentObj.enrollmentTrend(masterWin) / 1000000)
            graphTitle = 'Enrollment By Year'
            xLabel = 'Years'
            yLabel = 'Amount of Students (Per Million)'
            plt.plot(xData, yData, '-*r', label = 'Students')
            plt.legend(loc='best')

        elif methodNum == 2:
            xData = ['<19', '20-24', '25-29', '30-34', '35-39', '40-49', '50+']
            yData = self._enrollmentObj.enrollmentByYear(self._year, masterWin)
            graphTitle = 'Enrollment By Age Groups in ' + str(self._year)
            xLabel = 'Age Groups'
            yLabel = 'Amount of Students' 
            plt.bar(xData, yData)

        plt.title(graphTitle)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack()
        self._canvas.draw()
        
        ### future edits ###
        # plot stuff is supposed to be in enrollment. only keep canvas things inside of methods


def main():

    app = MainWin(FILENAME)
    app.mainloop()

main()

### need to have class for each window ###

'''
EXTRA CREDIT:
In 2008, the CA economy took a hard hit causing a lot of unemployment / lay-offs. In times of 
economic recession, people usually extend their higher education in the absense of employment. 
The enrollment trend plot verfies this with total enrollment being much higher in the 2008-2010
compared to now. In the age group bar plot, you can also see that the older age groups
enrollment numbers were more heavily influenced by the 2008 recession.

'''

'''
class mainWin(tk.Tk):
    def __init__(self):
        super().__init__():
        (all widgets)
        instance variables

    def callback1():
    
    def callback2(): 

'''

### Problems to fix in REDO ###

# super().__init__(master) --> need master

# window should close when user hits okay in dialog window via self.destroy callback

# remove plotting methods and just keep canvas. add plotting back to 