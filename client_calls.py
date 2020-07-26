from dsync import connect_to_server, send_message, receive_message, send_message_fn
import asyncio
from quote import Quote

connection = None

async def connect():
	global connection
	connection = await connect_to_server("localhost", 9000, "csprojecttest")

async def register(username, password, name, address):
	await send_message(connection, "Register")
	return (await send_message_fn(connection, username, name, address.city, address.state, address.zipcode, address.address1, address.address2, password))

async def login(username, password):
	await send_message(connection, "Login")
	return (await send_message_fn(connection, username, password))

async def logout():
	global connection
	await send_message(connection, "Logout")
	connection[1].close()
	await connection[1].wait_closed()
	connection = None

async def get_quote(gallons, date):
	result = await send_message_fn(connection, "Get Quote", gallons, date)
	try:
		return float(result)
	except ValueError:
		return result

async def submit_quote():
	result = await(send_message_fn(connection, "Submit Quote"))
	return result

async def get_quote_history():
	strquotes = (await send_message_fn(connection, "Get Quote History")).split("\u200c")
	quotes = [Quote.from_str(strquote) for strquote in strquotes]
	return quotes

async def update_profile(*, name=None, address=None, oldpassword=None, newpassword=None):
	to_send = []
	if(name is not None):
		to_send.append("name")
		to_send.append(name)
	if(address is not None):
		to_send.append("address")
		to_send.append(address)
	if(oldpassword is not None):
		to_send.append("oldpassword")
		to_send.append(oldpassword)
	if(newpassword is not None):
		to_send.append("newpassword")
		to_send.append(newpassword)
	return (await send_message_fn(connection, "Update Profile", *to_send))