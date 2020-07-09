import asyncio
import socket
from types import CoroutineType

async def connect_to_server(server_name, server_port):
    if(server_name == "localhost"):
        server_name = socket.gethostname()
    try:
        reader, writer = await asyncio.open_connection(server_name, server_port)
        return (reader, writer)
    except:
        print("Connection failed: couldn't find server")
        exit(1)

async def send_message(connection, *args):
    data = ""
    for arg in args:
        data+=str(arg).replace("\u200c", "") + "\u200c"
    data = str(data[:-1]) + "\n"
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
    await send_message(connection, str(result).encode())

def run_server(callback, port, serve_forever=True):
    async def server_callback(reader, writer):
        await callback((reader, writer))
    async def server_main():
        print("starting server")
        server = await asyncio.start_server(server_callback, socket.gethostname(), port)
        print("server started")
        if(serve_forever):
            async with server:
                await server.serve_forever()
    asyncio.run(server_main())

