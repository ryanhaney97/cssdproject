import unittest
import server
import sqlite3
from datetime import datetime
from quote import Quote
from profile import Profile
import asyncio
import dsync
import socket

def setupFakeDB():
	connection = sqlite3.connect(":memory:")
	c = connection.cursor()
	c.execute('''
		CREATE TABLE quote
		(quoteID INTEGER PRIMARY KEY AUTOINCREMENT,
		 gallons real,
		 date date,
		 price real,
		 total real,
		 address text,
		 user text,
		 FOREIGN KEY (user) REFERENCES profile(username))''')
	c.execute('''
		CREATE TABLE profile
		(username text PRIMARY KEY,
		 password text,
		 name text,
		 city text,
		 state text,
		 zipcode text,
		 address1 text,
		 address2 text)
		''')
	return connection

def insertQuote(connection, quote, user=None):
	c = connection.cursor()
	c.execute('''
		INSERT INTO quote (gallons, date, price, total, address, user) VALUES (?, ?, ?, ?, ?, ?)
		''', (quote.gallons, quote.date, quote.price, quote.total, quote.address, user))

def insertProfile(connection, profile):
	c = connection.cursor()
	c.execute('''
		INSERT INTO profile (username, password, name, city, state, zipcode, address1, address2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		''', (profile.username, profile.password, profile.name, profile.city, profile.state, profile.zipcode, profile.address1, profile.address2))
	for quote in profile.quotes:
		insertQuote(connection, quote, profile.username)

class LoginTests(unittest.TestCase):
	def setUp(self):
		server.dbconnection = setupFakeDB()
	def tearDown(self):
		server.dbconnection.close()
		server.dbconnection = None
	def test_make_new_user_argtest(self):
		self.assertIsNone(server.make_new_user())
	def test_make_new_user_creationtest_addr1(self):
		#Fake profile data used:
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		#Make a Profile object from the above to aid in testing:
		testprofileobj = Profile(*testprofiledata)
		#Call our test function with the test data:
		actualprofile = server.make_new_user(*testprofiledata)
		#Make sure the result is a Profile object, and equal to our test object made earlier:
		self.assertIsInstance(actualprofile, Profile)
		self.assertEqual(actualprofile, testprofileobj)
		#Ensure that a new entry has been created in the database:
		c = server.dbconnection.cursor()
		c.execute("SELECT username, password, name, city, state, zipcode, address1 FROM profile WHERE username=?", (testprofileobj.username,))
		profiles = c.fetchall()
		self.assertEqual(len(profiles), 1)
		self.assertEqual(profiles[0], testprofiledata)
	def test_make_new_user_creationtest_addr2(self):
		#Same test as above, but with a second address argument to make sure it can handle both cases.
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1", "someaddr2")
		testprofileobj = Profile(*testprofiledata)
		actualprofile = server.make_new_user(*testprofiledata)
		self.assertIsInstance(actualprofile, Profile)
		self.assertEqual(actualprofile, testprofileobj)
		c = server.dbconnection.cursor()
		c.execute("SELECT username, password, name, city, state, zipcode, address1, address2 FROM profile WHERE username=?", (testprofileobj.username,))
		profiles = c.fetchall()
		self.assertEqual(len(profiles), 1)
		self.assertEqual(profiles[0], testprofiledata)
	def test_make_new_user_conflicttest(self):
		#Similar to above, but add the user to the database first and make sure that make_new_user returns None when there's a user conflict.
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		testprofileobj = Profile(*testprofiledata)
		insertProfile(server.dbconnection, testprofileobj)
		otherconflictingdata = ("someusername", "someotherpassword", "someothername", "someothercity", "someotherstate", "someotherzip", "someotheraddr1")
		self.assertIsNone(server.make_new_user(otherconflictingdata))
		c = server.dbconnection.cursor()
		#Also make sure it didn't change or overwrite anything.
		c.execute("SELECT username, password, name, city, state, zipcode, address1 FROM profile WHERE username=?", (testprofileobj.username,))
		profiles = c.fetchall()
		self.assertEqual(len(profiles), 1)
		self.assertEqual(profiles[0], testprofiledata)
	def test_get_user_for_login_correct(self):
		#Test that the proper profile object is returned after a correct login.
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		testprofileobj = Profile(*testprofiledata)
		insertProfile(server.dbconnection, testprofileobj)
		actualprofile = server.get_user_for_login(testprofileobj.username, testprofileobj.password)
		self.assertIsInstance(actualprofile, Profile)
		self.assertEqual(actualprofile, testprofileobj)
	def test_get_user_for_login_incorrectpassword(self):
		#Make sure it returns none for an incorrect login password.
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		testprofileobj = Profile(*testprofiledata)
		insertProfile(server.dbconnection, testprofileobj)
		self.assertIsNone(server.get_user_for_login(testprofileobj.username, "wrongpassword"))
	def test_get_user_for_login_incorrectusername(self):
		#Make sure it returns none for an incorrect login username.
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		testprofileobj = Profile(*testprofiledata)
		insertProfile(server.dbconnection, testprofileobj)
		self.assertIsNone(server.get_user_for_login("wrongusername", testprofileobj.password))



