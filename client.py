# This script requires aiohttp Python library to function.

import asyncio
import aiohttp
import json
import logging
import argparse
from urllib.parse import urlparse, urlunparse

# Default values
DEFAULT_CONCURRENCY = 4
DEFAULT_OLLAMA_URL = 'https://localhost:11434'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def websocket_client(url: str, ollama_url: str) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(f'{url}/publish') as ws:
                async with session.get(f'{ollama_url}/api/tags') as response:
                    if response.status != 200:
                        logging.error(f"Failed to fetch models: {response.status}")
                        return
                    models = await response.json()
                    await ws.send_json(models)

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        logging.info(f"Received data: {data}")
                        request_id = data['request_id']
                        api_url = urlunparse(urlparse(ollama_url)._replace(path=data['path']))

                        async with session.post(api_url, json=data['data']) as response:
                            if response.status != 200:
                                logging.error(f"Failed to post data: {response.status}")
                                continue
                            logging.info(f"Streaming response.")
                            async for msg in response.content:
                                msg = json.loads(msg.decode('utf-8'))
                                await ws.send_json(dict(
                                    request_id=request_id,
                                    data=msg
                                ))
                            logging.info(f"Response complete.")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logging.error("WebSocket error occurred.")
                        break
        except aiohttp.ClientError as e:
            logging.error(f"Client error occurred: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

async def main(concurrency: int, ollama_url: str) -> None:
    url = 'https://ollama.molodetz.nl'

    tasks = []
    for _ in range(concurrency):
        tasks.append(websocket_client(url, ollama_url))

    while True:
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Connection error: {e}")
            await asyncio.sleep(1)  # Wait before retrying

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WebSocket Client for Ollama API')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY,
                        help='Number of concurrent WebSocket connections (default: 4)')
    parser.add_argument('--ollama_url', type=str, default=DEFAULT_OLLAMA_URL,
                        help='Ollama API URL (default: http://localhost:11434)')

    args = parser.parse_args()

    if not validate_url(args.ollama_url):
        logging.error(f"Invalid Ollama URL: {args.ollama_url}")
        exit(1)

    asyncio.run(main(args.concurrency, args.ollama_url))
