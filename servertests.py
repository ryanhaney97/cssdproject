import unittest
import server
import sqlite3
from datetime import date as dtdate
from quote import Quote
from profile import Profile
from address import Address
import asyncio
import dsync
import socket
import database
import ssl

class SequentialTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        testcase_methods = list(testCaseClass.__dict__.keys())
        test_names.sort(key=testcase_methods.index)
        return test_names

def makeFakeQuote(address=None):
	if(address is None):
		return Quote(500, dtdate.today(), Address("qcity", "qstate", "qzip", "qaddr1", "qaddr2"), 1000)
	else:
		return Quote(500, dtdate.today(), address, 1000)
def makeFakeProfile():
	return Profile("someusername", "somename", Address("somecity", "somestate", "somezip", "someaddr1", "someaddr2"))

def makeAndInsertFakeProfile(connection, password="somepassword"):
	profile = makeFakeProfile()
	database.insertProfile(connection, profile, password)
	return profile

class DBTests(unittest.TestCase):
	def setUp(self):
		Quote.quote_by_id = {}
		Address.address_by_id = {}
		server.dbconnection = database.initDB(":memory:")
		server.connected_users = set()
	def tearDown(self):
		server.dbconnection.close()
		server.dbconnection = None
	def test_dbaddress(self):
		address = makeFakeProfile().address
		database.insertAddress(server.dbconnection, address)
		self.assertIsNotNone(address.id)
		Address.address_by_id = {}
		result_address = database.getAddress(server.dbconnection, address.id)
		self.assertIsNotNone(result_address.id)
		self.assertEqual(address, result_address)
	def test_dbquote(self):
		quote = makeFakeQuote()
		database.insertQuote(server.dbconnection, quote, 0)
		Quote.quote_by_id = {}
		result_quote = database.getQuote(server.dbconnection, quote.id)
		self.assertEqual(quote, result_quote)
	def test_dbprofile(self):
		profile = makeFakeProfile()
		profile.quotes.append(makeFakeQuote())
		profile.quotes.append(makeFakeQuote(profile.address))
		database.insertProfile(server.dbconnection, profile, "password")
		result_profile = database.getProfile(server.dbconnection, profile.username)
		self.assertEqual(profile, result_profile)

class LoginTests(unittest.TestCase):
	def setUp(self):
		Quote.quote_by_id = {}
		Address.address_by_id = {}
		server.dbconnection = database.initDB(":memory:")
		server.connected_users = set()
	def tearDown(self):
		server.dbconnection.close()
		server.dbconnection = None
	def test_make_new_user_argtest(self):
		self.assertIsInstance(server.make_new_user(), str)
	def test_make_new_user_creationtest(self):
		#Make fake profile:
		testprofile = makeFakeProfile()
		#Call our test function with the test data:
		actualprofile = server.make_new_user(
			testprofile.username,
			testprofile.name,
			testprofile.address.city,
			testprofile.address.state,
			testprofile.address.zipcode,
			testprofile.address.address1,
			testprofile.address.address2,
			"somepassword")
		#Make sure the result is a Profile object, and equal to our test object made earlier:
		self.assertIsInstance(actualprofile, Profile)
		self.assertEqual(actualprofile, testprofile)
		#Ensure that a new entry has been created in the database:
		dbprofile = database.getProfile(server.dbconnection, testprofile.username)
		self.assertIsInstance(dbprofile, Profile)
		self.assertEqual(dbprofile, testprofile)
	def test_make_new_user_conflicttest(self):
		#Similar to above, but add the user to the database first and make sure that make_new_user returns None when there's a user conflict.
		testprofile = makeAndInsertFakeProfile(server.dbconnection)
		otherconflictingdata = ()
		self.assertIsInstance(server.make_new_user("someusername", "someothername", "someothercity", "someotherstate", "someotherzip", "someotheraddr1", "someotherpassword"), str)
		#Also make sure it didn't change or overwrite anything.
		profile = database.getProfile(server.dbconnection, testprofile.username)
		self.assertIsInstance(profile, Profile)
		self.assertEqual(profile, testprofile)
	def test_get_user_for_login_correct(self):
		#Test that the proper profile object is returned after a correct login.
		testpassword = "somepassword"
		testprofile = makeAndInsertFakeProfile(server.dbconnection, password=testpassword)
		actualprofile = server.get_user_for_login(testprofile.username, testpassword)
		self.assertIsInstance(actualprofile, Profile)
		self.assertEqual(actualprofile, testprofile)
	def test_get_user_for_login_incorrectpassword(self):
		#Make sure it returns none for an incorrect login password.
		testprofile = makeAndInsertFakeProfile(server.dbconnection, password="somepassword")
		self.assertIsInstance(server.get_user_for_login(testprofile.username, "wrongpassword"), str)
	def test_get_user_for_login_incorrectusername(self):
		#Make sure it returns none for an incorrect login username.
		testpassword = "somepassword"
		testprofile = makeAndInsertFakeProfile(server.dbconnection, password=testpassword)
		self.assertIsInstance(server.get_user_for_login("wrongusername", testpassword), str)