def dfetchone(cursor):
	columns = [col[0] for col in cursor.description]
	return dict(zip(columns, cursor.fetchone()))

def dfetchall(cursor):
	columns = [col[0] for col in cursor.description]
	return [dict(zip(columns, row)) for row in cursor.fetchall()]


async def setupFakeServer(self):
	async def server_callback(reader, writer):
		self.server_connection = (reader, writer)
	self.server = await asyncio.start_server(server_callback, socket.gethostname(), 9001)

async def runServForever(self):
	async with self.server:
		await self.server.serve_forever()

class ConnectionTests(unittest.TestCase):
	def setUp(self):
		self.server = None
		self.server_connection = None
		server.dbconnection = setupFakeDB()
		loop = asyncio.get_event_loop()
		loop.run_until_complete(setupFakeServer(self))
		loop.create_task(runServForever(self))
		self.connection = loop.run_until_complete(dsync.connect_to_server("localhost", 9001))
	def tearDown(self):
		self.server.close()
		self.server_connection = None
		self.server = None
		self.connection = None
		server.dbconnection.close()
		server.dbconnection = None
		loop = asyncio.get_event_loop()
		if(loop.is_running()):
			loop.stop()
	def test_dsync_messages(self):
		loop = asyncio.get_event_loop()
		message = "abcdefg"
		loop.create_task(dsync.send_message(self.connection, message))
		recieved = loop.run_until_complete(dsync.receive_message(self.server_connection))
		self.assertEqual(message, recieved)
		messages = ["123456", "abcdefg", "hijklmnop"]
		loop.create_task(dsync.send_message(self.connection, *messages))
		recieved_messages = loop.run_until_complete(dsync.receive_message(self.server_connection)).split("\u200c")
		self.assertEqual(messages, recieved_messages)
	def test_server_registration(self):
		loop = asyncio.get_event_loop()
		login_task = loop.create_task(server.handle_new_login(self.server_connection))
		loop.run_until_complete(dsync.send_message(self.connection, "Register"))
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		response = loop.run_until_complete(dsync.send_message_fn(self.connection, *testprofiledata))
		self.assertEqual(response, "Success")
		c = server.dbconnection.cursor()
		c.execute("SELECT username, password, name, city, state, zipcode, address1 FROM profile WHERE username=?", (testprofiledata[0],))
		profiles = c.fetchall()
		self.assertEqual(len(profiles), 1)
		self.assertEqual(profiles[0], testprofiledata)
		loop.run_until_complete(dsync.send_message_fn(self.connection, "Logout"))
		self.assertTrue(login_task.done())
	def test_server_login(self):
		testprofiledata = ("someusername", "somepassword", "somename", "somecity", "somestate", "somezip", "someaddr1")
		c = server.dbconnection.cursor()
		c.execute("INSERT INTO profile (username, password, name, city, state, zipcode, address1) VALUES (?, ?, ?, ?, ?, ?, ?)", testprofiledata)
		loop = asyncio.get_event_loop()
		login_task = loop.create_task(server.handle_new_login(self.server_connection))
		loop.run_until_complete(dsync.send_message(self.connection, "Login"))
		response = loop.run_until_complete(dsync.send_message_fn(self.connection, testprofiledata[0], testprofiledata[1]))
		self.assertEqual(response, "Success")
		loop.run_until_complete(dsync.send_message_fn(self.connection, "Logout"))
		self.assertTrue(login_task.done())
	def test_server_disconnect(self):
		loop = asyncio.get_event_loop()
		login_task = loop.create_task(server.handle_new_login(self.server_connection))
		loop.run_until_complete(dsync.send_message_fn(self.connection, "Logout"))
		self.assertTrue(login_task.done())


if __name__ == '__main__':
	unittest.main()
	loop = asyncio.get_event_loop()
	loop.run_until_complete(loop.shutdown_asyncgens())
	loop.close()
