import sqlite3 as sql
import hashlib
from os import urandom
def initDB(db):
	dbconnection = sql.connect(db)
	c = dbconnection.cursor()
	c.execute('''CREATE TABLE Profile(
					username TEXT PRIMARY KEY,
					password VARBINARY(64),
					salt VARBINARY(64),
					name CHARACTER VARYING(50),
					address1 CHARACTER VARYING(100),
					address2 CHARACTER VARYING(100),
					city CHARACTER VARYING(100),
					state CHARACTER (2),
					zipcode CHARACTER VARYING(9))''')
	c.execute('''CREATE TABLE Quote
				(gallons INTEGER,
				 date DATETIME,
				 address TEXT,
				 price INTEGER,
				 total INTEGER,
				 username TEXT,
				 FOREIGN KEY (username) REFERENCES Profile(username) ON DELETE CASCADE)''')
	return dbconnection

def hash_password(password, salt):
	return hashlib.scrypt(password.encode(), salt=salt, n=1024, p=1, r=8)

def insertQuote(connection, quote, username):
	c = connection.cursor()
	c.execute("INSERT INTO Quote (gallons, date, price, total, address, username) VALUES (?, ?, ?, ?, ?, ?)", (quote.gallons, quote.date, quote.price, quote.total, quote.address, username))

def insertProfile(connection, profile, password):
	c = connection.cursor()
	salt = urandom(64)
	passhash = hash_password(password, salt)
	c.execute('''
		INSERT INTO Profile (username, password, salt, name, city, state, zipcode, address1, address2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		''', (profile.username, passhash, salt, profile.name, profile.city, profile.state, profile.zipcode, profile.address1, profile.address2))
	for quote in profile.quotes:
		insertQuote(connection, quote, profile.username)