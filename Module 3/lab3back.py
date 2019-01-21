## James Pham and Nick Lewis ##
### CIS 41B : lab3back ###

# this module scrapes data from Fandango movie reviews and stores 
# them in 2 different files and stores in data base:

#   pickle
#   JSON
#   SQLite (DB)

import requests
from bs4 import BeautifulSoup
import re

import pickle
import json

import sqlite3

pickeFile = 'fandangoData.pkl'
JSONFile = 'fandangoData.json'

class FandangoData:
    '''Class that scrapes data from Fandago Movie Review Page and stores data in various formats'''

    def __init__(self):
        '''constructor: makes a request to https://www.fandango.com/movie-reviews
        and stores in 3 different database files'''

        self._movieData = []    # list of dictionaries. formatted {title, fan rating, release date, genre}

        mainPage = requests.get('https://www.fandango.com/movie-reviews')       # url Response object (html page)
        soup = BeautifulSoup(mainPage.content, 'lxml')                          # organize with BeautifulSoup for easier data retrieval

        for tableRow in soup.find_all( 'tr', class_='reviews-row'):   # loop thru each table row element with class reviews-row
            
            ## Title Extraction ##
            linkTag = tableRow.find('a')                        # link element
            title = re.sub(" Review", "", linkTag.get_text())   # clip off "Review" in text portion of link element

            ## Star Rating Extraction ##
            starCount = 0                       # stores the fan rating
            for fullStar in tableRow.find_all('span', class_='star-icon full'): # class for full star
                starCount += 1
            if tableRow.find('span', class_='star-icon half'):                  # class for half star. No need for loop, need to check instance for just one instance
                starCount += 0.5

            link = linkTag['href']  # link to movie review. Will be used to in another request to obtain release date & genre

            subPage = requests.get(link)                            # get new request for sublink
            subSoup = BeautifulSoup(subPage.content, 'lxml')        # create soup format for HTML subpage

            ## Release Date and Genre Extraction ##
            # releaseDate = subSoup.find('li', class_='movie-details__release-date').get_text()

            ## Genre Extraction ##
            movieDetailList = subSoup.find('ul', class_='movie-details__detail')
            liCount = 1

            for li in movieDetailList.find_all('li'):
                if (liCount == 2):                      # Release date is the 2nd list item of ul
                    releaseDate = li.get_text()
                elif(liCount == 4):                     # Genre is the 4th list item of ul
                    genre = li.get_text()
                liCount += 1

            record = [title, starCount, releaseDate, genre]
            self._movieData.append(record)    # add newly obtained movie data to instance variable

        self._movieData[8][3] = 'N/A'   # hard code this data. replace '\n\n\n\n\n' with 'N/A'

        self._toPickle()    # write to pickle file
        self._toJSON()      # write to JSON file

    def _toPickle(self):
        '''stores data in pickle format'''
        pickle.dump(self._movieData, open('fandangoData.pkl', 'wb'))

    def _toJSON(self):
        '''stores data in JSON format'''
        with open('fandangoData.json', 'w') as fh:
            json.dump(self._movieData, fh, indent=3)


class SQLiteDB:
    '''our database that while communicate with our front-end to relay data (lab3front.py)'''

    def __init__(self, filename):
        '''sets up the DB. This particular one will accept JSON'''

        try:
            with open(filename, 'r') as fh:
                movieData = json.load(fh)
        except IOError:
            print('File not found. Now exiting')
            raise(SystemExit)

        conn = sqlite3.connect('fandangoData.db')   # connect / create db 
        cur = conn.cursor()                         # set up DB for sequel commands

        cur.execute('DROP TABLE IF EXISTS Genre') # start with table without foreign keys. Only have 1 in this DB 
        cur.execute('''CREATE TABLE Genre(
                        id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                        genre TEXT UNIQUE ON CONFLICT IGNORE)''')

        cur.execute('DROP TABLE IF EXISTS MoviesDB')  # create central/primary table
        cur.execute('''CREATE TABLE MoviesDB(
                        title TEXT,
                        rating REAL,
                        date TEXT,
                        genre_id INTEGER)''')

        for record in movieData:
        # insert records into table beginning with foreign table Genre

            ###  INSERTION AT FOREIGN TABLE  ###
            cur.execute('''INSERT INTO Genre (genre) VALUES (?)''', (record[3],) )  # insert genre name into Genre table
            cur.execute('SELECT id FROM Genre WHERE genre = ?', (record[3],) )     # obtain matching if of genre
            genre_id = cur.fetchone()[0]    # fetch selected item from DB, choose first elem to remove from returned tuple

            ###  INSERTION AT CENTRAL TABLE  ###
            cur.execute('''INSERT INTO MoviesDB
                            (title, rating, date, genre_id)
                            VALUES (?,?,?,?)''', (record[0], record[1], record[2], genre_id,))

        conn.commit()   # finish creating DB
        conn.close()    # and close out connection


# FandangoData()          # produces JSON and pickle file
# SQLiteDB(JSONFile)      # creates database from JSON file