from dsync import run_server, receive_message, send_message, receive_message_fn
from functools import partial
import sqlite3
import database
from profile import Profile
from quote import Quote
from address import Address
from os.path import isfile
from datetime import date as dtdate

dbconnection = None

def get_user_for_login(username, password):
	c = dbconnection.cursor()
	c.execute("SELECT password, salt FROM Profile WHERE username=?", (username,))
	results = c.fetchall()
	if(len(results)!=1):
		return None
	correct_hash, salt = results[0]
	passhash = database.hash_password(password, salt)
	if(passhash == correct_hash):
		return database.getProfile(dbconnection, username)
	else:
		return None

def make_new_user(*args):
	if(len(args) == 7 or len(args) == 8):
		password = args[-1]
		restargs = args[:-1]
		username, name = restargs[:2]
		address = Address(*restargs[2:])
		profile = Profile(username, name, address)
		c = dbconnection.cursor()
		c.execute("SELECT username FROM Profile WHERE username=?", (profile.username,))
		results = c.fetchall()
		if(len(results) == 0):
			database.insertProfile(dbconnection, profile, password)
			dbconnection.commit()
			return profile
	return None

def get_quote(current_user, *args):
	if(len(args) != 2):
		return "Error, invalid arity."
	gallons, strdate = args
	date = dtdate.fromisoformat(strdate)
	newquote = Quote(gallons, date, current_user.address)
	current_user.quoteinprogress = newquote

def get_quote_history(current_user, *args):
	pass

def submit_quote(current_user, *args):
	pass

userhandlermap = {
	"Get Quote": get_quote,
	"Get Quote History": get_quote_history,
	"Submit Quote": submit_quote,
}

#Dispatch function for the server
async def handle_user_requests(connection, current_user, *args):
	if(len(args) == 0):
		return "Error, Empty Request"
	if(args[0] == "Logout"):
		connection[1].close()
		return
	elif(args[0] in userhandlermap):
		return userhandlermap[args[0]](current_user, *(args[1:]))
	else:
		return "Error, Invalid Request"



async def handle_new_login(connection):
	try:
		current_user = None
		while(current_user is None and (not connection[1].is_closing())):
			message = await receive_message(connection)
			if(message == "Login"):
				result = (await receive_message(connection)).split("\u200c")
				if(len(result)!=2):
					await send_message(connection, "Error, Wrong Number Of Arguments")
				else:
					current_user = get_user_for_login(*result)
				if(current_user is None):
					await send_message(connection, "Error, Wrong Username Or Password")
			elif(message == "Register"):
				args = (await receive_message(connection)).split("\u200c")
				current_user = make_new_user(*args)
				if(current_user is None):
					await send_message(connection, "Error, Invalid Data")
			elif(message == "Logout"):
				connection[1].close()
				await connection[1].wait_closed()
				return
			else:
				await send_message(connection, "Error, Invalid Connection Option")
		if(connection[1].is_closing()):
			await connection[1].wait_closed()
			return
		await send_message(connection, "Success")
		async def enclosed_handler(*args):
			result = await handle_user_requests(connection, current_user, *args)
			return result
		while(not connection[1].is_closing()):
			await receive_message_fn(connection, enclosed_handler)
		await connection[1].wait_closed()
	except ConnectionResetError:
		print("Disconnected!")

def main():
	global dbconnection
	if(not isfile("csproject.db")):
		print("Initializing Database...")
		database.initDB("csproject.db")
	dbconnection = sqlite3.connect("csproject.db")
	run_server(handle_new_login, 9000, "csprojecttest")

if __name__ == "__main__":
	main()