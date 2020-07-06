import asyncio
import socket
def make_service_call(service_name, service_port):
    async def service_call(*args):
        data = ""
        for arg in args:
            data+=str(arg) + ","
        data = str(data[:-1]) + "\n"
        reader = None
        writer = None
        while reader is None and writer is None:
            try:
                reader, writer = await asyncio.open_connection(service_name, service_port)
            except:
                print("Connection failed: no servers for service", service_name, "available.")
                await asyncio.sleep(10)
                print("Retrying connection for", service_name)
        writer.write(data.encode())
        await writer.drain()
        response_data = await reader.readline()
        response = response_data.decode().strip()
        writer.close()
        await writer.wait_closed()
        return response
    return service_call

def run_service_server(service, port, serve_forever=True):
    async def handle_service(reader, writer):
        data = await reader.readline()
        message = data.decode().strip()
        args = message.split(",")
        response = str(service(*args)) + "\n"
        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    async def service_main():
        print("starting server")
        server = await asyncio.start_server(handle_service, socket.gethostname(), port)
        print("server started")
        if(serve_forever):
            async with server:
                await server.serve_forever()
    asyncio.run(service_main())

