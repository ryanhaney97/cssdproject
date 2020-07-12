from dsync import connect_to_server, send_message, receive_message, send_message_fn
import asyncio

async def main():
	testprofiledata = ("someusername", "somename", "somecity", "somestate", "somezip", "someaddr1", "somepassword")
	connection = await connect_to_server("localhost", 9000, "csprojecttest")
	await send_message(connection, "Login")
	response = await send_message_fn(connection, "someusername", "somepassword")
	# response = await send_message_fn(connection, *testprofiledata)
	print("response:", response)
	if(response == "Success"):
		print("Success! Yay!")
	print("Logout")
	result = await send_message_fn(connection, "Logout")
	print("Done!")

if __name__ == "__main__":
    asyncio.run(main())