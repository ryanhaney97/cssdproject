import asyncio
import socket
from types import CoroutineType
import ssl
from traceback import print_stack

async def connect_to_server(server_name, server_port, certificate):
    if(server_name == "localhost"):
        server_name = socket.gethostname()
    sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_verify_locations(certificate + '.crt')
    reader, writer = await asyncio.open_connection(server_name, server_port, ssl=sslcontext)
    return (reader, writer)

def assemble_message(args):
    data = ""
    for arg in args:
        if(isinstance(arg, list) or isinstance(arg, tuple)):
            data+=assemble_message(arg)
        else:
            data+=str(arg).replace("\u200c", "") + "\u200c"
    return data

async def send_message(connection, *args):
    data = assemble_message(args)[:-1] + "\n"
    reader, writer = connection
    if(not writer.is_closing()):
        writer.write(data.encode())
        await writer.drain()

async def receive_message(connection):
    reader, writer = connection
    data = None
    while(data is None and not connection[1].is_closing()):
        try:
            data = await asyncio.wait_for(reader.readline(), timeout = 1)
        except asyncio.TimeoutError:
            pass
    if(data is not None):
        data = data.decode().strip()
        return data
    return data

async def send_message_fn(connection, *args):
    await send_message(connection, *args)
    response = await receive_message(connection)
    return response

async def receive_message_fn(connection, handler):
    message = await receive_message(connection)
    result = handler(*(message.split("\u200c")))
    if(isinstance(result, CoroutineType)):
        result = await result
    await send_message(connection, result)

async def make_server(callback, port, certificate):
    async def server_callback(reader, writer):
        await callback((reader, writer))
    sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_cert_chain(certificate + ".crt", certificate + ".key")
    server = await asyncio.start_server(server_callback, socket.gethostname(), port, ssl=sslcontext)
    return server

def run_server(callback, port, certificate):
    async def server_main():
        print("Starting Server...")
        server = await make_server(callback, port, certificate)
        print("Server Started")
        async with server:
            await server.serve_forever()
    asyncio.run(server_main())

