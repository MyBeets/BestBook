#!/usr/bin/env python

import flask
from flask import request, redirect

#hashlib setup
import hashlib

#mongo
from mongo_script import *

#reference table
from relevancetable import RelevanceTable

#for testing the coord generator
#import matplotlib.pyplot as plt

exec(open("mongo_script.py").read())

#http://127.0.0.1:5000/ 

#global var definitions
unwantedChar = [' ', '{', '}', "'"]
length_scalar = 0.5
map_size_cap = 5
map_depth_cap = 10
#currentBook -- defined in func replace_current_book
#currentResults -- defined in func replace_current_results

# Create the application.
app = flask.Flask(__name__)


@app.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('index.html')


@app.route('/account/')
def account():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('account.html')

@app.route('/add/')
def add():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('add.html')

@app.route('/search/')
def search():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('search.html', link = "/search/results/")

@app.route('/book/', methods = ['POST'])
def book_main():
    book_id = (next(iter(request.form.keys())))
    result = search_current_results(book_id)
    replace_current_book(result)
    return flask.render_template('book.html', book = currentBook, length = len(currentBook['genres']))

@app.route('/author/', methods = ['POST'])
def author_main():
    author_id = (next(iter(request.form.keys())))
    result = search_current_results(author_id)
    return flask.render_template('author.html', author = result)

@app.route('/map/', methods = ['POST'])
def display_map():
    relevanceTable = generate_relevance_table(currentBook) #implement size
    #map_string = from_relevance_table_generate_map_as_string(relevanceTable)
    #print(map_string)
    print(str(relevanceTable))
    coordlist = relevanceTable.generate_coordinate_list()
    print(str(coordlist))
    map_string = relevanceTable.generate_mapping_string()
    print(map_string)
    
    """ mathplot visual representation for testing
    plt.plot(0, 0, 'bo')
    for e in coordlist:
        plt.plot(e[0], e[1], 'bo')
    plt.show()
    """
    return flask.render_template('map.html', book = currentBook, mapString = map_string)

@app.route('/error/')
def error_nonspecific():
    return flask.render_template('not-implemented.html')


"""
ROUTES FOR FUNCTIONS
"""
@app.route('/search/results/', methods = ['POST'])
def results():
    book_id = db_format(request.form['book_id'])
    search_results = db_search(db_format(book_id))

    temp = []
    for r in search_results:
            temp.append(r)

    replace_current_results(temp)

    if add_edge == True:
        changeLink = "/book/add_edge/"
        replace_add_edge(False)

    else: changeLink = "/book/"

    return flask.render_template('display_results.html', results = currentResults, link = changeLink)

@app.route('/search/authors/', methods = ['POST'])
def results_authors():
    author = db_format(request.form['author_name'])
    search_results = db_authorsearch(author)
    if not search_results:
        return flask.render_template('custom.html', customText = "looks like this author doesn't exist", title = "D:")

    temp = []
    for r in search_results:
            temp.append(r)

    replace_current_results(temp)

    return flask.render_template('display_authors.html', results = currentResults, link = '/author/')


@app.route('/add/add_book/', methods = ['POST'])
def add_book():
    if not loggedIn: return flask.render_template('custom.html', customText = "error. you're not logged in")
    
    title = request.form['title']
    author = request.form['author']
    genres = request.form['genres'].split(",")
    db_add_book(title, author, genres, [])
    return flask.render_template('custom.html', customText = "you've added a book :D", title = "congrats")


@app.route('/add/add_edge/', methods = ['POST'])
def add_edge():
    if not loggedIn: return flask.render_template('custom.html', customText = "error. you're not logged in")

    book1 = request.form['book1']
    book2 = request.form['book2']

    if not db_add_edge(book1, book2):
            return flask.render_template('custom.html', customText = "looks like one of these books doesn't exist", title = "oh no")
    return flask.render_template('custom.html', customText = "you've added an edge :D", title = "congrats")


@app.route('/account/signup/', methods = ['POST'])
def signup_page():
    username = request.form['username']

    encrypter = hashlib.sha256()
    encrypter.update(request.form['password'].encode())

    password = encrypter.hexdigest()
    if db_add_account(username, password):
        replace_login_status(True)
        return flask.render_template('custom.html', customText = "you've logged in successfully", title = "congrats") #successfully logged in
    return flask.render_template('custom.html', customText = "it looks like this username is already taken", title = "oh no")#username taken

@app.route('/account/login/', methods = ['POST'])
def login_page():
    username = request.form['username']

    encrypter = hashlib.sha256()
    encrypter.update(request.form['password'].encode())

    password = encrypter.hexdigest()
    if db_check_login(username, password):
        replace_login_status(True)
        return flask.render_template('index.html') #successfully logged in
    return redirect('/error/')#log in error

@app.route('/book/button/', methods = ['POST'])
def book_page_button():
    replace_add_edge(True)
    replace_book2(currentBook)
    return redirect('/search/')


@app.route('/book/add_edge/', methods = ['POST'])
def book_page_add_edge():
    """
    from book main
    """
    book_id = (next(iter(request.form.keys())))
    result = search_current_results(book_id)
    replace_current_book(result)

    book1 = currentBook
    book2 = globBook2

    if not db_add_edge_bookObj(book1, book2):
        return redirect('/error/')
    return redirect('/add/')

"""
FUNCTIONS WITHOUT ROUTES
"""
def replace_login_status(boolean):
    global loggedIn
    loggedIn = boolean

def replace_current_book(book):
    global currentBook
    currentBook = book

def replace_current_results(results):
    global currentResults
    currentResults = results

def replace_add_edge(boolean):
    global add_edge
    add_edge = boolean

def replace_book2(book):
    global globBook2
    globBook2 = book

def search_current_results(book_id):
    for r in currentResults:
        if r['_id'] == book_id:
            return r
    return False

def sort_by_second_element(e):
    return e[1]

def generate_relevance_table( book, depth = map_depth_cap,  size = map_size_cap, prev_books = [], prev_relevanceTable = None):
    #infinite loop begone
    if size == 0: return None

    #double counting begone
    if not prev_books:
        prev_books = [book['_id']]

    #double adding to the relevance table begone
    edges = book['edges']
    for e in edges:
        if e[0] in prev_books:
            edges.remove(e)
    if not edges: return None

    #length control
    if prev_relevanceTable: 
        length_control = prev_relevanceTable.connection_length*length_scalar
        relevanceTable = RelevanceTable(length_control)
    else:
        relevanceTable = RelevanceTable()

    #actually building the relevance table
    edges.sort(reverse=True,key=sort_by_second_element)

    for i in range(map_size_cap):
        if i >= len(edges):
            break
        e = edges[i]
        if e[0] not in prev_books:
            prev_books.append(e[0])

            book_e = next(iter(db_search(e[0]))) #e as a book (not an edge)

            relevanceTable.add(e)

            temp = generate_relevance_table(book_e, depth-1, size, prev_books, relevanceTable)
            if temp: relevanceTable.add(temp)

    return relevanceTable


"""
MAIN
"""
if __name__ == '__main__':
    app.run()
    replace_login_status(False)
