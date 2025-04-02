import asyncio
import aiohttp
from aiohttp import web
import uuid
import pathlib

class OllamaServer:
    def __init__(self, ws, models):
        self.ws = ws
        self.queues = {}
        self.models = models

    @property
    def model_names(self):
        return [model['name'] for model in self.models]

    async def forward_to_http(self, request_id, message):
        if request_id not in self.queues:
            self.queues[request_id] = asyncio.Queue()
        await self.queues[request_id].put(message)

    async def forward_to_websocket(self, request_id, message, path):
        self.queues[request_id] = asyncio.Queue()
        await self.ws.send_json(dict(request_id=request_id, data=message, path=path))

        while True:
            chunk = await self.queues[request_id].get()
            yield chunk
            if chunk['done']:
                break

    async def serve(self):
        async for msg in self.ws:
            if msg.type == web.WSMsgType.TEXT:
                data = msg.json()
                request_id = data['request_id']
                await self.forward_to_http(request_id, data['data'])
            elif msg.type == web.WSMsgType.ERROR:
                break

class NoServerFoundException(BaseException):
    pass 

class ServerManager:
    def __init__(self):
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def remove_server(self, server):
        self.servers.remove(server)

    def get_server_by_model_name(self, model_name):
        for server in self.servers:
            if model_name in server.model_names:
                return server
        return None

    async def forward_to_websocket(self, request_id, message, path):
        try:
            server = self.servers.pop(0)
            self.servers.append(server)
            server = self.get_server_by_model_name(message['model'])
            if not server:
                raise NoServerFoundException
            async for msg in server.forward_to_websocket(request_id, message, path):
                yield msg
        except:
            raise

    def get_models(self):
        models = {}
        for server in self.servers:
            for model_name in server.model_names:
                if not model_name in models:
                    models[model_name] = 0
                models[model_name] += 1
        return models


server_manager = ServerManager()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    models = await ws.receive_json()

    server = OllamaServer(ws, models['models'])
    server_manager.add_server(server)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = msg.json()
            await server.forward_to_http(data['request_id'], data['data'])
        elif msg.type == web.WSMsgType.ERROR:
            print(f'WebSocket connection closed with exception: {ws.exception()}')

    server_manager.remove_server(server)
    return ws

async def http_handler(request):
    request_id = str(uuid.uuid4())
    data = None
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400)

    resp = web.StreamResponse(headers={'Content-Type': 'application/x-ndjson', 'Transfer-Encoding': 'chunked'})
    await resp.prepare(request)
    import json
    try:
        async for result in server_manager.forward_to_websocket(request_id, data, path=request.path):
            await resp.write(json.dumps(result).encode() + b'\n')
    except NoServerFoundException:
        await resp.write(json.dumps(dict(error="No server with that model found.",available=server_manager.get_models())).encode() + b'\n')
    await resp.write_eof()
    return resp

async def index_handler(request):
    index_template = pathlib.Path("index.html").read_text()
    client_py = pathlib.Path("client.py").read_text()
    index_template = index_template.replace("#client.py", client_py)
    return web.Response(text=index_template, content_type="text/html")

async def models_handler(self):
    return web.json_response(server_manager.get_models())

app = web.Application()

app.router.add_get("/", index_handler)
app.router.add_route('GET', '/publish', websocket_handler)
app.router.add_route('POST', '/api/chat', http_handler)
app.router.add_route('GET', '/models', models_handler)

if __name__ == '__main__':
    web.run_app(app, port=1984)
