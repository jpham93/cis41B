# CIS 41B #
# By: James Pham #

### DRIVER module ###

# Client that runs scores module. Allows user to choose from a menu and exec desired program commands.

import scores
import re   #used for validating A or B choice in printLimit()

def main():
    '''interface for user. will prompt user for options 1-5. Exits upon option 5. Will
    re-ask user if repsonse invalid'''
    scoresObj = scores.Scores()
    menu(scoresObj)

def menu(score):
    '''Accepts a score obj in order to pass through functions. 
    Ask users to choice from 1-5. if invalid choice, will reprompt user. 
    Will exec task depending on choice.'''

    done = False

    while not done:

        #dictionary of functions. Key is chosen by user and function call is done in line 39
        choiceDict = {1: printAll, 2: printLimit, 3: printOneByOne , 4: printFrequency}

        print('Please select form the following choices:\n\
        1. Print total score\n\
        2. Print by limit\n\
        3. Print one by one\n\
        4. Print score frequency\n\
        5. Exit\n')

        try:
            choice = int(input('~ '))
            print()
            choiceDict[choice](score)
            print()
        
        except ValueError:  #exception for non-int value
            print('Invalid choice. Please Try Again.\n')
            print() #extra line space since it comes before KeyError exception
            
        except KeyError:    #exception for options outside of 1-4. 5 is special case --> exiting loop
            if choice == 5: #handles 5 for exiting
                print('Now exiting program...\n')
                done = True
            else:
                print('Invalid choice. Please Try Aagin.\n')



def printAll(obj):
    '''calls printByTotal method of Scores obj'''
    obj.printByTotal()

def printLimit(obj):
    '''prompts user for limit and above or below.
    then it displays the countres that matches criteria'''
    
    done = False

    while not done:
        try:
            limit = int(input('Please enter the limit: '))
            choice = input('Please choose a for above or b for below: ').upper() #default to uppercase to account for case sensitivity
            3
            if not re.match("^[AB]$", choice):  
                raise(ValueError) 

            #ternary. above is true if choice is A. Originally just used 'A' and 'B'
            #as argument in printByLimit, but converted into bool because of rubric.   
            above = True if choice == 'A' else False 

            print()
            obj.printByLimit(limit, above)
            done = True

        except ValueError:
            print()
            print('Invalid choice. Please try again.')
            print()

def printOneByOne(obj):
    '''prints one by one with the returned generator. Continues when user 
    enters "ENTER" alone, quits when user hits any other key'''

    gen = obj.printOne()
    done = False

    while not done:
        try:
            stringCheck = input('Hit ENTER to see the next country, or any other key with enter to exit: ')
            print()
            #end loop if user doesn't hit enter by itself
            if len(stringCheck) > 0:
                break

            print(*(next(gen))) # unpack because generator is in tuple form
            print()

        except StopIteration:
            print('No more countries to show...')
            print()
            done = True

def printFrequency(obj):
    '''prints the frequency of each score for all countries. sorted in ascending order'''
    obj.printFreq()
            

main()