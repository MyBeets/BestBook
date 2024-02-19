import os
import pymongo

client = pymongo.MongoClient(os.getenv("MONGO_CONNECTION"))

database = client['main']

accounts = database['accounts']

books = database['books']

authors = database['authors']

def db_add_book(title, author, genres, edges):
	#search for book

	#if found display error

	#else add book
	book_id = db_format(title + '_' + author)
	t_dict = { '_id': book_id, 
	'title': space_pres(title), 
	'author': space_pres(author),
	'genres': genres,
	'edges': edges}
	books.insert_one(t_dict)
	db_add_author(author, title)

def db_add_edge(book1, book2):
	book1_obj = books.find_one({ '_id': book1 })
	book2_obj = books.find_one({ '_id': book2 })
	if not book1_obj or not book2_obj:
		return False

	edges1 = book1_obj['edges']
	edges2 = book2_obj['edges']
	id1 = book1_obj['_id']
	id2 = book2_obj['_id']

	edge_check_and_update(edges1, id2)
	edge_check_and_update(edges2, id1)

	books.update_one({'_id' : id1},{'$set' : {'edges' : edges1}})
	books.update_one({'_id' : id2},{'$set' : {'edges' : edges2}})
	return True

def db_add_edge_bookObj(book1, book2):
	edges1 = book1['edges']
	edges2 = book2['edges']
	id1 = book1['_id']
	id2 = book2['_id']

	edge_check_and_update(edges1, id2)
	edge_check_and_update(edges2, id1)

	books.update_one({'_id' : id1},{'$set' : {'edges' : edges1}})
	books.update_one({'_id' : id2},{'$set' : {'edges' : edges2}})
	return True

def db_search(query):
	book1_dict = books.find({ '_id': { '$regex' : query} })
	if book1_dict:
		return book1_dict
	return 1

def db_add_account(username, password):
	userTaken = list(iter(accounts.find({'username' : str(username)})))
	if not userTaken:
		t_dict = { 'username': username, 
		'password': password}
		accounts.insert_one(t_dict)
		return True
	return False

def db_check_login(username, password):
	query = str(username)
	user = accounts.find_one({'username' : query})
	if user and user['password'] == password:
		return True
	return False

def db_add_author(name, book):
	name = db_format(name)
	author = db_authorsearch_one(name)
	if not author:
		books = [ book ]
		t_dict = { '_id': name, 'books': books}
		authors.insert_one(t_dict)
	else:
		books = author['books'] + [book]
		authors.update_one({'_id' : name} , {'$set' : {'books' : books}})


def db_authorsearch_one(query):
	author_dict = authors.find_one({ '_id' : query })
	if author_dict:
		print(author_dict)
		return author_dict
	return False

def db_authorsearch(query):
	authors_dict = authors.find({ '_id': { '$regex' : query} })
	if authors_dict:
		return authors_dict
	return False


# database related helper functions
# THESE DO NOT INTERACT DIRECTLY WITH THE DATABASE
def db_format(string):
	return string.lower().replace(' ', '')

def space_pres(string):
	return string.replace(' ','.')

def edge_check_and_update(edges, _id):
	exists = False
	for e in edges:
		if e[0] == _id:
			e[1] += 1
			exists = True
			break;
	if not exists:
		edges.append((_id, 1))
