from dsync import run_server, receive_message, send_message
from functools import partial

#Dummy implementation
def get_user_for_login(username, password):
	pass

#Dummy implementation
def make_new_user(*args):
	pass

#Dispatch function for the server, Dummy implementation (add features off of here)
def handle_user_requests(connection, current_user, *args):
	pass

async def handle_new_login(connection):
	message = await receive_message(connection)
	current_user = None
	while(current_user is None):
		if(message == "Login"):
			username, password = await receive_message(connection).split(",")
			current_user = get_user_for_login(username, password)
			if(current_user is None):
				await send_message("Error,Wrong Username Or Password")
		elif(message == "Register"):
			args = await receive_message(connection)
			current_user = make_new_user(*args)
			if(current_user is None):
				await send_message("Error,Invalid Data")
		else:
			await send_message("Error,Invalid Connection Option")
	await send_message("Success")
	#Note: Change this so it stops when the connection is closed later when we have a logout function.
	while(True):
		await receive_message_fn(connection, partial(handle_user_requests, connection, current_user))

def main():
	run_server(server_handler, 9000)

if __name__ == "__main__":
    main()