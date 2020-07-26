from dsync import run_server, receive_message, send_message, receive_message_fn
from functools import partial
import sqlite3
import database
from profile import Profile
from quote import Quote
from address import Address
from os.path import isfile
from datetime import date as dtdate
import pricing

dbconnection = None
connected_users = set()

def get_user_for_login(username, password):
	c = dbconnection.cursor()
	if(username in connected_users):
		return "Error: User is already logged in"
	c.execute("SELECT password, salt FROM Profile WHERE username=?", (username,))
	results = c.fetchall()
	if(len(results)!=1):
		return "Error: Invalid Username or Password"
	correct_hash, salt = results[0]
	passhash = database.hash_password(password, salt)
	if(passhash == correct_hash):
		connected_users.add(username)
		return database.getProfile(dbconnection, username)
	else:
		return "Error: Invalid Username or Password"

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
			connected_users.add(profile.username)
			return profile
		return "Error: Username already taken"
	return "Error: Invalid arity"

def get_quote(current_user, *args):
	if(len(args) != 2):
		return "Error: Invalid arity"
	strgallons, strdate = args
	try:
		gallons = int(strgallons)
	except ValueError:
		return "Error: given number of gallons is not an integer"
	try:
		date = dtdate.fromisoformat(strdate)
	except ValueError:
		return "Error: given date is in an invalid or unknown format"
	newquote = Quote(gallons, date, current_user.address)
	current_user.quoteinprogress = newquote
	return pricing.calc_full_quote(current_user, newquote)

def get_quote_history(current_user, *args):
	if(len(args) != 0):
		return "Error: Invalid arity"
	return current_user.quotes

def submit_quote(current_user, *args):
	if(len(args) != 0):
		return "Error: Invalid arity"
	if(current_user.quoteinprogress is None):
		return "Error: No quote in progress"
	database.insertQuote(dbconnection, current_user.quoteinprogress, current_user.username)
	dbconnection.commit()
	current_user.quotes.append(current_user.quoteinprogress)
	current_user.quoteinprogress = None
	return "Success"

def update_profile(current_user, *args):
	oldname = current_user.name
	oldaddress = current_user.address
	oldpassword = None
	newpassword = None
	if(len(args)&1 == 1):
		return "Error: Expected even number of keys/vals"
	for i in range(0, len(args), 2):
		key,val = (args[i], args[i+1])
		if(key == "oldpassword"):
			oldpassword = val
		elif(key == "newpassword"):
			newpassword = val
		elif(key == "name"):
			current_user.name = val
		elif(key == "address"):
			current_user.address = Address.from_str(val)
		else:
			return "Error: Invalid Key"
	result = database.updateProfile(dbconnection, current_user, oldpassword, newpassword)
	if(result == "Success"):
		dbconnection.commit()
	else:
		current_user.name = oldname
		current_user.address = oldaddress
	return result

userhandlermap = {
	"Get Quote": get_quote,
	"Get Quote History": get_quote_history,
	"Submit Quote": submit_quote,
	"Update Profile": update_profile
}

#Dispatch function for the server
async def handle_user_requests(connection, current_user, *args):
	if(len(args) == 0):
		return "Error: Empty Request"
	if(args[0] == "Logout"):
		connected_users.remove(current_user.username)
		connection[1].close()
		return
	elif(args[0] in userhandlermap):
		return userhandlermap[args[0]](current_user, *(args[1:]))
	else:
		return "Error: Invalid Request"

async def handle_new_login(connection):
	try:
		current_user = None
		while(current_user is None and (not connection[1].is_closing())):
			message = await receive_message(connection)
			if(message == "Login"):
				result = (await receive_message(connection)).split("\u200c")
				if(len(result)!=2):
					await send_message(connection, "Error: Wrong Number Of Arguments")
				else:
					current_user = get_user_for_login(*result)
			elif(message == "Register"):
				args = (await receive_message(connection)).split("\u200c")
				current_user = make_new_user(*args)
			elif(message == "Logout"):
				connection[1].close()
				await connection[1].wait_closed()
				return
			else:
				await send_message(connection, "Error: Invalid Connection Option")
			if(isinstance(current_user, str)):
				await send_message(connection, current_user)
				current_user = None
		if(connection[1].is_closing()):
			await connection[1].wait_closed()
			return
		await send_message(connection, "Success")
		async def enclosed_handler(*args):
			result = await handle_user_requests(connection, current_user, *args)
			return result
		while(not connection[1].is_closing()):
			# print("Name:", current_user.name, "Address:", current_user.address)
			await receive_message_fn(connection, enclosed_handler)
		await connection[1].wait_closed()
	except ConnectionResetError:
		if(isinstance(current_user, Profile)):
			connected_users.remove(current_user.username)
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