### James Pham && Nick Lewis ###
    # CIS 41B #

# Enrollment module. A class that accepts a csv file and creates two returns two different numpy array calculation 
# based on provided csv data

# Three Tasks:
# 1. Read Filename
# 2. Plot trend (total students vs year)
# 3. For one year plot the number of students in each age group

import csv
import numpy as np


'''DECORATOR'''
def showNums(func):
    def wrapper(*args, **kwargs):
        arrayReturned = func(*args, **kwargs)
        print('Array returned from method is: ', arrayReturned)
        return arrayReturned
    return wrapper
'''''''''''''''
'''''''''''''''
class Enrollment:
    '''a class that takes csv data and produces visual plots for data representation''' 
    def __init__(self, filename):
        '''constructor for Enrollment. Takes a filename as an argument'''
        try:
            with open(filename) as fh:
                reader = csv.reader(fh)
                
                tempList = [[int(elem) for elem in row] for row in reader]
                
                yearsList = tempList[0].copy()  # use first row from csv file and store as list
                                                # no need for array, will act as indexing, no need for calc with these values

                # convert to array first then, then store every row except the first in
                # a calculations array for data manipulation
                tempArr = np.array(tempList)
                calcArr = tempArr[1:len(tempList)]

        except IOError as e: 
            raise(e)
        
        self._calcArr = calcArr
        self._yearsList = yearsList
    
    # @showNums
    def enrollmentTrend(self, masterWin):
        '''Returns an array of total students from year to year. Will represent Y axis values
        in PlotWin class.'''

        totalStudents = self._calcArr.sum(0)

        ### all plt methods and associated variables are in lab2 PlotWin class ###

        return totalStudents
    
    @showNums
    def enrollmentByYear(self, year, masterWin):
        '''returns an list of age group enrollment for that year. Returned list that will be used as Y values for
        PlotWin.'''

        numGroups = 7   # number of age groups in csv file. Using 7 vs 8 because we are ignoring the last group (unknown)
        colIndex = (self._yearsList).index(year)   # column index that will be used to calculate age group totals from self._calcArr

        # used list comprehension with the sum of each array pattern. No need for array container because this is the final result needed for plotting
        yearTotals = [self._calcArr[num::8, colIndex].sum() for num in range(numGroups)]   # list that corresponds with age group totals for that year

        ### all plt methods and associated variables are in lab2 PlotWin class ###

        return yearTotals
            
    def getYears(self):
        '''returns a list of years. allows dynamic size of year options
        regardless csv file given. Acts as x axis for enrollmentTrend, and
        search index for enrollmentByYear. (Returns a list in order to use
        .index() method of List class)'''
        return self._yearsList


# def main():
#     x = Enrollment('students2.csv')
#     y = x.enrollmentByYear(2008, 't')
#     print(y)

# main()

### things to fix on REDO ### 

# use loadtxt ro read in data into np array. Don't need to read into a list of lists

# add plt back to the methods minus .show() method

# don't need to raise exception in the constructor

#