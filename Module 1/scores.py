# CIS 41B #
# By: James Pham #

### Scores module ###

# Class that reads data from a file of scores and lets the user selectively print the data

import collections
import operator #for using greater than or less than operator from module 


def printName(func):
    '''Decorator. Prints function/method name before running the method
    used in methods 2 (printByTotal) and 4 (printFreq). Note my 4th method
    is supposed to be the 3rd function'''
    def wrapper(*args, **kwargs):
        print(str(func.__name__))
        func(*args, **kwargs)    
    return wrapper

class Scores:
    '''Scores class - reads data from a file and lets user selectively print data'''

    def __init__(self):
        '''constructor - asks user to filename. opens user input-ed filename. intializes instance variables'''
        fileName = input('Please enter the file name: ')
        print() #extra line space after input
        self._scoresDict = self._readFile(fileName)

    def _readFile(self, fileName):
        '''reads in file and stores countries and scores in a (blank) data structure'''
        try:
            with open(fileName) as inFile:
                
                #parsing and converting text into 2d list
                dataList = [line.strip().split() for line in inFile]    #currently in two dimensions. countries in first row
                # print(dataList)

                #converting 2d list into dictionary
                #using defaultdict. values will be list
                scoresD = collections.defaultdict(list)

                for row in range( 1, len(dataList) ):   #will only iterate through 2nd to last row. first row will be key
                    for col in range( 0, len(dataList[row]) ):  #add every column
                        scoresD[dataList[0][col]].append( int(dataList[row][col]) ) #the country abbrev (first row, respective col) will add appropriate data
                # print(scoresD)
                
                return scoresD

        #if file fails to open, we exit program via raising SystemExit to driver
        except IOError as e:
            print(str(e), '. Program is now shutting down.')
            raise(SystemExit)

    @printName
    def printByTotal(self):
        '''sort counrties by total score in ascending order. prints out 
        countries and corresponding scores in specific format'''
        for k,v in sorted( self._scoresDict.items(), key = lambda t: sum(t[1]) ):
            print("{:5s}:".format(k), end='')
            #more elegant way print? tried unpacking list in print but can't format individual list elem...
            #refer back in future, to update into a one liner if possible
            for elem in v:
                print("{:6d}".format(elem), end='')
            print()
    
    def printByLimit(self, limit, above):
        '''prints just the abbrev. of countries below or above the user define limit'''
        sign = operator.gt if above else operator.lt #ternary operator for deciding greater or less than
        # print(sign)
        result = [ k for k,v in self._scoresDict.items() if any(sign(elem, limit) for elem in v) ]
        print(*result)

    @printName
    def printFreq(self):
        '''prints out the frequency of each score in ascending order'''    
        freqD = collections.defaultdict(int)
        scores = sum( [v for k,v in self._scoresDict.items()], [] ) #flatten 2d list into 1d for easier iteration
                                                                    #second argument is [] 
        # print(scores)
        for num in scores:
            freqD[num] += 1

        for k,v in sorted(freqD.items()):
            print( '{:2d}:{:2d}'.format(k, v) )
        
    def printOne(self):
        '''prints one country and it's scores one at a time. scores will be in ascending order'''
        return ((k,*sorted(v)) for k,v in sorted(self._scoresDict.items()) )


# s = Scores()
# s.printByTotal()
# s.printByLimit(10, 'B')
# s.printFreq()
# n = s.printOne()

# print(next(n))
# print(next(n))
# print(next(n))
# print(next(n))
# print(next(n))