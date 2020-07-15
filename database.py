import sqlite3 as sql
import hashlib
from datetime import date as dtdate
from address import Address
from quote import Quote
from profile import Profile
from os import urandom
def initDB(db):
	dbconnection = sql.connect(db)
	c = dbconnection.cursor()
	c.execute('''CREATE TABLE Address(
					addressID INTEGER PRIMARY KEY AUTOINCREMENT,
					address1 CHARACTER VARYING(100),
					address2 CHARACTER VARYING(100),
					city CHARACTER VARYING(100),
					state CHARACTER (2),
					zipcode CHARACTER VARYING(9))''')
	c.execute('''CREATE TABLE Profile(
					username TEXT PRIMARY KEY,
					password VARBINARY(64),
					salt VARBINARY(64),
					name CHARACTER VARYING(50),
					address INTEGER,
					FOREIGN KEY (address) REFERENCES Address(addressID))''')
	c.execute('''CREATE TABLE Quote
				(quoteID INTEGER PRIMARY KEY AUTOINCREMENT,
				 gallons INTEGER,
				 date DATE,
				 address INTEGER,
				 price INTEGER,
				 username TEXT,
				 FOREIGN KEY (username) REFERENCES Profile(username) ON DELETE CASCADE,
				 FOREIGN KEY (address) REFERENCES Address(addressID))''')
	return dbconnection

def hash_password(password, salt):
	return hashlib.scrypt(password.encode(), salt=salt, n=1024, p=1, r=8)

def insertAddress(connection, address):
	c = connection.cursor()
	c.execute("INSERT INTO Address (city, state, zipcode, address1, address2) VALUES (?, ?, ?, ?, ?)", (address.city, address.state, address.zipcode, address.address1, address.address2))
	c.execute("SELECT MAX(addressID) FROM Address")
	address.setID(c.fetchone()[0])

def insertQuote(connection, quote, username):
	c = connection.cursor()
	if(quote.address.id is None):
		insertAddress(connection, quote.address)
	c.execute("INSERT INTO Quote (gallons, date, address, price, username) VALUES (?, ?, ?, ?, ?)", (quote.gallons, quote.date, quote.address.id, quote.price, username))
	c.execute("SELECT MAX(quoteID) FROM Quote")
	quote.setID(c.fetchone()[0])

def insertProfile(connection, profile, password):
	c = connection.cursor()
	if(profile.address.id is None):
		insertAddress(connection, profile.address)
	salt = urandom(64)
	passhash = hash_password(password, salt)
	c.execute('''
		INSERT INTO Profile (username, password, salt, name, address) VALUES (?, ?, ?, ?, ?)
		''', (profile.username, passhash, salt, profile.name, profile.address.id))
	for quote in profile.quotes:
		if(quote.id is None):
			insertQuote(connection, quote, profile.username)

def getAddress(connection, addressID):
	if(addressID in Address.address_by_id):
		return Address.address_by_id[addressID]
	c = connection.cursor()
	c.execute("SELECT city, state, zipcode, address1, address2 FROM Address WHERE addressID=?", (addressID,))
	results = c.fetchall()
	if(len(results) == 0):
		return None
	address = Address(*results[0])
	address.setID(addressID)
	return address

def getQuote(connection, quoteID):
	if(quoteID in Quote.quote_by_id):
		return Quote.quote_by_id[quoteID]
	c = connection.cursor()
	c.execute("SELECT gallons, date, address, price FROM Quote WHERE quoteID=?", (quoteID,))
	results = c.fetchall()
	if(len(results) != 1):
		return None
	gallons, strdate, addressID, price = results[0]
	date = dtdate.fromisoformat(strdate)
	address = getAddress(connection, addressID)
	quote = Quote(gallons, date, address, price)
	quote.setID(quoteID)
	return quote

def getProfile(connection, username):
	c = connection.cursor()
	c.execute("SELECT name, address FROM Profile WHERE username=?", (username,))
	results = c.fetchall()
	if(len(results)!=1):
		return None
	name, addressID = results[0]
	address = getAddress(connection, addressID)
	c.execute("SELECT quoteID FROM Quote WHERE username=?", (username,))
	quotes = []
	for (quoteID,) in c:
		quote = getQuote(connection, quoteID)
		if(quote is not None):
			quotes.append(quote)
	return Profile(username, name, address, quotes)

