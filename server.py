from dsync import run_server, receive_message, send_message, receive_message_fn
from functools import partial
import sqlite3
from profile import Profile
from quote import Quote

dbconnection = None

def get_user_for_login(username, password):
	c = dbconnection.cursor()
	c.execute("SELECT * FROM profile")
	print(username, password)
	c.execute("SELECT username, password, name, city, state, zipcode, address1, address2 FROM profile WHERE username=? AND password=?", (username, password))
	results = c.fetchall()
	print(results)
	if(len(results)==0):
		return None
	result = results[0]
	c.execute("SELECT gallons, date, price, total, address FROM quote WHERE user=?", (username,))
	quotes = []
	for quote in c:
		quotes.append(Quote(*quote))
	return Profile(*result, quotes=quotes)

def make_new_user(*args):
	if(len(args) == 7 or len(args) == 8):
		profile = Profile(*args)
		c = dbconnection.cursor()
		c.execute("SELECT username FROM profile WHERE username=?", (profile.username,))
		results = c.fetchall()
		if(len(results) == 0):
			c.execute("INSERT INTO profile (username, password, name, city, state, zipcode, address1, address2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
					 (profile.username, profile.password, profile.name, profile.city, profile.state, profile.zipcode, profile.address1, profile.address2))
			dbconnection.commit()
			return profile
	return None

#Dispatch function for the server, Dummy implementation (add features off of here)
async def handle_user_requests(connection, current_user, *args):
	if(args[0] == "Logout"):
		connection[1].close()
		return


#Warning: This login system is NOT secure (doesn't use SSL). For now this will do, but in a real app (or latter, if needed),
#should be replaced with a proper ssl, token-based auth.
async def handle_new_login(connection):
	try:
		current_user = None
		while(current_user is None and (not connection[1].is_closing())):
			message = await receive_message(connection)
			if(message == "Login"):
				username, password = (await receive_message(connection)).split("\u200c")
				current_user = get_user_for_login(username, password)
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
	dbconnection = sqlite3.connect("csproject.db")
	run_server(handle_new_login, 9000)

if __name__ == "__main__":
	main()