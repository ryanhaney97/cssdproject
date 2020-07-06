import asyncio
import socket

async def connect_to_server(server_name, server_port):
    try:
        connection = await asyncio.open_connection(service_name, service_port)
        return connection
    except:
        print("Connection failed: couldn't find server")
        exit(1)

async def send_message(connection, *args):
    data = ""
    for arg in args:
        data+=str(arg) + ","
    data = str(data[:-1]) + "\n"
    reader, writer = connection
    writer.write(data.encode())
    await writer.drain()

async def receive_message(connection):
    reader, writer = connection
    data = await reader.readline()
    message = data.decode().strip()
    return message

async def send_message_fn(connection, *args):
    await send_message(connection, *args)
    response = await receive_message(connection)
    return response

async def receive_message_fn(connection, handler):
    message = await receive_message(connection)
    args = message.split(",")
    await send_message(connection, str(handler(*args)).encode())

def run_server(callback, port, serve_forever=True):
    async def server_callback(reader, writer):
        callback((reader, writer))
    async def server_main():
        print("starting server")
        server = await asyncio.start_server(server_callback, socket.gethostname(), port)
        print("server started")
        if(serve_forever):
            async with server:
                await server.serve_forever()
    asyncio.run(server_main())

