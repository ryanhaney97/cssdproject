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
    response_data = await reader.readline()
    response = response_data.decode().strip()
    return response

async def receive_message(connection, handler):
    reader, writer = connection
    data = await reader.readline()
    message = data.decode().strip()
    args = message.split(",")
    response = str(service(*args)) + "\n"
    writer.write(response.encode())
    await writer.drain()

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

