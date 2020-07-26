from dsync import connect_to_server, send_message, receive_message, send_message_fn
import asyncio
from quote import Quote
from address import Address
from datetime import date as dtdate
from client_calls import connect, login, register, logout, update_profile

async def testfn():
	testaddress = Address("testcity", "TX", "testzip", "testaddr1")
	testaddress2 = Address("testcity", "teststate", "testzip", "testaddr1")
	testprofiledata = ("testusername", "testpassword", "testname", testaddress)
	await connect()
	response = await login(testprofiledata[0], testprofiledata[1])
	if(response != "Success"):
		print("Got error from server:")
		print(response)
	await logout()


def main():
	asyncio.run(testfn())

if __name__ == "__main__":
    main()