async def wait_server(server):
	async with server:
		await server.serve_forever()
class ConnectionTests(unittest.IsolatedAsyncioTestCase):
	async def server_callback(self, connection):
		self.server_connection = connection
	def setUp(self):
		Quote.quote_by_id = {}
		Address.address_by_id = {}
		server.dbconnection = database.initDB(":memory:")
		server.connected_users = set()
	async def asyncSetUp(self):
		self.server = await dsync.make_server(self.server_callback, 9001, "csprojecttest")
		asyncio.create_task(wait_server(self.server))
		self.connection = await dsync.connect_to_server("localhost", 9001, "csprojecttest")	
	def tearDown(self):
		server.dbconnection.close()
		server.dbconnection = None
	async def asyncTearDown(self):
		self.server.close()
		self.connection[1].close()
		await self.connection[1].wait_closed()
		self.server_connection[1].close()
		await self.server_connection[1].wait_closed()
		self.server_connection = None
		self.server = None
		self.connection = None
	async def test_dsync_messages(self):
		message = "abcdefg"
		asyncio.create_task(dsync.send_message(self.connection, message))
		recieved = await asyncio.wait_for(dsync.receive_message(self.server_connection), timeout=10)
		self.assertEqual(message, recieved)
		messages = ["123456", "abcdefg", "hijklmnop"]
		asyncio.create_task(dsync.send_message(self.connection, *messages))
		recieved_messages = (await asyncio.wait_for(dsync.receive_message(self.server_connection), timeout=10)).split("\u200c")
		self.assertEqual(messages, recieved_messages)
	async def test_server_disconnect(self):
		login_task = asyncio.create_task(server.handle_new_login(self.server_connection))
		await asyncio.wait_for(dsync.send_message_fn(self.connection, "Logout"), timeout=10)
		self.assertTrue(login_task.done())
	async def test_server_registration(self):
		login_task = asyncio.create_task(server.handle_new_login(self.server_connection))
		await asyncio.wait_for(dsync.send_message(self.connection, "Register"), timeout=10)
		testprofile = makeFakeProfile()
		testpassword = "somepassword"
		response = await asyncio.wait_for(dsync.send_message_fn(self.connection,
			testprofile.username,
			testprofile.name,
			testprofile.address.city,
			testprofile.address.state,
			testprofile.address.zipcode,
			testprofile.address.address1,
			testprofile.address.address2,
			testpassword), timeout=10)
		self.assertEqual(response, "Success")
		profile = database.getProfile(server.dbconnection, testprofile.username)
		self.assertIsNotNone(profile)
		self.assertEqual(profile, testprofile)
		await asyncio.wait_for(dsync.send_message_fn(self.connection, "Logout"), timeout=10)
		self.assertTrue(login_task.done())
	async def test_server_login(self):
		testpassword = "somepassword"
		testprofile = makeAndInsertFakeProfile(server.dbconnection, password=testpassword)
		login_task = asyncio.create_task(server.handle_new_login(self.server_connection))
		await asyncio.wait_for(dsync.send_message(self.connection, "Login"), timeout=10)
		response = await asyncio.wait_for(dsync.send_message_fn(self.connection, testprofile.username, testpassword), timeout=10)
		self.assertEqual(response, "Success")
		await asyncio.wait_for(dsync.send_message_fn(self.connection, "Logout"), timeout=10)
		self.assertTrue(login_task.done())

def main():
	unittest.main(testLoader=SequentialTestLoader())

if __name__ == '__main__':
	main()
